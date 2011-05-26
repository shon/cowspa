import datetime
import itertools
import bases
import bases.persistence as persistence
import be.repository.stores as stores
import be.libs.signals as signals

import members as memberslib

plan_store = stores.plan_store
plansubscribers_store = stores.plansubscribers_store

class Plans(bases.app.Collection):
    methods_available = ['new', 'list']
    def new(self, name, bizplace_id, description, enabled=True):
        created = datetime.datetime.now()
        return self.store.add(name, bizplace_id, description, enabled, created)

class PlanMethods(bases.app.ObjectMethods):
    methods_available = ['info', 'get', 'set']
    id_name = 'plan_id'
    def info(self, plan_id):
        return self.store.get(plan_id)

class Subscribers(bases.app.Collection):
    methods_available = ['new', 'list', 'delete']
    def new(self, subscriber_id, plan_id):
        if self.store.get_by(plan_id=plan_id, subscriber_id=subscriber_id):
            pass
        else:
            self.store.add(plan_id, subscriber_id)
    def list(self, plan_id):
        plan = self.store.get(plan_id)
        return [memberslib.member_methods.info(s) for s in plan.subscribers]
    def delete(self, plan_id, subscriber_id):
        raise NotImplemented

plans = Plans(plan_store)
plan_methods = PlanMethods(plan_store)
subscribers = Subscribers(plansubscribers_store)

signals.connect("plan_approved", subscribers.new)
