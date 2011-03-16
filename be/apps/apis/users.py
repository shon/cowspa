from pycerberus.schema import SchemaValidator
from pycerberus.validators import StringValidator

import commonlib
import be.repository.stores as stores

userstore = stores.userstore
session_store = stores.session_store

def create_session(username):
    token  = commonlib.helpers.random_key_gen()
    user = userstore.fetch_one_by(username=username)
    session = session_store.add(token, user.id)
    return session.token

def get_or_create_session(username):
    user = userstore.fetch_one_by(username=username)
    try:
        session = session_store.fetch_one_by(user_id=user.id)
        token = session.token
    except IndexError:
        token = create_session(username)
    return token

def authenticate(username, password):
    try:
        user = userstore.fetch_one_by(username=username)
    except IndexError:
        return False
    return user.password == password

def login(username, password):
    if authenticate(username, password):
        return get_or_create_session(username)

class AddValidator(SchemaValidator):
    username = StringValidator(required=True)
    password = StringValidator(required=True)

def add(username, password, enabled=True):
    user = userstore.add(username, password, enabled)
    return user.id

add.validator = AddValidator()
