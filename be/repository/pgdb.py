import psycopg2
import psycopg2.pool
import bases.persistence as persistence

pool = None

class Provider(persistence.DBProvider):
    def tr_start(self, context):
        conn = pool.getconn()
        context.db = conn.cursor()

    def tr_complete(self, context):
        cur = context.db
        cur.connection.commit()
        pool.putconn(cur.connection)

    def tr_abort(self, context):
        cur = context.db
        cur.execute('abort')

    def startup(self):
        global pool
        pool = psycopg2.pool.SimpleConnectionPool(5, 5, "dbname=shon")

    def shutdown(self):
        pool.close_all()

provider = Provider()
