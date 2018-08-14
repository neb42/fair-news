from .connect import connect

def setup():
    queries = [
        'CREATE SEQUENCE sources_id_seq;',
        '''CREATE TABLE sources (
            id BIGINT DEFAULT NEXTVAL('sources_id_seq') CONSTRAINT sources_id_seq_pkey PRIMARY KEY,
            source_id TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            url TEXT NOT NULL,
            language_code TEXT NOT NULL,
            country_code TEXT NOT NULL,
            bias TEXT DEFAULT NULL,
            reliability TEXT DEFAULT NULL
        );''',
        'CREATE SEQUENCE source_bias_id_seq;',
        '''CREATE TABLE source_bias (
            id BIGINT DEFAULT NEXTVAL('source_bias_id_seq') CONSTRAINT source_bias_id_seq_pkey PRIMARY KEY,
            source_id TEXT NOT NULL,
            ip_address TEXT NOT NULL,
            political_bias TEXT NOT NULL,
            reliability TEXT NOT NULL,
            CONSTRAINT source_bias_sources_id_fkey FOREIGN KEY (source_id) REFERENCES sources(source_id) ON DELETE CASCADE
        );''',
        'CREATE SEQUENCE articles_id_seq;',
        '''CREATE TABLE articles (
            id BIGINT DEFAULT NEXTVAL('articles_id_seq') CONSTRAINT articles_id_seq_pkey PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            source_id TEXT NOT NULL,
            url TEXT NOT NULL,
            published_at DATE NOT NULL,
            named_entities TEXT[] DEFAULT NULL,
            CONSTRAINT articles_sources_id_fkey FOREIGN KEY (source_id) REFERENCES sources(source_id) ON DELETE CASCADE
        );''',
    ]
    with connect() as conn:
        with conn.cursor() as cur:
            for query in queries:
                cur.execute(query)
        conn.commit()

def tear_down():
    queries = [
        'DROP TABLE IF EXISTS articles;',
        'DROP SEQUENCE IF EXISTS articles_id_seq;',
        'DROP TABLE IF EXISTS source_bias;',
        'DROP SEQUENCE IF EXISTS source_bias_id_seq;',
        'DROP TABLE IF EXISTS sources;',
        'DROP SEQUENCE IF EXISTS sources_id_seq;',
    ]
    with connect() as conn:
        with conn.cursor() as cur:
            for query in queries:
                cur.execute(query)
        conn.commit()