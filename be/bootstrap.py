import __builtin__
import sys
import conf
import commonlib
import commonlib.helpers
import commonlib.messaging.email
import gevent.local
import be.repository.pgdb as pgdb
import be.repository.stores as stores

def setdefaultencoding():
    reload(sys)
    sys.setdefaultencoding('utf-8')

def init():
    class env: pass
    env.config = conf.parse_config()
    commonlib.helpers.random_key_gen = commonlib.helpers.RandomKeyFactory(env.config.random_str)
    env.mailer = commonlib.messaging.email.Mailer(env.config.mail)
    env.mailer.start()
    env.context = gevent.local.local()
    return env

def dbsetup():
    pgdb.provider.startup()
    pgdb.provider.tr_start(env.context)
    stores.startup()
    pgdb.provider.tr_complete(env.context)

setdefaultencoding()
__builtin__.env = init()
dbsetup()

