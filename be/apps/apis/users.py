from pycerberus.schema import SchemaValidator
from pycerberus.validators import StringValidator

import be.repository.stores as stores

userstore = stores.userstore

def authenticate(username, password):
    try:
        user = userstore.fetch_one_by(username=username)
    except IndexError:
        return False
    return user.password == password

class AddValidator(SchemaValidator):
    username = StringValidator(required=True)
    password = StringValidator(required=True)

def add(username, password, enabled=True):
    user = userstore.add(username, password, enabled)
    return user.id

add.validator = AddValidator()
