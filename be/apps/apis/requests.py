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

class Request(object):
    @classmethod
    def set_approved(self, req):
        request_store.update(req.id, approver_id=env.context.user_id, status=APPROVED)

class NewNetworkRequest(Request):
    name = 'new_network'
    approver_perm = 'superuser'
    label = "business network request"

class MembershipRequest(Request):
    name = 'membership'
    approver_perm = 'Biz:{{biz_id_from_plan_id}}::' + str(permission_store.get_one_by(name='approve_plan').id)
    label = "membership request"
    template = 'Membership request by "{{requestor_display_name}}" for plan {{name_from_plan_id}}'
    @classmethod
    def approve(self, req):
        signals.send_signal('plan_approved', req.requestor_id, req.req_data['plan_id'])
        self.set_approved(req)

class NewBizRequest(Request):
    name = "newbiz"
    label = "add new business request"
    approver_perm = "{{id_by_name:admin}}"
    template = 'New co-working place "{{name}}" at {{city}} by "{{requestor_display_name}}"'
    @classmethod
    def approve(self, req):
        signals.send_signal('newbiz_approved', director_id=req.requestor_id, **req.req_data)
        self.set_approved(req)

request_types = dict((req.name, req) for req in globals().values() if inspect.isclass(req) and req is not Request and issubclass(req, Request))

def is_approver(user_id, req):
    permission_ids = [p.permission_id for p in user_perms_store.get_by(user_id=user_id, _fields=['permission_id'])]
    print permission_ids, req.approver_perm
    return req.approver_perm in permission_ids

class Requests(bases.app.Collection):
    methods_available = ['new', 'list', 'forme']

    def new(self, name, req_data):
        requestor_id = env.context.user_id
        approver_perm = macros.process(request_types[name].approver_perm, env.context, req_data)
        created = datetime.datetime.now()
        return request_store.add(name=name, created=created, requestor_id=requestor_id, status=ACTION_AWAITED, approver_perm=approver_perm, req_data=req_data)

    def forme(self):
        return [request_methods.to_info(req) for req in self.store.get_by(status=ACTION_AWAITED) if is_approver(env.context.user_id, req)]

    def mine(self):
        requestor_id = env.context.user_id
        return [request_store.obj2dict(req) for req in request_store.get_by(requestor_id=requestor_id)]

class RequestMethods(bases.app.ObjectMethods):
    methods_available = ['info', 'update']
    id_name = 'request_id'
    def update(self, request_id, mod_data):
        approver_id = env.context.user_id
        req = self.store.get(request_id)
        if not is_approver(approver_id, req):
            raise Exception("approver does not have permissions")
        if mod_data.get('status') == APPROVED:
            request_types[req.name].approve(req)
        mod_data.update(acted_at = datetime.datetime.now(), approver_id=approver_id)
        request_store.update(request_id, **mod_data)
        return True

    def to_info(self, req):
        req['label'] = request_types[req.name].label
        data =req.req_data
        data['requestor_id'] = req.requestor_id
        req['description'] = macros.process(request_types[req.name].template, env.context, data)
        return req

    def info(self, request_id):
        req = request_store.get(request_id)
        return self.to_info(req)

requests = Requests(stores.request_store)
request_methods = RequestMethods(stores.request_store)
