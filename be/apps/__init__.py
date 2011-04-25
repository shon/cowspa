import bases.app as applib
import wrappers as wrapperslib

import apis
import apis.members
import apis.users
import apis.biz
import apis.requests

cowapp_version = '0.1'

get_cowapp_version = lambda: cowapp_version
get_cowapp_version.console_debug = True

login = apis.users.login

user_permissions = apis.users.get_user_permissions

list_requests = apis.requests.list_requests
create_request = apis.requests.create_request
act_on_request = apis.requests.act_on_request
request_info = apis.requests.info

def api_factory(f):
    wrappers = (wrapperslib.console_debugger, wrapperslib.permission_checker)
    return applib.API(f, wrappers)

mapper = applib.Mapper(cowapp_version)
mapper.add_api_factory(api_factory)
mapper.connect(login)
mapper.connect('version', get_cowapp_version)
mapper.connect_collection('registrations', apis.members.registrations)
mapper.connect_collection('biz', apis.biz.biz)
mapper.connect_collection('members', apis.members.members)
mapper.connect_object_methods('members/<int:member_id>', apis.members.member_methods)
mapper.connect_object_methods('me', apis.members.me_methods)
mapper.connect_object_methods('users/<username>', apis.users.user_methods)

tree = mapper.build()

cowapp = applib.TraverserFactory(applib.PyTraverser, tree, apis.users.session_lookup)
cowapp_http = applib.TraverserFactory(applib.HTTPTraverser, tree, apis.users.session_lookup)
