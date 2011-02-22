import be.bases as bases

Command = bases.Command
APINode = bases.APINode
Application = bases.Application

import apis
import apis.users

cowapp = APINode()

users = APINode()
users.add_api(Command(apis.users.add))
users.add_api(Command(apis.users.authenticate))
cowapp.add_node('users', users)
