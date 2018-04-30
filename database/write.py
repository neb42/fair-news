from .connect import connect

def write_article(article_id, url, title, description, source published_at):
    query = f'''
        INSERT INTO articles
        (article_id, url, title, description, source, published_at)
        VALUES ({article_id}, {url}, {title}, {description}, {source}, {published_at});
    '''
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
        conn.commit()
            
def write_named_entities(article_id, named_entities_list):
    named_entities_tuple = tuple(named_entities_list)
    query = f'''
        UPDATE articles
        SET named_entities = {named_entities_tuple}
        WHERE article_id = {article_id}
    '''
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
        conn.commit()
        
def update_cluster(cluster, article_id_list):
    article_id_tuple = tuple(article_id_list)
    query = f'''
        UPDATE articles
        SET cluster = {cluster}
        WHERE article_id in {article_id_tuple}
    '''
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
        conn.commit()