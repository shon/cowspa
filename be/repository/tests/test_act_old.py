import os
import sys

if os.environ['COWSPA_HOME'] is not None:
    sys.path.append(os.environ['COWSPA_HOME'])

#try:
#    os.environ['COWSPA_HOME']
#    sys.path.append(os.environ['COWSPA_HOME'])
#except OSError:
#    print "Path not set"


print sys.path

#from be import arep
import be as b

print dir(b)
print b.__package__
for item in dir(b):
    print item, b['item']

from be import apps
from be import repository
import be as c
print dir(c)

import be as d
print dir(d)
from be import arep
print dir(d)


#print arep
