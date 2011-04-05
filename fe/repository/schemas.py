import redis
import redisco
import redisco.models as models

class UIPref(models.Model):
    start_page = models.Attribute()
    user_id = models.Attribute(required=True)
