import common
#import redisco
#redisco.connection_setup(host="")

import be.bootstrap
import be.apps

app = be.apps.cowapp
reg_data =  dict(first_name="Shekhar", last_name="Tiwatne", email='cowspa.dev@gmail.com')
member_data= dict(username='shon', password='secret', address='Pune', city='Pune', country='IND', pincode='411000', organization='pydevers', home_no=None, mobile_no=None,  short_description="Programmer", long_description="<i>Programmer</i>", twitter="shon_", facebook=None, blog=None, linkedin=None, use_gravtar=None, enabled=True)

username = member_data['username']

biz_data = dict(name="My New Biz")
plan_data = dict(name='Hub 25', description='A simple plan')

res = app.root['0.1'].registrations.new(ipaddr='127.0.0.1', **reg_data)
retcode, result = res['retcode'], res['result']
activation_id = result

res = app.root['0.1'].registrations.by_id(activation_id)
retcode, result = res['retcode'], res['result']
activation_key = result['activation_key']

app.root['0.1'].registrations.activate(activation_key, **member_data)

res = app.root['0.1'].login(member_data['username'], member_data['password'])
retcode, result = res['retcode'], res['result']
token = result

res1 = app.root['0.1'].login(member_data['username'], member_data['password'])
assert res == res1, "cookies must match"

app.root.set_context(token)

app.root['0.1'].me.update({'profile': member_data})
res = app.root['0.1'].biz.new(**biz_data)
retcode, result = res['retcode'], res['result']
biz_id = result

app.root['0.1'].plans.list()

res = app.root['0.1'].plans.new(biz_id=biz_id, **plan_data)
retcode, result = res['retcode'], res['result']
plan_id = result

role_data = dict(biz_id=biz_id, role_names=['host', 'member'])
app.root['0.1'].users[username].assign_roles(**role_data)

app.root['0.1'].plans[plan_id].info()
app.root['0.1'].biz[biz_id].plans()
#app.root['0.1'].plans[4].subscribers.new(1)

req_data = dict(plan_id=plan_id)
res = app.root['0.1'].requests.new(name = 'membership', reg_data=req_data)
retcode, result = res['retcode'], res['result']
req_id = result

app.root['0.1'].requests[req_id].update(mod_data=dict(status=1))
app.root['0.1'].requests[req_id].info()

username = username + '1'
member1_data = dict(username=username, first_name='Shon', password='secret', enabled=True, email='abc@example.com')
member_id = app.root['0.1'].members.new(**member1_data)
#
#def test_get(member_id):
#    member = app.root['0.1'].members.get(member_id)
#
##print common.timer(test_add, [data], 1)
##print common.timer(test_get, [1])
##print common.timer(test_add, [data], 10000)
##print common.timer(test_get, [1])
