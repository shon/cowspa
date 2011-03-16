import be.bases as bases

import apis
import apis.members
import apis.users

cowapp_version = '0.1'

get_cowapp_version = lambda: cowapp_version

class Login(bases.APISpec):
    path = cowapp_version + '/login'

class MemberDetails(bases.APISpec):
    """
    Returns member information
    """
    path = cowapp_version + '/members/<int:member_id>/details'

class Version(bases.APISpec):
    """
    Application version
    """
    path = cowapp_version + '/version'

class AddMember(bases.APISpec):
    path = cowapp_version + '/members/new'

login = bases.APISpec(apis.users.login)
login.path = cowapp_version + '/login'

register = bases.APISpec(apis.members.register)
register.path = cowapp_version + '/members/register'

activate = bases.APISpec(apis.members.activate)
activate.path = cowapp_version + '/members/activate'

member_details = bases.APISpec(apis.members.get_details)
member_details.path = cowapp_version + '/members/<int:member_id>/details'

add_member = bases.APISpec(apis.members.add)
add_member.path = cowapp_version + '/members/new'
#add_member.validator = apis.members.AddValidator

cowapp = bases.Application()

cowapp.add_api(login)
cowapp.add_api(register)
cowapp.add_api(activate)
cowapp.add_api(Version(get_cowapp_version))
cowapp.add_api(member_details)
cowapp.add_api(add_member)
