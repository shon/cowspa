from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader('commonlib/messaging/templates'))

def render(template, data):
    template = env.get_template(template)
    return template.render(**data)

class Message(object):
    def __init__(self, path):
        self.path = path
    def create_message(self, data):
        rendered = render(self.path, data)
        message_dict = dict(author = data.get('author'), to = data.get('to'))
        exec(rendered, {}, message_dict)
        return message_dict

activation = Message('activation')
