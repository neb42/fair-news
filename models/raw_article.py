import os
import uuid
from goose3 import Goose
from nltk import ne_chunk, pos_tag, word_tokenize
from nltk.tree import Tree
from newsapi import NewsApiClient
from multiprocessing import Process, Queue

from database.connect import connect

CORES = int(os.environ['NUM_CPUS'])
API_KEY = os.environ['API_KEY']
PAGE_SIZE = int(os.environ['PAGE_SIZE'])
NEWS_SOURCES = os.environ['NEWS_SOURCES'].split(' ')

goose = Goose()

class RawArticle:
    def __init__(
        self,
        url, 
        title,
        description,
        source,
        published_at,
    ):
        self.url = url
        self.title = title
        self.description = description
        self.source = source,
        self.published_at = published_at

        
    @staticmethod
    def get_raw_articles(from_date, to_date):
        page = 1
        raw_articles = []
        newsapi = NewsApiClient(api_key=API_KEY)
        while True:
            response = newsapi.get_everything(
                sources=','.join(NEWS_SOURCES),
                from_param=from_date,
                to=to_date,
                language='en',
                sort_by='publishedAt',
                page=page,
                page_size=PAGE_SIZE,
            )
            if response['status'] != 'ok':
                raise Exception('Error querying news api', response)
            raw_articles += response['articles']
            if PAGE_SIZE * page >= response['totalResults']:
                break;
            page += 1
        return list(map(lambda x: RawArticle(
            x['url'],
            x['title'],
            x['description'],
            x['source']['id'],
            x['publishedAt']
        ), raw_articles))
 
