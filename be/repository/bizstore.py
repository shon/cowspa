import datetime

from tests import common
import bases.persistence as persistence
from be.repository import schemas

RedisStore = persistence.RedisStore

class bizStore(RedisStore):
    
    def biz_add(self,name):
	print "inside add biz"

    def biz_get_all(self):
	print "inside biz get all"

    def biz_search_by_name(self,name):
	    print "searching by name for: ", name


if __name__ == '__main__':
    print "bizstore"

    bz = bizStore()
    bz.biz_add('name')
    bz.biz_get_all()
    bz.biz_search_by_name('Named Business for Search')
