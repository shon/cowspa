import __builtin__
import conf
import commonlib
import commonlib.helpers
import commonlib.messaging.email

def init():
    class env: pass
    env.config = conf.parse_config()
    commonlib.helpers.random_key_gen = commonlib.helpers.RandomKeyFactory(env.config.random_str)
    env.mailer = commonlib.messaging.email.Mailer(env.config.mail)
    env.mailer.start()
    return env

__builtin__.env = init()
