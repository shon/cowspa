import sys

reload(sys)
sys.setdefaultencoding('utf-8')
del sys.setdefaultencoding
print "default encoding: utf-8"

import os
import itertools
import copy
import jinja2
import shpaml
import cssprefixer


DEBUG = bool(sys.argv[0:1])
pathjoin = os.path.join

api_version = '0.1'
srcroot = "fe/src"
dstroot = "pub"
themes_srcroot = "fe/src/themes"
themes_dstroot = "pub/themes"
themes = (('default', 'Green'), ('bw', 'Black and White'), ('fb', 'Facebook'))
theme_labels = [theme[1] for theme in themes]
theme_codes = [theme[0] for theme in themes]
langs = (('en', 'English'), ('es', 'Spanish'), ('de', 'German'))
lang_labels = [lang[1] for lang in langs]
lang_codes = [lang[0] for lang in langs]
roles = ('new', 'member', 'host', 'director', 'board', 'admin')
role_codes = roles
contrib_root = "fe/contrib"
contribs = ['css', 'js', 'Assets']
static_root = srcroot
statics = ('js', 'images', 'favicon.ico')
theme_root = pathjoin(srcroot, "themes")

template_env = jinja2.Environment(loader=jinja2.FileSystemLoader(srcroot))

def compute_possible_pathdata(data):
    data_prefixed = {}
    for k, v in data.items():
        v_new = [(k + ':' + x)  for x in v]
        data_prefixed[k] = v_new
    path_data_prefixed = itertools.product(*data_prefixed.values())
    return list(dict(y.split(':', 1) for y in x) for x in path_data_prefixed)


class Template(object):
    def __init__(self, src, dsts):
        self.src = src
        # self.source = file(src).read()
        self.dsts = dsts if not isinstance(dsts, basestring) else [dsts]
    def add_env(self, context):
        context.update( dict(available_langs=langs, available_themes=themes, api_version=api_version) )
    def render(self, context):
        #out = jinja2.Template(self.source).render(**context)
        template = template_env.get_template(self.src)
        self.add_env(context)
        out = template.render(**context)
        return out
    def copy(self, content, path):
        dstdir = pathjoin(dstroot, os.path.dirname(path))
        dstpath = pathjoin(dstroot, path)
        if not os.path.exists(dstdir):
            os.makedirs(dstdir)
        print "writing " ,dstpath
        file(dstpath, 'w').write(content)
    def process_dst_data(self):
        paths_data = []
        paths = []
        for path_dict in path_combinations:
            for dst in self.dsts:
                path = jinja2.Template(dst).render(path_dict)
                if path not in paths: # check to avoid duplicates
                    paths_data.append((path, path_dict))
                    paths.append(path)

        return paths_data

    def build(self, data={}, dst_data={}):
        final_dst_data = self.process_dst_data()
        for path, dst_data in final_dst_data:
            dstpath = pathjoin(dstroot, path)
            if os.path.exists(dstpath):
                if os.path.getmtime(dstpath) > os.path.getmtime(pathjoin(srcroot, self.src)):
                    #print "skipping ", path
                    continue
            context = copy.deepcopy(data)
            context.update(dst_data)
            context['pubroot'] = os.path.sep.join('..' for x in os.path.dirname(path).split('/') )
            context['curdir'] = os.path.dirname(path)
            out = self.render(context)
            self.copy(out, path)

class SHPAMLTemplate(Template):
    def render(self, context):
        source = file(pathjoin(srcroot, self.src)).read()
        out = shpaml.convert_text(source)
        self.add_env(context)
        return template_env.from_string(out).render(**context)

class CSSTemplate(Template):
    def render(self, context):
        theme_dir = pathjoin(theme_root, context['theme'])
        print "compiling", theme_dir
        cssdefs_path = os.path.join(theme_dir, 'theme.py')
        theme_data = {}
        execfile(cssdefs_path, {}, theme_data)
        print theme_data
        context.update(theme_data)
        out = super(CSSTemplate, self).render(context)
        out = cssprefixer.process(out, debug=False, minify=(not DEBUG))
        return out

