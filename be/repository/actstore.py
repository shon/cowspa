import datetime

import bases.persistence as persistence
import definitions

RedisStore = persistence.RedisStore

class actStore(RedisStore):
    model = definitions.Activity

    def activity_add(self, name,added):
        activity = self.model(name=name,added=added)
	if not activity.is_valid():
	    print "Errors adding", activity.errors
	else:
            activity.save()
	    print "added"
	    return activity

    def activity_search_by_type(self,type):
	#return 'type\t',type
	return type

    def activity_get_all(self):
	return self.model.objects.all()

    def activity_get_latest(self):
        return self.model.objects.zfilter(added__lt=datetime.datetime.now())

    def activity_search_by(self,name):
	return self.model.objects.filter(name=name)

    def activity_search_by_date(self, start_date, end_date):
        return self.model.objects.zfilter(added__in=(start_date, end_date))



if __name__ == "__main__":
    acs=actStore()

    print "all\n",acs.activity_get_all()
    print "range\n",acs.activity_search_by_date(datetime.datetime(2001,1,1),datetime.datetime.now())
    print "search by\n",acs.activity_search_by('-----------------------000')
    print "----from activity_get_latest------------"
    print acs.activity_get_latest()
