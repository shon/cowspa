import datetime
import inspect

import bases
import be.repository.stores as stores
import be.libs.macros as macros
import be.libs.signals as signals

ACTION_AWAITED = 0
APPROVED = 1
REJECTED = 2
ON_HOLD = 3
IGNORED = 4
CONFUSED = 5 # ;)

request_store = stores.request_store
user_store = stores.userstore
user_perms_store = stores.user_perms_store
permission_store = stores.permission_store

class Request(object): pass

class NewNetworkRequest(Request):
    name = 'new_network'
    approver_perm = 'superuser'
    label = "business network request"

class MembershipRequest(Request):
    name = 'membership'
    approver_perm = 'Biz:{{biz_id_from_plan_id}}::' + permission_store.fetch_one_by(name='approve_plan').id
    label = "membership request"
    template = "Membership request by \"{{requestor_display_name}}\" for plan {{name_from_plan_id}}"
    @classmethod
    def approve(self, req):
        signals.send_signal('plan_approved', req.requestor_id, req.req_data['plan_id'])

request_types = dict((req.name, req) for req in globals().values() if inspect.isclass(req) and req is not Request and issubclass(req, Request))

def is_approver(user_id, req):
    permission_ids = user_perms_store.fetch_one_by(user_id=user_id).permission_ids
    return req.approver_perm in permission_ids

class Requests(bases.app.Collection):
    methods_available = ['new', 'list', 'forme']

    def new(self, name, req_data):
        requestor_id = env.context.user_id
        approver_perm = macros.process(request_types[name].approver_perm, env.context, req_data)
        req = request_store.add(name=name, requestor_id=requestor_id, status=ACTION_AWAITED, approver_perm=approver_perm,
            req_data=req_data)
        return req.id

    def forme(self):
        return [request_methods.to_info(req) for req in self.store.fetch_all() if is_approver(env.context.user_id, req)]

    def mine(self):
        requestor_id = env.context.user_id
        return [request_store.obj2dict(req) for req in request_store.fetch_by(requestor_id=requestor_id)]

class RequestMethods(bases.app.ObjectMethods):
    methods_available = ['info', 'update']
    id_name = 'request_id'
    def update(self, request_id, mod_data):
        approver_id = env.context.user_id
        req = self.store.fetch_by_id(request_id)
        if not is_approver(approver_id, req):
            raise Exception("approver does not have permissions")
        if mod_data.get('status') == APPROVED:
            request_types[req.name].approve(req)
        mod_data.update(acted_at = datetime.datetime.now(), approver_id=approver_id)
        request_store.edit(request_id, mod_data)
        return True

    def to_info(self, req):
        d = request_store.obj2dict(req)
        d['label'] = request_types[req.name].label
        data =req.req_data
        data['requestor_id'] = req.requestor_id
        d['description'] = macros.process(request_types[req.name].template, env.context, data)
        return d

    def info(self, request_id):
        req = request_store.fetch_by_id(request_id)
        return self.to_info(req)

requests = Requests(stores.request_store)
request_methods = RequestMethods(stores.request_store)
