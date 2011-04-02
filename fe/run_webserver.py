import os
import sys
import time

path = os.path.abspath(os.getcwd())
sys.path.append(path)

import be
import be.apps
import be.bases

cowapp = be.apps.cowapp

import testdata
from flask import Flask, jsonify, url_for, session, redirect, request
app = Flask(__name__)#, static_path=os.path.abspath("../pub"))
app.secret_key = os.urandom(24)

redirect_to_index = redirect('/dashboard')

@app.route('/api/<path:apireq>', methods=['GET', 'POST'])
def api_dispatch(apireq):
    root = be.apps.cowapp
    # if you have nothing in request.json mostly 'Content-type' request header are not set to 'application/json'
    data = dict(request.json.items())
    # app.root.process_slashed_path('0.1/members/1')()
    res = cowapp.root.process_slashed_path(apireq)(**data)
    resp = jsonify(res)
    resp.mimetype='text/plain'
    return resp

@app.route('/app/<path:path>')
def default(path):
    data = getattr(testdata, path, {'error':'no donuts for you'})
    return jsonify(data=data)

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
            info = cowapp.root['0.1'].users[username].info()['result']
            result = '/en/%(role)s/default/dashboard' % info
            session['authcookie'] = auth_token
            session.permanent = remember
            print 'login success'
        else:
            result = None
            print 'login failed'
        resp = jsonify({'retcode': retcode, 'result': result})
    elif request.method == 'GET':
        resp = static('login')
    return resp

@app.route('/<path:path>')
def static(path):
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
