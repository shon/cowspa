import be.bootstrap
import be.apps

app = be.apps.cowapp['0.1']

data = dict(username='shon0', password='secret', enabled=True, email='who@example.net', address='Pune', city='Pune', country='IND', pincode='411000', organization='pydevers', home_no=None, mobile_no=None, first_name="Shekhar", last_name="Tiwatne", short_description="Programmer", long_description="<i>Programmer</i>", twitter_handle="shon_", facebook_name=None, blog=None, linkedin_contact=None, use_gravtar=None)

def test_add(data):
    username = data['username']
    data['username'] = username + str(int(username[-1]) + 1)
    member_id = app.members.add(**data)

def test_get(member_id):
    member = app.members.get(member_id)

def test_register(data):
    return app.members.register(data['first_name'], data['last_name'], data['email'], '127.0.0.1')

def test_activate(activation_key):
    return app.members.activate(activation_key, **data)

def test_auth(data):
    return app.login('shon0', 'secret')

import common
print test_register(data)
activation_key = test_register(data)['result']
print activation_key
print test_activate(activation_key)
print test_auth(data) == test_auth(data)
#print common.timer(test_add, [data], 1)
#print common.timer(test_get, [1])
#print common.timer(test_add, [data], 10000)
#print common.timer(test_get, [1])
