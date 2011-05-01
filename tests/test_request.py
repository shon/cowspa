import be.bootstrap
import be.apps
app = be.apps.cowapp

data = dict(username='shon4', password='secret', req_name='membership')

token = app.root['0.1'].login(data['username'], data['password'])['result']
app.root.set_context(token)
req_id = app.root['0.1'].requests.new(data['req_name'], plan_id=13)['result']
# be.apps.cowapp_http.root('0.1/requests/new', 'POST', {'name':'membership', 'req_data': {'plan_id': 1}})
role_data = dict(biz_id=1, role_names=['host'])
print app.root['0.1'].users[data['username']].assign_roles(**role_data)
print app.root['0.1'].requests[req_id].update(mod_data=dict(status=1))
print app.root['0.1'].requests[req_id].info()
