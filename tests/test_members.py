import be.bootstrap
import be.apps

app = be.apps.cowapp

data = dict(username='shon8', password='secret', enabled=True, email='who@example.net', address='Pune', city='Pune', country='IND', pincode='411000', organization='pydevers', home_no=None, mobile_no=None, first_name="Shekhar", last_name="Tiwatne", short_description="Programmer", long_description="<i>Programmer</i>", twitter="shon_", facebook=None, blog=None, linkedin=None, use_gravtar=None)

username = data['username']

def test_add(data):
    username = data['username']
    data['username'] = username + str(int(username[-1]) + 1)
    member_id = app.root['0.1'].members.new(**data)

def test_get(member_id):
    member = app.root['0.1'].members.get(member_id)

def test_register(data):
    return app.root['0.1'].registrations.new(data['first_name'], data['last_name'], data['email'], '127.0.0.1')

def test_activate(activation_id):
    activation_key = app.root['0.1'].registrations.by_id(activation_id)['result']['activation_key']
    return app.root['0.1'].registrations.activate(activation_key, **data)

def test_auth(data):
    return app.root['0.1'].login(username, 'secret')

def test_add_biz():
    data = dict(name="My New Biz")
    return app.root['0.1'].biz.new(**data)

def test_role_assign():
    data = dict(biz_id=1, role_names=['member'])
    return app.root['0.1'].users[username].assign_roles(**data)

import common
print test_register(data)
activation_id = test_register(data)['result']
print test_activate(activation_id)
print test_auth(data) == test_auth(data)
print test_add_biz()
print test_role_assign()


#print common.timer(test_add, [data], 1)
#print common.timer(test_get, [1])
#print common.timer(test_add, [data], 10000)
#print common.timer(test_get, [1])
