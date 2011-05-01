import datetime
import inspect

import bases
import be.repository.stores as stores
import be.libs.macros as macros

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

request_types = dict((req.name, req) for req in globals().values() if inspect.isclass(req) and req is not Request and issubclass(req, Request))

def can_approve(user_id, request_id):
    req = request_store.fetch_by_id(request_id)
    permission_ids = user_perms_store.fetch_one_by(user_id=user_id).permission_ids
    return req.approver_perm in permission_ids

class Requests(bases.app.Collection):
    methods_available = ['new', 'list']

    def new(self, name, **req_data):
        requestor_id = env.context.user_id
        approver_perm = macros.process(request_types[name].approver_perm, env.context, req_data)
        req = request_store.add(name=name, requestor_id=requestor_id, status=ACTION_AWAITED, approver_perm=approver_perm,
            req_data=req_data)
        return req.id

    def requests_for_me(self):
        reqs = [req for req in self.store.fetch_all() if is_approver(env.context.user_id, req)]
        return [request_store.obj2dict(req) for req in request_store.fetch_by(requestor_id=requestor_id)]

    def my_requests(self):
        requestor_id = env.context.user_id
        return [request_store.obj2dict(req) for req in request_store.fetch_by(requestor_id=requestor_id)]

class RequestMethods(bases.app.ObjectMethods):
    methods_available = ['info', 'update']
    id_name = 'request_id'
    def update(self, request_id, mod_data):
        approver_id = env.context.user_id
        if not can_approve(approver_id, request_id):
            raise Exception("approver does not have permissions")
        mod_data.update(acted_at = datetime.datetime.now(), approver_id=approver_id)
        request_store.edit(request_id, mod_data)
        return True

    def info(self, request_id):
        req = request_store.fetch_by_id(request_id)
        d = request_store.obj2dict(req)
        d['label'] = request_types[req.name].label
        return d

requests = Requests(stores.request_store)
request_methods = RequestMethods(stores.request_store)
