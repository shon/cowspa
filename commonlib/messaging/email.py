import turbomail
from turbomail.control import interface
import html2text

class Mailer(object):

    def __init__(self, config):
        self.config = config

    def start(self):
        interface.start(self.config)

    def stop(self):
        interface.stop()

    def send(self, author, to, subject='', rich='', plain='', cc=[], bcc=[]):
        if not rich and plain:
            msg = turbomail.Message(author, to, subject, cc=cc, bcc=bcc, plain=plain)
        else:
            if not plain:
                plain = html2text.html2text(rich)
            msg = turbomail.Message(author, to, subject, cc=cc, bcc=bcc, rich=rich, plain=plain)
        msg.send()
        return True


def test():
    config = {
        'mail.on': True,
        'mail.transport': 'smtp',
        'mail.smtp.server': 'smtp.gmail.com',
        'mail.smtp.port': 587,
        'mail.smtp.tls': True,
        'mail.smtp.username': 'me@gmail.com',
        'mail.smtp.password': 'secret',
        'mail.smtp.debug': True,
        'mail.utf8qp.on': True
    }
    mailer = Mailer(config)
    to = "to.me@gmail.com"
    subject = "TurboMail test"
    rich = """
    <html>
        <body>
            <strong>Hi There</strong>
        </body>
    </html>"""
    mailer.start()
    mailer.send("to.me@gmail.com", to, subject, rich=rich)
