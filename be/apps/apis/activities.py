import datetime

import bases
import bases.persistence as persistence
import be.repository.stores as stores

class Activities(bases.app.Collection):
    methods_available = ['new', 'list']

    def new(self, name):
        created = datetime.datetime.now() # to be removed once redisco fixes https://github.com/iamteem/redisco/issues/18
        activity = self.store.add(name=name, created=now)
        return activity.id

    def latest(self):
        return self.model.objects.zfilter(created__lt=datetime.datetime.now())

    def by_date(self, start, end):
        """
        start: datetime
        end: datetime
        """
        return self.model.objects.zfilter(created__in=(start_date, end_date))

activities = Activities(stores.activity_store)
