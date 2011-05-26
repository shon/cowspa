import bases.app as applib
import wrappers as wrapperslib

import be.repository.pgdb as pgdb
import be.repository.stores as stores

import apis
import apis.members
import apis.users
import apis.biz
import apis.requests
import apis.plans

pg_provider = pgdb.provider

cowapp_version = '0.1'

get_cowapp_version = lambda: cowapp_version
get_cowapp_version.console_debug = True

def api_factory(f):
    wrappers = (wrapperslib.dbtransaction, wrapperslib.console_debugger, wrapperslib.permission_checker) # order is important
    return applib.API(f, wrappers)

mapper = applib.Mapper(cowapp_version)
mapper.add_api_factory(api_factory)
mapper.connect(apis.users.login)
mapper.connect(apis.users.logout)
mapper.connect('version', get_cowapp_version)
mapper.connect_collection('registrations', apis.members.registrations)
mapper.connect_collection('biz', apis.biz.biz)
mapper.connect_object_methods('biz/<int:biz_id>', apis.biz.biz_methods)
mapper.connect_collection('bizplaces', apis.biz.bizplaces)
mapper.connect_object_methods('bizplaces/<int:bizplace_id>', apis.biz.bizplace_methods)
mapper.connect_collection('members', apis.members.members)
mapper.connect_object_methods('members/<int:member_id>', apis.members.member_methods)
mapper.connect_object_methods('me', apis.members.me_methods)
mapper.connect_object_methods('users/<username>', apis.users.user_methods)
mapper.connect_collection('requests', apis.requests.requests)
mapper.connect_object_methods('requests/<int:request_id>', apis.requests.request_methods)
mapper.connect_collection('plans', apis.plans.plans)
mapper.connect_object_methods('plans/<int:plan_id>', apis.plans.plan_methods)
mapper.connect_collection('plans/<int:plan_id>/subscribers', apis.plans.subscribers)
mapper.connect('addsuperuser', apis.members.addsuperuser)

tree = mapper.build()

cowapp = applib.Application('cowspa')
cowapp.on_shutdown.append(pg_provider.shutdown)
cowapp.tree = tree
cowapp.session_lookup = apis.users.session_lookup
pg_provider.tr_start(env.context)
cowapp.startup()
pg_provider.tr_complete(env.context)
