import os
import psycopg2.extras
from newsapi import NewsApiClient

from database.connect import connect

API_KEY = os.environ['API_KEY']

class Source:
    def __init__(
        self,
        source_id,
        name,
        description,
        url,
        language_code,
        country_code,
        bias=None,
        reliability=None,
        id=None
    ):
        self.source_id = source_id
        self.name = name
        self.description = description
        self.url = url
        self.language_code = language_code
        self.country_code = country_code
        self.bias = bias
        self.reliability = reliability
        self.id = id
    
    @staticmethod
    def load_from_db(source_id=None, id=None, country_codes=None):
        if source_id:
            query = f'SELECT * FROM sources WHERE source_id = {source_id};'
            row = cur.fetchone()
            return Source(
                row['source_id'],
                row['name'],
                row['description'],
                row['url'],
                row['language_code'],
                row['country_code'],
                row['bias'],
                row['reliability'],
                row['id']
            )
        elif country_codes:
            raise NotImplementedError
        else:
            query = 'SELECT * FROM sources;'
            sources = []
            with connect() as conn:
                with conn.cursor(cursor_factory = psycopg2.extras.DictCursor) as cur:
                    cur.execute(query)
                    for row in cur:
                        sources.append(Source(
                            row['source_id'],
                            row['name'],
                            row['description'],
                            row['url'],
                            row['language_code'],
                            row['country_code'],
                            row['bias'],
                            row['reliability']
                        ))
            return sources
            
    @staticmethod
    def set_bias(source_biases):
        raise NotImplementedError
    
    @staticmethod
    def set_reliability(source_biases):
        raise NotImplementedError
    
    @staticmethod
    def fetch_from_api():
        newsapi = NewsApiClient(api_key=API_KEY)
        response = newsapi.get_sources()
        if response['status'] != 'ok':
            raise Exception('Error querying news api', response)
        return list(map(lambda x: Source(
            x['id'],            
            x['name'],
            x['description'],
            x['url'],
            x['language'],
            x['country']
        ), response['sources']))
    
    @staticmethod
    def bulk_insert(sources):
        def build_value_str(source):
            source_id = source.source_id
            name = source.name.replace("'", '"')
            description = source.description.replace("'", '"')
            url = source.url
            language_code = source.language_code
            country_code = source.country_code
            return f"('{source_id}', '{name}', '{description}', '{url}', '{language_code}', '{country_code}')"

        values = ', '.join(map(build_value_str, sources))
        query = f'''
            INSERT INTO sources
            (source_id, name, description, url, language_code, country_code)
            VALUES {values};
        '''
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(query)
            conn.commit()