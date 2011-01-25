import os
from jinja2 import Environment, FileSystemLoader

outdir = "out"
if not os.path.exists(outdir):
    os.mkdir(outdir)
    cmd = "cp -rv fe/src/js " + outdir
    os.system(cmd)
    cmd = "cp -rv fe/src/css " + outdir
    os.system(cmd)

name = "dashboard.html"
env = Environment(loader=FileSystemLoader('fe/src'))
print "compiling ", name
template = env.get_template(name)
out = template.render()
file(os.path.join(outdir, name), 'w').write(out)
