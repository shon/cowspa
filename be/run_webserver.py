import os
import time
import testdata
from flask import Flask, jsonify, url_for, session, redirect, request
app = Flask(__name__)#, static_path=os.path.abspath("../pub"))

@app.route('/app/<path:path>')
def default(path):
    time.sleep(2);
    data = getattr(testdata, path, {'error':'no donuts for you'})
    print data
    return jsonify(data=data)

@app.route('/set_theme/<theme_name>')
def set_theme(theme_name):
    redirect_to_index = redirect('/dashboard')
    response = app.make_response(redirect_to_index )
    response.set_cookie('theme',value=theme_name)
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

