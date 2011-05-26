import abc

from commonlib.helpers import odict

known_stores = {}

def ref2o(ref):
    _type, id = ref.split(':')
    return known_stores[_type].fetch_by_id(id)

class BaseStore(object):
    __metaclass__ = abc.ABCMeta

class BaseStore(object):

    def __init__(self):
        known_stores[self.model.__name__] = self

    def ref(self, oid):
        return self.model.__name__ + ':' + str(oid)

    def get(self, oid, fields=None):
        """
        oid: object id. match with id field of row.
        fields: fields to include in result. None return all.
        -> odict which is jsonable
        """

    def query(self, q):
        """
        q: query string
        -> list/iterable
        """

    def count(self):
        """
        -> int
        """

    def add(self, data):
        """
        add a row based on data
        data: dict
        -> id/True
        """

    def update(self, oid, mod_data):
        """
        update a row based on mod_data passed
        mod_data: dict
        -> True/False
        """

    def remove(self, oid):
        """
        delete all rows where id is oid
        -> int: number of rows deleted
        """

    def remove_by(self, crit, params):
        """
        delete all matching rows
        crit: eg. WHERE userid = %s
        params: list/iterable
        -> int: number of rows deleted
        """

    def soft_get_one_by(self, *args, **kw):
        try:
            return self.get_one_by(*args, **kw)
        except IndexError, err:
            pass


class PGStore(BaseStore):

    odicter = odict

    def fields2cols(self, fields):
        cols_str = '*'
        if fields:
            cols_str = ', '.join(fields)
        return cols_str

    def get(self, oid, _fields=None):
        """
        oid: object id. match with id field of row.
        _fields: fields to include in result. None return all.
        -> odict which is jsonable
        """
        cols_str = self.fields2cols(_fields)
        q = "SELECT %(cols_str)s FROM %(table_name)s WHERE id = %%s" %dict(table_name=self.model.table_name, cols_str=cols_str)
        env.context.db.execute(q, (oid,))
        cols = (r[0] for r in env.context.db.description)
        values = env.context.db.fetchone()
        if not values:
            raise Exception("User with id %d does not exist" % oid)
        return self.odicter(zip(cols, values))

    def get_all(self, _fields=None):
        cols_str = self.fields2cols(_fields)
        q = "SELECT %(cols_str)s FROM %(table_name)s" %dict(table_name=self.model.table_name, cols_str=cols_str)
        env.context.db.execute(q)
        cols = [r[0] for r in env.context.db.description]
        rows = env.context.db.fetchall()
        return [self.odicter(zip(cols, row)) for row in rows]

    def get_by(self, _fields=None, **crit):
        """
        crit: eg. dict(name='Joe', lang='en')
        -> list of odict
        """
        cols_str = self.fields2cols(_fields)
        crit_keys = crit.keys()
        values = [crit[k] for k in crit_keys]
        crit_keys_s = ' AND '.join(('%s = %%s' % k for k in crit_keys))
        table_name = self.model.table_name
        q = 'SELECT %(cols_str)s FROM %(table_name)s WHERE %(crit_keys_s)s' % locals()
        env.context.db.execute(q, values)
        cols = [r[0] for r in env.context.db.description]
        rows = env.context.db.fetchall()
        return [self.odicter(zip(cols, row)) for row in rows]

    def get_one_by(self, _fields=None, **crit):
        """
        crit: eg. name='Joe', lang='en'
        -> odict
        """
        cols_str = self.fields2cols(_fields)
        crit_keys = crit.keys()
        values = [crit[k] for k in crit_keys]
        crit_keys_s = ', '.join(('%s = %%s' % k for k in crit_keys))
        table_name = self.model.table_name
        q = 'SELECT %(cols_str)s FROM %(table_name)s WHERE %(crit_keys_s)s' % locals()
        env.context.db.execute(q, values)
        cols = [r[0] for r in env.context.db.description]
        row = env.context.db.fetchall()[0]
        return self.odicter(zip(cols, row))


    def query(self, crit, values, fields=None):
        """
        crit: eg. WHERE userid = %s
        values: values to parameterize for crit
        fields: fields to include in result. None return all.
        -> list/iterable
        """
        cols_str = self.fields2cols(fields)
        table_name = self.model.table_name
        q = 'SELECT %(cols_str)s FROM %(table_name)s WHERE %(crit)s' % locals()
        env.context.db.execute(q, values)
        return env.context.db.fetchall()

    def count(self):
        """
        -> int
        """
        env.context.db.execute('SELECT count(*) from %s' % self.model.table_name)
        return env.context.db.fetchone()[0]

    def _add(self, **data):
        cols = data.keys()
        cols_str = ', '.join(cols)
        values_str = ', '.join( ['%s' for i in cols] )
        q = 'INSERT INTO %(table_name)s (%(cols)s) VALUES (%(values_str)s)' % \
            dict(table_name=self.model.table_name, cols=cols_str, values_str=values_str)
        values = tuple(data[k] for k in cols)
        env.context.db.execute(q, values)
        if self.model.auto_id:
            q = 'SELECT lastval()'
            env.context.db.execute(q)
            oid = env.context.db.fetchone()[0]
            return oid
        return True


    def update(self, oid, **mod_data):
        """
        update a row based on mod_data passed
        mod_data: dict
        -> True/False
        """
        cols = mod_data.keys()
        cols_str = ', '.join('%s=%%(%s)s' % (k,k) for k in mod_data.keys())
        table_name = self.model.table_name
        q = 'UPDATE %(table_name)s SET %(cols)s WHERE id = %(oid)s' % dict(table_name=table_name, cols=cols_str, oid=oid)
        values = dict((k, mod_data[k]) for k in cols)
        try:
            env.context.db.execute(q, values)
        except:
            print q
            print values
            raise
        return True

    def update_by(self, crit, **mod_data):
        """
        condition: sql condition expression
        """
        crit_keys = crit.keys()
        values = [crit[k] for k in crit_keys]
        condition = ', '.join(('%s = %%s' % k for k in crit_keys))
        cols = mod_data.keys()
        cols_str = ', '.join('%s=%%s' % k for k in mod_data.keys())
        table_name = self.model.table_name
        q = 'UPDATE %(name)s SET %(cols)s WHERE %(condition)s' % dict(name=table_name, cols=cols_str, condition=condition)
        values = [mod_data[k] for k in cols] + values
        env.context.db.execute(q, values)
        return True

    def remove(self, oid):
        """
        delete all rows where id is oid
        -> int: number of rows deleted
        """

    def remove_by(self, **crit):
        """
        delete all matching rows
        -> int: number of rows deleted
        """

