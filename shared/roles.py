class ACObject(object): # Access Control Object
    def __init__(self, name):
        self.name = name
        self.label = name.replace('_', ' ').capitalize()
        self.description = self.label + ' ' + self.__class__.__name__.capitalize()
    def __str__(self):
        return "<%s: %s>" % (self.__class__.__name__, self.label)
    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, self.label)

class Permission(ACObject): pass

admin = Permission('admin')
access_business = Permission('access_business')
manage_own_profile = Permission('manage_own_profile')
manage_biz_invoices = Permission('manage_biz_invoices')
manage_biz_profile = Permission('manage_biz_profile')
apply_membership = Permission('apply_membership')
view_own_invoices = Permission('view_own_invoices')
search_biz = Permission('search_biz')
approve_plan = Permission('approve_plan')
invite_member = Permission('invite_member')
activate_member = Permission('activate_member')
change_member_role = Permission('change_member_role')

class Role(ACObject): pass

admin_role = Role('admin')
admin_role.permissions = [admin]

registered = Role("registered")
registered.permissions = [
    apply_membership,
    ]

member = Role("member")
member.permissions = [
    access_business,
    manage_own_profile,
    search_biz,
    view_own_invoices,
    ]

host = Role("host")
host.permissions = [
    approve_plan,
    invite_member,
    manage_biz_profile,
    activate_member,
    manage_biz_invoices,
    change_member_role,
    ]

all_roles = (v for v in globals().values() if isinstance(v, Role))
all_permissions = (v for v in globals().values() if isinstance(v, Permission))
