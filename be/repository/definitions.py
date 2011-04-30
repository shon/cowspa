import cPickle

import redis
import redisco
import redisco.models as models

types = ['USER_MG',
	'USER_ADD'
	'INVOICE_ADD',
	'INVOICE_DELAYED'
	]

categores = ['CATEGORY_1',
	'CATEGORY_2',
	'CATEGORY_3',
