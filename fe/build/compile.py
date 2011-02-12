import sys

reload(sys)
sys.setdefaultencoding('utf-8')
del sys.setdefaultencoding
print "default encoding: utf-8"

import os
from jinja2 import Environment, FileSystemLoader

pathjoin = os.path.join

dstroot = "pub"
srcdir = "fe/src"
contribdir = "fe/contrib"
themes_srcdir = "fe/src/themes"
themes = (('default', 'Green'), ('bw', 'Black and White'))
langs = (('en', 'English'), ('es', 'Spanish'))
available_langs = [lang[1] for lang in langs]
available_themes = [theme[1] for theme in themes]
contribs = ['css', 'js']

env = Environment(loader=FileSystemLoader(srcdir))

def copy_dirs(dirs, srcdir, dstdir):
    if not os.path.exists(dstdir):
        os.mkdir(dstroot)
    for dirname in dirs:
        cmd = "cp -rv %s/%s %s" % (srcdir, dirname, dstdir)
        os.system(cmd)

def is_template(filename, srcpath):
    return filename.endswith('.htm') and 'extends' in file(srcpath).read()

def compile_template(filename, srcpath, dstdir):
    print "compiling", srcpath
    reldir = os.path.dirname(srcpath).replace(srcdir, '')
    if reldir.startswith(os.sep):
        reldir = reldir[1:]
    rel_level_to_pubroot = len([x for x in reldir.split(os.path.sep) if x])
    relpath = os.path.join(reldir, filename)
    relpath_to_pubroot = os.path.join(*['..' for i in range(rel_level_to_pubroot)]) if rel_level_to_pubroot else '.'
    relpath = os.path.join(reldir, filename)
    template = env.get_template(relpath)
    out = template.render(pubroot=relpath_to_pubroot, available_langs=available_langs, available_themes=available_themes)
    dstdir = os.path.join(dstdir, reldir)
    if not os.path.exists(dstdir):
        os.makedirs(dstdir)
    outpath = os.path.join(dstdir, filename.replace('.htm', ''))
    print "writing ", outpath
    file(outpath, 'w').write(out)

def make_theme(srcdir, theme_dir, dstdir):
    cssdir = pathjoin(dstdir, 'css')
    print "compiling", theme_dir
    srcpath = os.path.join(srcdir, 'themes', theme_dir, 'cssdefs.py')
    data = {}
    execfile(srcpath, {}, data)
    template = env.get_template('css/cowspa.css')
    out = template.render(**data)
    if not os.path.exists(cssdir):
        os.makedirs(cssdir)
    outpath = os.path.join(cssdir, 'main.css')
    print "writing ", outpath
    file(outpath, 'w').write(out)

def is_themedef(filename, srcpath):
    return filename == "cssdefs.py"

def src_walk(srcdir, dstdir, **data):
    for root, dirs, filenames in os.walk(srcdir):
        for filename in filenames:
            srcpath = os.path.join(root, filename)
            if filename.startswith('.'): continue # .swp etc.
            if is_template(filename, srcpath):
                compile_template(filename, srcpath, dstdir)

# pub/en/sunsine/

for lang_code, lang_label in langs:
    for theme_dir, theme_label in themes:
        print lang_code, theme_dir
        print "============\n"
        dstdir = os.path.join(dstroot, lang_code, theme_dir)
        src_walk(srcdir, dstdir, lang_code=lang_code, theme_dir=theme_dir)
        make_theme(srcdir, theme_dir, dstdir)
        copy_dirs(contribs, contribdir, dstdir)
        copy_dirs(('js', 'images'), srcdir, dstdir)
