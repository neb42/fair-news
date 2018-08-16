import os
import sys
module_path = os.path.abspath(os.path.join('..'))
if module_path not in sys.path:
    sys.path.append(module_path)
if '/project/fair-news' not in sys.path:
    sys.path.append('/project/fair-news')

import tempfile
import sherlockml.filesystem as sfs
from datetime import datetime, timedelta

from models.article import Article
from models.raw_article import RawArticle

from_date = datetime.today().date() - timedelta(days=2)
to_date = datetime.today().date() - timedelta(days=1)

raw_articles = RawArticle.get_raw_articles(
    from_date.strftime('%Y-%m-%d'),
    to_date.strftime('%Y-%m-%d')
)
articles = Article.build_articles(raw_articles)
Article.bulk_insert(articles)

for article in articles:
    tmp = tempfile.NamedTemporaryFile()
    with open(tmp.name, 'w') as f:
        f.write(article.raw_content)
    sfs.put(tmp.name, f'/input/article_content/{article.article_uuid}')
    print(article.raw_content)
