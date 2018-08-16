import os
import uuid
from goose3 import Goose
from nltk import ne_chunk, pos_tag, word_tokenize
from nltk.tree import Tree
from newsapi import NewsApiClient
from multiprocessing import Process, Queue
from dateutil import parser
import psycopg2.extras

from database.connect import connect

CORES = int(os.environ['NUM_CPUS'])
API_KEY = os.environ['API_KEY']
PAGE_SIZE = int(os.environ['PAGE_SIZE'])
NEWS_SOURCES = os.environ['NEWS_SOURCES'].split(' ')

goose = Goose()

class Article:
    def __init__(
        self,
        url, 
        title,
        description,
        source_id,
        published_at,
        article_uuid=None,
        named_entities=None,
        id=None,
        raw_content=None
    ):
        self.url = url
        self.title = title
        self.description = description
        self.source_id = source_id
        self.article_uuid = article_uuid or uuid.uuid4()
        self.id = id

        if type(published_at) is str:
            self.published_at = parser.parse(published_at)
        else:
            self.published_at = published_at

        if named_entities:
            self.named_entities = named_entities
        else:
            self.raw_content = goose.extract(url=url).cleaned_text
            self.named_entities = self.extract_named_entities(self.raw_content)
        
    def extract_named_entities(self, text):
        chunked = ne_chunk(pos_tag(word_tokenize(text)))
        prev = None
        continuous_chunk = []
        current_chunk = []
        for i in chunked:
            if type(i) == Tree:
                current_chunk.append(" ".join([token for token, pos in i.leaves()]))
            elif current_chunk:
                named_entity = " ".join(current_chunk)
                if named_entity not in continuous_chunk:
                    continuous_chunk.append(named_entity)
                    current_chunk = []
                else:
                    continue
        return continuous_chunk
        
    @staticmethod
    def build_articles(raw_articles, sequential=False):
        def single_core_article_builder():
            articles = []
        
            for a in raw_articles:
                try:
                    articles.append(Article(
                        a.url,
                        a.title,
                        a.description,
                        a.source_id,
                        a.published_at,
                    ))
                except Exception as e:
                    continue
            return articles
        
        def multi_core_article_builder():
            def doWork(q, a):
                results = []
                errors = []
                for article in a:
                    try:
                        results.append(Article(
                            article.url,
                            article.title,
                            article.description,
                            article.source_id,
                            article.published_at,
                        ))
                    except Exception as e:
                        continue
                q.put(results)
                
            q = Queue()
            subprocesses = []
            for i in range(CORES):
                start = int(i * (len(raw_articles)/CORES))
                end = int((i + 1) * (len(raw_articles)/CORES))
                p = Process(target=doWork, args=(q, raw_articles[start:end]))
                p.start()
                subprocesses.append(p)
        
            articles = []
            for i in range(CORES):
                articles.extend(q.get(True))
            while subprocesses:
                subprocesses.pop().join()
            return articles
        
    
        if not sequential and CORES > 1:
            print(f'Running on {CORES} cores')
            articles = multi_core_article_builder()
        else:
            print('Running on single core')
            articles = single_core_article_builder()
        print('Finished building articles')
        return articles
        
    @staticmethod
    def load_articles_from_db(from_date=None, to_date=None):
        query = 'SELECT * FROM articles'
        if from_date or to_date:
            query += ' WHERE'
        if from_date:
            query += f" published_at >= '{from_date}'"
            if to_date:
                query += ' AND'
        if to_date:
            query += f" published_at < '{to_date}'"
        print(query)
        articles = []
        with connect() as conn:
            with conn.cursor(cursor_factory = psycopg2.extras.DictCursor) as cur:
                cur.execute(query)
                for row in cur:
                    articles.append(Article(
                        row['url'],
                        row['title'],
                        row['description'],
                        row['source_id'],
                        row['published_at'],
                        row['article_uuid'],
                        row['named_entities'],
                        row['id'],
                    ))
        return articles

    @staticmethod
    def bulk_insert(articles):
        def build_value_str(article):
            if not article.description or not article.title or len(article.named_entities) == 0:
                print(article.url)
                return None
            url = article.url
            title = article.title.replace("'", '"')
            description = article.description.replace("'", '"')
            source_id = article.source_id
            published_at = article.published_at
            article_uuid = article.article_uuid
            foo = "','".join(map(lambda x: x.replace("'", '"'), article.named_entities))
            named_entities = f"ARRAY['{foo}']"
            return f"('{url}', '{title}', '{description}', '{source_id}', '{published_at}', '{article_uuid}', {named_entities})"
        value_strings_with_none = map(build_value_str, articles)
        value_strings = [x for x in value_strings_with_none if x is not None]
        values = ', '.join(value_strings)
        query = f'''
            INSERT INTO articles
            (url, title, description, source_id, published_at, article_uuid, named_entities)
            VALUES {values};
        '''
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(query)
            conn.commit()