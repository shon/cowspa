import os
import time
import testdata
from flask import Flask, jsonify, url_for
app = Flask(__name__)#, static_path=os.path.abspath("../pub"))
static_dir = "pub/en/default"
static_dir = "pub/en/bw"

@app.route('/app/<path:path>')
def default(path):
    time.sleep(2);
    data = getattr(testdata, path, {'error':'no donuts for you'})
    print data
    return jsonify(data=data)

@app.route('/<path:path>')
def static(path):
    print 'req for ', path
    fspath = os.path.join(static_dir, path)
    filename = os.path.basename(path)
    if '.' in path:
        content_type = "text/" + path.split('.')[-1]
    else:
        content_type = "text/html"
    return file(fspath).read(), 200, {'Content-Type': content_type +'; charset=utf-8'}

if __name__ == '__main__':
    app.run('0.0.0.0',debug=True)

