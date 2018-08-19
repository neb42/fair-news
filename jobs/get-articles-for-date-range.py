import os
import sys
module_path = os.path.abspath(os.path.join('..'))
if module_path not in sys.path:
  sys.path.append(module_path)
if '/project/fair-news' not in sys.path:
  sys.path.append('/project/fair-news')

import tempfile
import click
import pandas as pd
import sherlockml.filesystem as sfs
from dateutil import parser
from datetime import datetime, timedelta

from models.article import Article
from models.raw_article import RawArticle

# Setup dates
from_date = datetime.today().date() - timedelta(days=1)
to_date = datetime.today().date()

def fetch_and_save_articles_in_date_range(from_date, to_date):
  # Fetch raw articles
  raw_articles = RawArticle.get_raw_articles(
    from_date.strftime('%Y-%m-%d'),
    to_date.strftime('%Y-%m-%d')
  )
  
  # Build articles and insert into database
  articles = Article.build_articles(raw_articles)
  # Article.bulk_insert(articles)
  
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
  tmp = tempfile.NamedTemporaryFile()
  with open(tmp.name, 'w') as f:
    df.to_csv(tmp.name, sep='\t', encoding='utf-8', index=False)
  date_str = from_date.strftime('%Y-%m-%d')
  sfs.put(tmp.name, f'/input/article_content/{date_str}.csv')
  
def split_date_range_into_days(from_date, to_date):
  start_dates = [from_date.date()]
  while start_dates[-1] + timedelta(days=1) < to_date.date():
    start_dates.append(start_dates[-1] + timedelta(days=1))
  return start_dates


@click.command()
@click.option('--fromm')
@click.option('--to')
def main(fromm, to):
  from_date = parser.parse(fromm)
  to_date = parser.parse(to)
  start_dates = split_date_range_into_days(from_date, to_date)
  for start_date in start_dates:
    print(start_date)
    fetch_and_save_articles_in_date_range(start_date, start_date + timedelta(days=1))

if __name__ == "__main__":
  main()