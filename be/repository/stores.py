import be.bases as bases
import schemas

class RedisStore(bases.BaseStore):
    def add(self, **data):
        """
        returns oid
        """
        raise NotImplemented

    def edit(self, oid, mod_data):
        """
        """

    def list(self, limit=None, order_by=None):
        """
        """
        raise NotImplemented

    def fetch_by(self, **crit):
        """
        """
        return self.model.objects.filter(**crit)

    def fetch_one_by(self, **crit):
        """
        """
        return self.model.objects.filter(**crit)[0]

    def fetch_by_id(self, oid):
        """
        """
        raise NotImplemented

    def remove(self, oid):
        obj = self.model.objects.filter(id=oid)[0]
        return obj.delete()

class UserStore(RedisStore):
    model = schemas.User
    def connect(self):
        pass
    def add(self, username, password, enabled):
        user = self.model(username=username, password=password, enabled=enabled)
        if not user.is_valid():
            print user.errors # fail here
        else:
            user.save()
            return user

userstore = UserStore()
