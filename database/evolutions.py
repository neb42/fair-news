from .connect import connect

def setup():
    queries = [
        '''CREATE TABLE articles (
            article_id UUID PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            source TEXT NOT NULL,
            url TEXT NOT NULL,
            published_at DATE NOT NULL,
            named_entities TEXT[] DEFAULT NULL
        );''',
    ]
    with connect() as conn:
        with conn.cursor() as cur:
            for query in queries:
                cur.execute(query)
        conn.commit()

def tear_down():
    queries = [
        'DROP TABLE articles;',
    ]
    with connect() as conn:
        with conn.cursor() as cur:
            for query in queries:
                cur.execute(query)
        conn.commit()