class CachedStore(BaseStore):
    def __init__(self, store):
        self.store = store
        self._cache_by_id = {}
        self.load()
    def load(self, *args, **kw):
        self.store.load(*args, **kw)
        self._cache_by_id = dict((o.id, o) for o in self.store.get_all())
        for k,v in self._cache_by_id.items():
            v['id'] = k
    def add(self, *args, **kw):
        oid = self.store.add(*args, **kw)
        obj = self.store.get(oid)
        self._cache_by_id[oid] = obj
        return obj
    def get_all(self, _fields=None): # fields ignored
        return self._cache_by_id.values()
    def get_one_by(self, _fields=None, **crit):
        for d in self._cache_by_id.values():
            if all(((k,v)==(k,d[k])) for k,v in crit.items()):
                return d
        raise IndexError("No match: %s" % str(crit))
    def get_by(self, _fields, **crit):
        if _fields:
            strip_dict = lambda d: [d[k] for k in _fields]
        else:
            strip_dict = lambda d: d
        return tuple(strip_dict(d) for d in self._cache_by_id.values() if \
            all(((k,v)==(k,d[k])) for k,v in crit.items()))
    def get(self, oid):
        return self._cache_by_id[oid]
    def remove(self, oid):
        raise NotImplemented # unless we take care of cache invalidation


class DBProvider(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def startup(self):
        """
        """
    @abc.abstractmethod
    def shutdown(self):
        """
        """
    @abc.abstractmethod
    def tr_start(self, context):
        """
        context: context storage
        """
    @abc.abstractmethod
    def tr_abort(self, context):
        """
        """
    @abc.abstractmethod
    def tr_complete(self, context):
        """
        """
