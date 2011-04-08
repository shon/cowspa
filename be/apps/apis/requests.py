import datetime
import inspect

import be.repository.stores as stores

ACTION_AWAITED = 0
APPROVED = 1
REJECTED = 2
ON_HOLD = 3
IGNORED = 4
CONFUSED = 5 # ;)

request_store = stores.request_store

class Request(object): pass

class NewNetworkRequest(Request):
    name = 'new_network'
    approver_perm = 'superuser'
    label = "business network request"

class MembershipRequest(Request):
    name = 'membership'
    approver_perm = 'Biz:{{biz_id}}:approve_membership'
    label = "membership request"

requests = dict((req.name, req) for req in globals().values() if inspect.isclass(req) and req is not Request and issubclass(req, Request))

def create_request(name, **req_data):
    requestor_id = env.context.user_id
    req = request_store.add(name=name, requestor_id=requestor_id, status=ACTION_AWAITED, req_data=req_data)
    return req.id

def act_on_request(request_id, status=APPROVED):
    approver_id = env.context.user_id
    mod_data = dict(status  = status, acted_at = datetime.datetime.now())
    request_store.edit(request_id, mod_data)
    return True

def list_requests(user_id):
    return [request_store.obj2dict(req) for req in request_store.fetch_by(requestor_id=user_id)]

def info(request_id):
    req = request_store.fetch_by_id(request_id)
    d = request_store.obj2dict(req)
    d['label'] = requests[req.name].label
    return d
