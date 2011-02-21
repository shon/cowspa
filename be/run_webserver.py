import os
import sys
import time

path = os.path.abspath(os.getcwd())
sys.path.append(path)

import be
import be.apps

cowapp = be.apps.cowapp

import testdata
from flask import Flask, jsonify, url_for, session, redirect, request
app = Flask(__name__)#, static_path=os.path.abspath("../pub"))

redirect_to_index = redirect('/dashboard')

@app.route('/app/<path:path>')
def default(path):
    time.sleep(2);
    data = getattr(testdata, path, {'error':'no donuts for you'})
    print data
    return jsonify(data=data)

@app.route('/set_theme/<theme_name>')
def set_theme(theme_name):
    response = app.make_response(redirect_to_index )
    response.set_cookie('theme',value=theme_name)
    return response

@app.route('/auth', methods=['POST'])
def auth():
    username = request.form['username']
    password = request.form['password']
    if cowapp.users.authenticate(username, password):
        where = redirect_to_index
        response = app.make_response(where)
        response.set_cookie('authenticated', '1')
        response.set_cookie('msg',value='')
    else:
        where = redirect('/login')
        response = app.make_response(where)
        msg = "Authentication failed. Try again."
        response.set_cookie('msg',value=msg)
    return response

@app.route('/<path:path>')
def static(path):
    static_root = "pub/en/"
    static_dir = static_root + request.cookies.get("theme", "default")
    fspath = os.path.join(static_dir, path)
    filename = os.path.basename(path)
    if '.' in path:
        content_type = "text/" + path.split('.')[-1]
    else:
        content_type = "text/html"
    return file(fspath).read(), 200, {'Content-Type': content_type +'; charset=utf-8'}

if __name__ == '__main__':
    app.run('0.0.0.0',debug=True)

