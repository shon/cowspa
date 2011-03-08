import be.bases as bases

Command = bases.Command
APINode = bases.APINode
Application = bases.Application

import apis
import apis.members

cowapp = APINode()

members = APINode()
members.add_api(Command(apis.members.register))
members.add_api(Command(apis.members.activate))
members.add_api(Command(apis.members.add))
members.add_api(Command(apis.members.get))
#members.add_api(Command(apis.members.authenticate))
cowapp.add_node('members', members)
