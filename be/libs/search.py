import os
from whoosh.qparser import QueryParser
from whoosh.index import create_in, open_dir
from whoosh.fields import *
from whoosh.qparser import MultifieldParser

indexdir = "indexdir"

member_schema = Schema(id=ID(stored=True, unique=True), username=TEXT(stored=True), display_name=TEXT(stored=True), short_description=TEXT(), long_description=TEXT(), email=TEXT())

mparser = MultifieldParser(["id", "display_name", "username", "short_description", "long_description", "email"], schema=member_schema)

def populate(member_store):
    writer = build_writer()
    print "Populating whoosh..."
    for m in member_store.fetch_all():
        writer.add_document(**member2dict(m))
    writer.commit()
    print "Populating whoosh: Done"

def do_search(qry_text):
    qry_text = unicode(qry_text)
    qry = mparser.parse(qry_text)
    searcher = ix.searcher()
    return [item for item in searcher.search(qry, sortedby="display_name")]

def add(user):
    writer = build_writer()
    try:
        writer.add_document(**member2dict(user))
    except Exception, err:
        writer.commit()
        return False
    writer.commit()
    return True

def update(user):
    writer = build_writer()
    try:
        writer.update_document(**user2dict(user))
        writer.commit()
    except Exception, err:
        writer.commit()
        return False
    return True

def remove(username):
    writer = build_writer()
    writer.delete_by_term("username", username)
    writer.commit()
    return True

def sync():
    User.select()
    raise NotImplemented
    return True

def build_writer():
    return ix.writer()

if not os.path.exists(indexdir):
    os.mkdir(indexdir)
    ix = create_in(indexdir, member_schema)
else:
    ix = open_dir(indexdir)

def stop():
    ix.close()
    ix.unlock()
    print "search shutdown"

if __name__ == '__main__':
    def test():
        def timer(fn, args, n=1):
            import datetime
            start = datetime.datetime.now()
            for x in range(n):
                fn(*args)
            return datetime.datetime.now() - start

        qry_text = "shon"
        print do_search(qry_text)
        N = 1000
        print "whoosh"
        print timer(do_search, [qry_text], N)
