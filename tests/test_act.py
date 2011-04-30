import common
import datetime

from be import arep

import be.arep.actstore as asto

astor = asto.actStore()
#astor.activity_add('Name',datetime.datetime.now())

print astor.activity_get_all()
print "----------------"
print astor.activity_get_latest()
print astor.activity_search_by_type('Type to search')
