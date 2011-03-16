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

@app.route('/api/<path:apireq>')
def api_dispatch(apireq):
    root = be.apps.cowapp
    res = be.bases.navigate_slashed_path(root, apireq, **request.form)
    resp = jsonify(res)
    resp.mimetype='text/plain'
    return resp

@app.route('/app/<path:path>')
def default(path):
    time.sleep(2);
    data = getattr(testdata, path, {'error':'no donuts for you'})
    return jsonify(data=data)

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    retcode, auth_token = cowapp['0.1'].login(username, password)
    if retcode == 0:
        where = redirect('/en/member/default/dashboard')
        response = app.make_response(where)
        session['authcookie'] = auth_token
        #response.set_cookie('authenticated', '1')
        #response.set_cookie('msg',value='')
    else:
        where = redirect('/login')
        response = app.make_response(where)
        msg = "Authentication failed. Try again."
        response.set_cookie('msg',value=msg)
    return response

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
