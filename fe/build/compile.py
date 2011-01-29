import os
from jinja2 import Environment, FileSystemLoader

outdir = "pub"
srcdir = "fe/src"

if not os.path.exists(outdir):
    os.mkdir(outdir)
    for dirname in ('js', 'css', 'images'):
        cmd = "cp -rv fe/src/%s %s" % (dirname, outdir)
        os.system(cmd)

env = Environment(loader=FileSystemLoader('fe/src'))
for root, dirs, filenames in os.walk(srcdir):
    for filename in filenames:
        if not filename.endswith('.htm'): continue
        print "compiling", os.path.join(root, filename)
        reldir = root.replace(srcdir, '')
        if reldir.startswith('/'):
            reldir = reldir[1:]
        relpath = os.path.join(reldir, filename)
        template = env.get_template(relpath)
        out = template.render()
        dstdir = os.path.join(outdir, reldir)
        if not os.path.exists(dstdir):
            os.makedirs(dstdir)
        outpath = os.path.join(dstdir, filename)#.replace('.htm', ''))
        print "writing ", outpath
        file(outpath, 'w').write(out)