def copydirs(srcs, dst, verbose=False):
    if isinstance(srcs, basestring):
        srcs = [srcs]
    else:
        srcs = list(srcs)
    if not srcs:
        raise Exception("No source specified")
    print "%s -> %s" % (srcs, dst)
    v = verbose and 'v' or ''
    dstdir = os.path.dirname(dst)
    if dstdir and not os.path.exists(dstdir):
        os.makedirs(dstdir)
    srcs = ' '.join(srcs)
    cmd = "/bin/cp -r%s %s %s" % (v, srcs, dst)
    print "Executing ", cmd
    if os.system(cmd) != 0:
        raise Exception("Copying failed: %s" % cmd)

############################
# Start Building
############################

data = dict(
    lang = lang_codes,
    role = role_codes,
    theme = theme_codes )

path_combinations = compute_possible_pathdata(data)

templates = [
    Template('login.html', dsts = ['login']),
    Template('dashboard.html', dsts = ['{{ lang }}/{{ role }}/{{ theme }}/dashboard']),
    SHPAMLTemplate('members/profile.html', dsts = ['{{ lang }}/{{ role }}/{{ theme }}/profile']),
    SHPAMLTemplate('members/memberships.html', dsts = ['{{ lang }}/{{ role }}/{{ theme }}/memberships']),
    Template('members/contact.html', dsts = ['{{ lang }}/{{ role }}/{{ theme }}/contact']),
    Template('members/billing.html', dsts = ['{{ lang }}/{{ role }}/{{ theme }}/billing']),
    Template('members/preferences.html', dsts = ['{{ lang }}/{{ role }}/{{ theme }}/preferences']),
    Template('members/security.html', dsts = ['{{ lang }}/{{ role }}/{{ theme }}/security']),
    SHPAMLTemplate('spaces/new.html', dsts = ['{{ lang }}/{{ role }}/{{ theme }}/spaces/new']),
    SHPAMLTemplate('spaces/list.html', dsts = ['{{ lang }}/{{ role }}/{{ theme }}/spaces/list']),
    SHPAMLTemplate('spaces/plans/new.html', dsts = ['{{ lang }}/{{ role }}/{{ theme }}/spaces/plans/new']),
    SHPAMLTemplate('spaces/plans/list.html', dsts = ['{{ lang }}/{{ role }}/{{ theme }}/spaces/plans/list']),
    Template('next.html', dsts = ['{{ lang }}/{{ role }}/{{ theme }}/next']),
    Template('activate.html', dsts = ['activate']),
    CSSTemplate('css/main.css', dsts = ['css/main.css', 'themes/{{ theme }}/main.css']),
    CSSTemplate('css/MooDialog.css', dsts = ['css/MooDialog.css', '{{ lang }}/{{ role }}/{{ theme }}/css/MooDialog.css']),
    Template('setup.html', dsts = ['setup']),
    ]

def copy_contribs():
    contribdirs = (pathjoin(contrib_root, name) for name in contribs)
    copydirs(contribdirs, dstroot)

def copy_statics():
    staticdirs = (pathjoin(static_root, s) for s in statics)
    copydirs(staticdirs, dstroot)

def compile_templates():
    for template in templates:
        dst_data = dict(
            lang = lang_codes,
            role = role_codes,
            theme = theme_codes )
        template.build({}, dst_data=dst_data)

def copy_theme_assets():
    asset_dirs = ('images',)
    combinations = itertools.product(theme_codes, asset_dirs)
    srcdir_combinations = (pathjoin(themes_srcroot, *c) for c in combinations)
    #print list(srcdir_combinations)
    src_dirs = (path for path in srcdir_combinations if os.path.isdir(path))
    for src_dir in src_dirs:
        dst = pathjoin(dstroot, src_dir.replace(srcroot, '')[1:])
        copydirs(src_dir, dst)

def prep():
    if not os.path.exists(dstroot):
        os.mkdir(dstroot)

prep()
copy_theme_assets()
copy_contribs()
copy_statics()
compile_templates()
