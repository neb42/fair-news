import os
import sys
module_path = os.path.abspath(os.path.join('..'))
if module_path not in sys.path:
    sys.path.append(module_path)
if '/project/fair-news' not in sys.path:
    sys.path.append('/project/fair-news')

import tempfile
import pandas as pd
import sherlockml.filesystem as sfs
from datetime import datetime, timedelta

from models.article import Article
from models.raw_article import RawArticle

# Setup dates
from_date = datetime.today().date() - timedelta(days=1)
to_date = datetime.today().date()

# Fetch raw articles
raw_articles = RawArticle.get_raw_articles(
    from_date.strftime('%Y-%m-%d'),
    to_date.strftime('%Y-%m-%d')
)

# Build articles and insert into database
articles = Article.build_articles(raw_articles)
Article.bulk_insert(articles)

# Store raw article content in datasets for later analysis
df = pd.DataFrame.from_records(
    [{ 'title': x.title, 'raw_content': x.raw_content, 'article_uuid': x.article_uuid } for x in articles if x.title is not None and x.description is not None]
)
tmp = tempfile.NamedTemporaryFile()
with open(tmp.name, 'w') as f:
    df.to_csv(tmp.name, sep='\t', encoding='utf-8')
date_str = from_date.strftime('%Y-%m-%d')
sfs.put(tmp.name, f'/input/article_content/{date_str}.csv')