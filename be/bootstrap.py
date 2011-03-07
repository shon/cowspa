import __builtin__
import conf
import commonlib.messaging.email

def init():
    class env: pass
    env.config = conf.parse_config()
    env.mailer = commonlib.messaging.email.Mailer(env.config.mail)
    env.mailer.start()
    return env

__builtin__.env = init()
