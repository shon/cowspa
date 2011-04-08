import be.bootstrap
import be.apps
app = be.apps.cowapp
token = app.root.process_slashed_path('0.1/login')('shon0', 'secret')['result']
app.set_context(token)
req_id = app.root['0.1'].requests.new('membership', biz_id=1)['result']
print req_id
print app.root['0.1'].requests[req_id].act(1)
print app.root['0.1'].requests[req_id]()
