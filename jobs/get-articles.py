import os
import sys
module_path = os.path.abspath(os.path.join('..'))
if module_path not in sys.path:
    sys.path.append(module_path)
if '/project/fair-news' not in sys.path:
    sys.path.append('/project/fair-news')

import tempfile
import argparse
import pandas as pd
from sherlockml import datasets
from datetime import datetime, timedelta

from models.article import Article
from models.raw_article import RawArticle

def fetch_articles_for_date(date_to_parse):
    from_date = date_to_parse
    to_date = date_to_parse + timedelta(days=1)
    
    # Fetch raw articles
    raw_articles = RawArticle.get_raw_articles(
        from_date.strftime('%Y-%m-%d'),
        to_date.strftime('%Y-%m-%d')
    )
    
    # Build articles and insert into database
    articles = Article.build_articles(raw_articles)
    
    return articles
  
   
def build_dataframe(articles):
    # Store raw article content in datasets for later analysis
    df = pd.DataFrame.from_records(
        [{
            'article_title': x.title,
            'article_uuid': x.article_uuid, 
            'article_url': x.url,
            'article_description': x.description,
            'source_id': x.source_id,
            'published_at': x.published_at,
            'named_entities': x.named_entities,
            'raw_content': x.raw_content,
        } for x in articles if x.title is not None and x.description is not None]
    ).drop_duplicates(subset='article_url').reset_index(drop=True)
    return df
    
    
def save_dataframe_to_datasets(df, parsed_date):
    tmp = tempfile.NamedTemporaryFile()
    with open(tmp.name, 'w') as f:
        df.to_csv(tmp.name, sep='\t', encoding='utf-8', index=False)
    date_str = parsed_date.strftime('%Y-%m-%d')
    datasets.put(tmp.name, f'/input/article_content/{date_str}.csv')
 
    
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "date_keyword", choices=[ 'today', 'yesterday' ], type=str, help=""
    )
    args = parser.parse_args()
    if args.date_keyword == 'today':
        date_to_parse = datetime.today().date()
    elif args.date_keyword == 'yesterday':
        date_to_parse = datetime.today().date() - timedelta(days=1)

    articles = fetch_articles_for_date(date_to_parse)
    df = build_dataframe(articles)
    save_dataframe_to_datasets(df, date_to_parse)

if __name__ == "__main__":
  main()