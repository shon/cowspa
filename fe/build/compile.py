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
        if (not filename.endswith('.htm') and not 'extends' in file(os.path.join(root, filename)).read()): continue
        print "compiling", os.path.join(root, filename)
        reldir = root.replace(srcdir, '')
        if reldir.startswith(os.sep):
            reldir = reldir[1:]
        rel_level_to_pubroot = len([x for x in reldir.split(os.path.sep) if x])
        relpath = os.path.join(reldir, filename)
        relpath_to_pubroot = os.path.join(*['..' for i in range(rel_level_to_pubroot)]) if rel_level_to_pubroot else '.'
        relpath = os.path.join(reldir, filename)
        template = env.get_template(relpath)
        out = template.render(pubroot=relpath_to_pubroot)
        dstdir = os.path.join(outdir, reldir)
        if not os.path.exists(dstdir):
            os.makedirs(dstdir)
        outpath = os.path.join(dstdir, filename.replace('.htm', ''))
        print "writing ", outpath
        file(outpath, 'w').write(out)
