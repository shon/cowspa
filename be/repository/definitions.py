import cPickle

import redis
import redisco
import redisco.models as models

type = ['USER_MG',
	'USER_ADD'
	'INVOICE_ADD',
	'INVOICE_DELAYED'
	]

category = ['CATEGORY_1',
	'CATEGORY_2',
	'CATEGORY_3',
	]

class Activity(models.Model):
    """
    	activity
    """

    name = models.Attribute(required=True)
    added = models.DateTimeField(auto_now_add=False)
