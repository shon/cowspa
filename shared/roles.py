class ACObject(object): # Access Control Object
    def __init__(self):
        self.label = self.__class__.__name__.capitalize()
        self.description = self.label
    def __str__(self):
        return "<%s: %s>" % (self.__class__.__name__, self.label)
    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, self.label)

class Permission(ACObject): pass

access_business = Permission()
access_business.name = "access_business"
access_business.label = "Access Business"

manage_own_profile = Permission()
manage_own_profile.name = "manage_own_profile"

manage_biz_invoices = Permission()
manage_biz_invoices.name = "manage_biz_invoices"

manage_biz_profile = Permission()
manage_biz_profile.name = "manage_biz_profile"

apply_membership = Permission()
apply_membership.name = "apply_membership"

view_own_invoices = Permission()
view_own_invoices.name = "view_own_invoices"

search_biz = Permission()
search_biz.name = "search_biz"

approve_membership = Permission()
approve_membership.name = "approve_membership"

invite_member = Permission()
invite_member.name = "invite_member"

activate_member = Permission()
activate_member.name = "activate_member"

change_member_role = Permission()
change_member_role.name = "change_member_role"

class Role(ACObject): pass

registered = Role()
registered.name = "registered"
registered.permissions = [
    apply_membership,
    ]

member = Role()
member.name = "member"
member.permissions = [
    access_business,
    manage_own_profile,
    search_biz,
    view_own_invoices,
    ]

host = Role()
host.name = "host"
host.permissions = [
    approve_membership,
    invite_member,
    manage_biz_profile,
    activate_member,
    manage_biz_invoices,
    change_member_role,
    ]

all_roles = (v for v in globals().values() if isinstance(v, Role))
all_permissions = (v for v in locals().values() if isinstance(v, Permission))
