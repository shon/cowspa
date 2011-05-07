import os
import sys
import time

path = os.path.abspath(os.getcwd())
sys.path.append(path)

import fe.repository.stores as stores

import be
import be.bootstrap
import be.apps

cowapp = be.apps.cowapp

import testdata
from flask import Flask, jsonify, url_for, session, redirect, request
app = Flask(__name__)#, static_path=os.path.abspath("../pub"))
app.secret_key = os.urandom(24)

@app.route('/api/<path:apireq>', methods=['GET', 'POST', 'DELETE'])
def api_dispatch(apireq):
    # if you have nothing in request.json mostly 'Content-type' request header are not set to 'application/json'
    data = {}
    if hasattr(request, 'json') and request.json:
        data = request.json
    # app.root.process_slashed_path('0.1/members/1')()
    #cowapp.set_context( session['authcookie'] )
    cowapp.root.set_context( request.cookies.get('authcookie', ''))
    res = be.apps.cowapp_http.root(apireq, request.method, data)
    resp = jsonify(res)
    resp.mimetype='text/plain'
    return resp

@app.route('/app/<path:path>', methods=['GET', 'POST', 'DELETE'])
def default(path):
    data = getattr(testdata, path, {'error':'no donuts for you'})
    return jsonify(data=data)

start_pages = dict (
    new = '%(language)s/%(role)s/%(theme)s/next',
    member = '%(language)s/%(role)s/%(theme)s/profile',
    host = '%(language)s/%(role)s/%(theme)s/dashboard',
    director = '%(language)s/%(role)s/%(theme)s/dashboard',
    board = '%(language)s/%(role)s/%(theme)s/dashboard',
    admin = '%(language)s/%(role)s/%(theme)s/dashboard')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # if you have nothing in request.json mostly 'Content-type' request header are not set to 'application/json'
        username = request.json.get('username')
        password = request.json.get('password')
        remember = bool(request.json.get('remember'))
        res = cowapp.root['0.1'].login(username, password) #TODO remove version hard coding
        retcode, auth_token = res['retcode'], res['result']
        if retcode == 0 and auth_token:
            session_data = {}
            session_data.update(cowapp.root['0.1'].users[username].info()['result'])
            session_data.update(cowapp.root['0.1'].members[session_data['id']].get(attr='pref')['result'])
            result = start_pages[session_data['role']] % session_data
            #session['authcookie'] = auth_token
            #session.permanent = remember
            print 'login success'
        else:
            result = None
            print 'login failed'
        resp = jsonify({'retcode': retcode, 'result': result})
        resp.set_cookie('authcookie',value=auth_token)
    elif request.method == 'GET':
        resp = static('login')
    return resp

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    resp = redirect('/login')
    resp.delete_cookie('authcookie')
    return resp

@app.route('/search', methods=['POST'])
def search():
    query = '*%s*' % request.form['query']
    import be.libs.search as searchlib
    items = searchlib.do_search(query)
    html_list = ''.join([('<li class="search-res" id="search-opt-%s">%s</li>' % (item['id'], item['display_name'])) for item in items])
    print html_list
    return html_list, 200, {'Content-Type': 'text/html; charset=utf-8'}

@app.route('/<path:path>')
def static(path):
    if path.startswith('en/Assets'): # mooEditable smileys
        path = path[3:]
    static_root = "pub/"
    fspath = os.path.join(static_root, path)
    filename = os.path.basename(path)
    if '.' in path:
        content_type = "text/" + path.split('.')[-1]
    else:
        content_type = "text/html"
    return file(fspath).read(), 200, {'Content-Type': content_type +'; charset=utf-8'}

if __name__ == '__main__':
    app.run('0.0.0.0',debug=True)
    from gevent.wsgi import WSGIServer

    http_server = WSGIServer(('', 5000), app)
    http_server.serve_forever()
