import be.bases as bases

import apis
import apis.members
import apis.users
import apis.biz

cowapp_version = '0.1'

get_cowapp_version = lambda: cowapp_version
get_cowapp_version.console_debugger = True

login = apis.users.login
login.console_debugger = True

register = apis.members.register

activate = apis.members.activate

member_details = apis.members.get_details

add_member = apis.members.add

assign_roles = apis.users.assign_roles

user_info = apis.users.info

add_biz= apis.biz.add

tree = bases.Tree('')
app = tree.add_branch(name=cowapp_version)
app.add_branch(login)
app.add_branch(get_cowapp_version, 'version')
members = app.add_branch(name='members')
members.add_branch(register)
members.add_branch(activate)
members.add_branch(add_member, 'new')
member_id = members.add_branch(member_details, 'int:member_id')
biz = app.add_branch(name='biz')
biz.add_branch(add_biz, 'new')
users = app.add_branch(name='users')
username = users.add_branch(user_info, 'str:username')
username.add_branch(user_info, 'info')
username.add_branch(assign_roles)

cowapp = bases.TraverserFactory(tree)
