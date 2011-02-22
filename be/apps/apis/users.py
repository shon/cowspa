import be.repository.stores as stores
userstore = stores.userstore

def authenticate(username, password):
    try:
        user = userstore.fetch_one_by(username=username)
    except IndexError:
        return False
    return user.password == password

def add(username, password, enabled=True):
    user = userstore.add(username, password, enabled)
    return user
