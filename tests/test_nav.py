import be.bootstrap
import be.apps
app = be.apps.cowapp
token = app.http('0.1/login', 'POST', dict(username='shon', password='x'))['result']
app.set_context(token)
print app.root['0.1'].members['1']()
