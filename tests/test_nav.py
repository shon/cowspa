import be.bootstrap
import be.apps
app = be.apps.cowapp
token = app.root.process_slashed_path('0.1/login')('shon0', 'secret')['result']
app.set_context(token)
print app.root['0.1'].members['1']()
