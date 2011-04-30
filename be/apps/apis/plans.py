import itertools
import bases
import bases.persistence as persistence
import be.repository.stores as stores

import members as memberslib

plan_store = stores.plan_store

class Plans(bases.app.Collection):
    methods_available = ['new', 'list']
    def new(self, name, description, owner):
        plan = self.store.add(name, description, owner)
        return plan.id

class PlanMethods(bases.app.ObjectMethods):
    methods_available = ['info', 'get', 'set']
    id_name = 'plan_id'
    def to_info(self, plan):
        d = self.store.obj2dict(plan)
        d.pop('subscribers')
        d.pop('created')
        return d
    def info(self, plan_id):
        plan = self.store.fetch_by_id(plan_id)
        return self.to_info(plan)

class Subscribers(bases.app.Collection):
    methods_available = ['new', 'list', 'delete']
    def new(self, subscriber_id, plan_id):
        plan = self.store.fetch_by_id(plan_id)
        subscribers = plan.subscribers
        if subscriber_id not in subscribers:
            plan.subscribers.append(subscriber_id)
            plan.save()
    def list(self, plan_id):
        plan = self.store.fetch_by_id(plan_id)
        return [memberslib.member_methods.info(s) for s in plan.subscribers]
    def delete(self, plan_id, subscriber_id):
        plan = self.store.fetch_by_id(plan_id)
        plan.subscribers.remove(subscriber_id)

plans = Plans(plan_store)
plan_methods = PlanMethods(plan_store)
subscribers = Subscribers(plan_store)
