import psycopg2.extras

from database.connect import connect

class SourceBias:
    def __init__(
        self,
        source_id,
        ip_address,
        political_bias,
        reliability
    ):
        self.source_id = source_id
        self.ip_address = ip_address
        self.political_bias = political_bias
        self.reliability = reliability
        
    @staticmethod
    def load_from_db(source_id=None):
        query = 'SELECT * FROM source_bias'
        if source_id:
            query += f' WHERE source_id={source_id}'
            
        source_biases = []
        with connect() as conn:
            with conn.cursor(cursor_factory = psycopg2.extras.DictCursor) as cur:
                cur.execute(query)
                for row in cur:
                    source_biases.append(SourceBias(
                        row['source_id'],
                        row['ip_address'],
                        row['political_bias'],
                        row['reliability']
                    ))
        return source_biases
        
    @staticmethod
    def insert_row(source_bias):
        query = f'''
            INSERT INTO source_bias
            (source_id, ip_address, political_bias, reliability)
            VALUES ('{source_bias.source_id}', '{source_bias.ip_address}', '{source_bias.political_bias}', '{source_bias.reliability}');
        '''
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(query)
            conn.commit()