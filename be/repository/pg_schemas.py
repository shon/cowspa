import cPickle
import psycopg2

import shared
from commonlib.helpers import odict

constants = shared.constants

class Model(object):
    auto_id = False
    schema = {}
    @classmethod
    def check_tablename(self):
        if not hasattr(self, 'table_name'):
            self.table_name = self.__name__.lower()
    @classmethod
    def create_table(self, cur):
        q = "CREATE TABLE %(table_name)s (%(sql)s)" % dict(table_name=self.table_name, sql=self.create_sql)
        try:
            cur.execute(q)
        except psycopg2.ProgrammingError:
            print q
            raise
    @classmethod
    def load_schema(self, cur):
        self.check_tablename()
        q = "select 1 from information_schema.tables where table_name = %s"
        cur.execute(q, (self.table_name,))
        if not cur.fetchone():
            self.create_table(cur)
        q = "select column_name, column_default, character_maximum_length from INFORMATION_SCHEMA.COLUMNS where table_name=%s"
        cur.execute(q, (self.table_name,))
        cols = cur.fetchall()
        schema = {}
        for name, column_default, max_len in cols:
            schema[name] = odict(name=name, max_len=max_len)
            if name == 'id' and column_default == "nextval('%s_id_seq'::regclass)" % self.table_name:
                self.auto_id = True
        self.schema = schema

class User(Model):
    table_name = "account"
    create_sql = """
    id SERIAL NOT NULL UNIQUE,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    enabled boolean default true NOT NULL
    """

class Contact(Model):
    table_name = "contact"
    create_sql = """
    id SERIAL NOT NULL UNIQUE,
    owner TEXT NOT NULL,
    address TEXT,
    city TEXT,
    country TEXT,
    pincode TEXT,
    homephone TEXT,
    mobile TEXT,
    fax TEXT,
    email TEXT NOT NULL,
    skype TEXT,
    sip TEXT
    """

class MemberPref(Model):
    table_name = "member_pref"
    create_sql = """
    member INTEGER NOT NULL,
    theme TEXT DEFAULT 'default',
    language TEXT DEFAULT 'en'
    """

class MemberServices(Model):
    table_name = "member_service"
    create_sql = """
    member TEXT NOT NULL,
    webpage boolean default false NOT NULL
    """

#class MemberProfileSecurity(Model):
#    #membership_id = IntegerField(required=True)
#    property_name = Attribute(required=True)
#    #level = ListField(required=True) # 0 off 1 on: [anonymous access][all locations][same location][private]

class MemberProfile(Model):
    table_name = "member_profile"
    create_sql = """
    member INTEGER NOT NULL,
    first_name TEXT NOT NULL,
    last_name TEXT,
    display_name TEXT,
    short_description TEXT,
    long_description TEXT,
    interests TEXT[],
    expertise TEXT[],
    website TEXT,
    blog TEXT,
    twitter TEXT[2],
    facebook TEXT[2],
    linkedin TEXT[2],
    use_gravtar boolean default false
    """

# Container objects
class Member(Model):
    table_name = "member"
    create_sql = """
    id INTEGER NOT NULL,
    contact INTEGER NOT NULL,
    created TIMESTAMP WITHOUT TIME ZONE NOT NULL
    """

class Registered(Model):
    create_sql = """
    id SERIAL NOT NULL UNIQUE,
    activation_key TEXT NOT NULL,
    first_name TEXT NOT NULL,
    last_name TEXT,
    email TEXT NOT NULL,
    ipaddr inet
    """

class Session(Model):
    create_sql = """
    token TEXT NOT NULL,
    user_id integer NOT NULL UNIQUE,
    created TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    last_seen TIMESTAMP WITHOUT TIME ZONE
    """

class Permission(Model):
    table_name = "permission"
    create_sql = """
    id SERIAL NOT NULL UNIQUE,
    name TEXT NOT NULL UNIQUE,
    label TEXT,
    description TEXT
    """

class Role(Model):
    table_name = "role"
    create_sql = """
    id SERIAL NOT NULL UNIQUE,
    name TEXT NOT NULL UNIQUE,
    label TEXT,
    description TEXT,
    permissions smallint[] NOT NULL
    """

class UserRole(Model):
    create_sql = """
    user_id integer NOT NULL,
    role_id TEXT NOT NULL
    """

class UserPermission(Model):
    create_sql = """
    user_id integer NOT NULL,
    permission_id TEXT NOT NULL
    """

class BizProfile(Model):
    create_sql = """
    short_description TEXT,
    long_description TEXT,
    tags TEXT[],
    website TEXT,
    blog TEXT,
    twitter TEXT[2],
    facebook TEXT[2],
    linkedin TEXT[2]
    """

class BizplaceProfile(Model):
    create_sql = """
    short_description TEXT,
    long_description TEXT,
    tags TEXT[],
    website TEXT,
    blog TEXT,
    twitter TEXT[2],
    facebook TEXT[2],
    linkedin TEXT[2]
    """

#class BizInvoicingPref(Model):
#    invoice_logo = Attribute()
#
class Biz(Model):
    create_sql = """
    id SERIAL NOT NULL UNIQUE,
    name TEXT NOT NULL,
    enabled boolean default true NOT NULL,
    created TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    logo TEXT,
    contact INTEGER
    """

class BizPlace(Model):
    create_sql = """
    id SERIAL NOT NULL UNIQUE,
    name TEXT NOT NULL,
    enabled boolean default true NOT NULL,
    created TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    contact INTEGER,
    langs TEXT[],
    tz TEXT,
    holidays smallint[],
    biz TEXT
    """

class Request(Model):
    create_sql = """
    id SERIAL NOT NULL UNIQUE,
    name TEXT NOT NULL,
    created TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    acted_at TIMESTAMP WITHOUT TIME ZONE,
    requestor_id integer,
    request_note TEXT,
    status smallint default 0 NOT NULL,
    approver_id integer,
    approver_perm TEXT NOT NULL,
    _req_data bytea
    """

class Plan(Model):
    create_sql = """
    id SERIAL NOT NULL UNIQUE,
    name TEXT NOT NULL,
    bizplace_id integer NOT NULL,
    description TEXT,
    enabled boolean default true NOT NULL,
    created TIMESTAMP WITHOUT TIME ZONE NOT NULL
    """

class PlanSubscribers(Model):
    create_sql = """
    subscriber_id integer,
    plan_id integer
    """

#class Activity(Model):
#    name = Attribute(required=True)
#    created = DateTimeField(auto_now_add=False)
