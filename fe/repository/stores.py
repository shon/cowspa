import datetime

from commonlib.helpers import odict

import bases.persistence as persistence
import schemas

RedisStore = persistence.RedisStore

class UIPref(RedisStore):
    defaults = dict (
        start_page = "/next" )
    model = schemas.UIPref
    def add(self, user_id):
        pref = self.model(user_id=user_id)
        pref.save()
        return pref
    def fetch_one_by(self, *args, **kw):
        try:
            super(UIPref, self).fetch_one_by(*args, **kw)
        except IndexError, err:
            return odict(self.defaults)

ui_pref_store = UIPref()
