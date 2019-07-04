# Each time you run this script (which requires Pattern),
# it collects articles from known sources and their bias,
# and appends to a CSV-file (/data/news1.csv)

import os
import feedparser
import pandas as pd
from faculty import datasets
from urllib.request import urlopen
from pathlib import Path
from datetime import datetime
from bs4 import BeautifulSoup
from requests_html import HTMLSession

# To estimate the level of bias:
# https://mediabiasfactcheck.com
# http://www.fakenewschecker.com

sources = { 
  (4, 'right', 'fake', 'Departed'                  ) : 'http://americansmaga.info/feed/',
  (4, 'right', 'fake', 'Hang The Bankers'          ) : 'http://www.hangthebankers.com/feed/',
  (4, 'right', 'fake', 'News Busters'              ) : 'http://www.newsbusters.org/blog/feed',
  (4, 'right', 'fake', 'Truth Revolt'              ) : 'http://www.truthrevolt.org/rss.xml',
  (4, 'right', 'fake', 'Young Conservatives'       ) : 'http://www.youngcons.com/feed/',
  (4, 'right', 'fake', 'American Free Press'       ) : 'http://americanfreepress.net/feed/',
  (4, 'right', 'fake', 'Liberty Writers News'      ) : 'https://libertywritersnews.com/feed/rss',
  (4, 'right', 'fake', 'Prntly'                    ) : 'http://prntly.com/feed/',
  (3, 'right', 'fake', 'The Federalist Papers'     ) : 'http://thefederalistpapers.org/feed',
  (3, 'right', 'fake', 'BlabberBuzz'               ) : 'http://www.blabber.buzz/politics/conservative?format=feed',
  (3, 'right', 'fake', 'World Net Daily'           ) : 'http://mobile.wnd.com/category/front-page/us/feed/',
  (3, 'right', 'fake', 'Infowars'                  ) : 'http://www.infowars.com/feed/custom_feed_rss',
  (3, 'right', 'fake', 'Freedom Daily'             ) : 'http://freedomdaily.com/feed',
  (2, 'right', 'real', 'Heat Street'               ) : 'https://heatst.com/feed/',
  (2, 'right', 'real', 'Breitbart'                 ) : 'http://feeds.feedburner.com/breitbart',
  (1, 'right', 'real', 'Fox News'                  ) : 'http://feeds.foxnews.com/foxnews/latest',

  (3, 'left' , 'fake', 'Realtime Politics'         ) : 'http://realtimepolitics.com/feed/rss',
  (3, 'left' , 'fake', 'Counter Current News'      ) : 'http://countercurrentnews.com/feed/',
  (2, 'left' , 'real', 'Upworthy'                  ) : 'http://feeds.feedburner.com/upworthy',
  (2, 'left' , 'real', 'Mother Jones'              ) : 'http://www.motherjones.com/rss/blogs_and_articles/feed',
  (2, 'left' , 'real', 'Slate'                     ) : 'http://www.slate.com/all.fulltext.all.rss',
  (2, 'left' , 'real', 'The Hill'                  ) : 'http://thehill.com/rss/syndicator/19110',
  (2, 'left' , 'real', 'Huffington Post'           ) : 'http://www.huffingtonpost.com/feeds/index.xml',
  (1, 'left' , 'real', 'New York Times'            ) : 'http://www.nytimes.com/services/xml/rss/nyt/HomePage.xml',
  (1, 'left' , 'real', 'Washington Post'           ) : 'http://feeds.washingtonpost.com/rss/rss_blogpost',

  (0, ''     , 'real', 'Reuters'                   ) : 'http://feeds.reuters.com/reuters/topNews',
  (0, ''     , 'real', 'USA Today'                 ) : 'http://rssfeeds.usatoday.com/usatoday-NewsTopStories',
  (0, ''     , 'real', 'Financial Times'           ) : 'http://www.ft.com/rss/world',
  (0, ''     , 'real', 'Associated Press'          ) : 'http://hosted2.ap.org/atom/APDEFAULT/3d281c11a96b4ad082fe88aa0db04305',
  (0, ''     , 'real', 'The Diplomat'              ) : 'http://thediplomat.com/feed/',
  (0, ''     , 'real', 'United Press International') : 'http://rss.upi.com/news/news.rss',
  
  (0, ''     , 'joke', 'The Onion'                 ) : 'http://www.theonion.com/feeds/rss',
  (4, 'right', 'joke', 'National Report'           ) : 'http://feeds.feedburner.com/NationalReport',
}

LOCK_FILE = '/project/hourly-homepage-crawler.lock'
DATASETS_ROOT_PATH = '/input/bias-data'
TODAY_STR = datetime.today().strftime('%Y-%m-%d')
TODAY_CSV = f'{DATASETS_ROOT_PATH}/{TODAY_STR}.csv'
TMP_CSV = '/tmp/today.csv'
COLUMNS = [
  'source_name', 
  'source_label',
  'bias', 
  'bias_level', 
  'article_title', 
  'article_content', 
  'article_url', 
]

class FailedToAcquireLockException(Exception):
    pass

def remove_file(filepath):
  if os.path.exists(filepath):
    os.remove(filepath)

def get_lock():
  if os.path.exists(LOCK_FILE):
    print('Failed to acquire lock')
    raise FailedToAcquireLockException
  else:
    print('Acquiring lock')
    Path(LOCK_FILE).touch()

def release_lock():
  print('Releasing lock')
  remove_file(LOCK_FILE)

def get_todays_dataframe():
  if TODAY_CSV in datasets.ls():
    datasets.get(TODAY_CSV, TMP_CSV)
    df = pd.read_csv(TMP_CSV, sep='\t', encoding='utf-8')
    if os.path.exists(TMP_CSV):
      os.remove(TMP_CSV)
    return df
  return None
  
def save_data_frame(df):
  remove_file(TMP_CSV)
  df.to_csv(TMP_CSV, sep='\t', encoding='utf-8', index=False)
  datasets.put(TMP_CSV, TODAY_CSV)

def parse_article(bias_level, bias, source_label, source_name, article_url, article_title):
  try:
    session = HTMLSession()
    response = session.get(article_url)
    soup = BeautifulSoup(response.html.raw_html, 'lxml')
  except Exception as e:
    print('Url Failed: ' + article_url)
    return None
  
  # Find article text with CSS selectors:
  for selector in (
    "article[class*='node-article']",            # The Hill
    "span[itemprop='articleBody']",
    "div[itemprop='articleBody']",
    "div[id='rcs-articleContent'] .column1", # Reuters
    "div[class='story-body']",
    "div[class='article-body']",
    "div[class='article-content']",
    "div[class^='tg-article-page']",
    "div[class^='newsArticle']",
    "div[class^='article-']",
    "div[class^='article_']",
    "div[class*='article']",
    "div[id*='storyBody']",                  # Associated Press
    "article",
    ".story",
  ):
    element = soup.find(selector)
    if element is None or len(element) == 0:
      continue
    
    for bad_tag in (
      "div[id='rightcolumn']",
      "div[id='rightcolumn']",
      "div[class='blog-sidebar-links']",
      "div[class='blog-sidebar-links']",
    ):
      try:
        [s.extract() for s in element.select(bad_tag)]
      except:
        continue
      
      [s.extract() for s in element.findAll('script')]
    
    try:
      article_content = element.text.strip()
    except Exception as e:
      print(e)
      continue
  
    #if article_url not in df.article_url.unique():
    row = {
      'source_name': source_name,
      'source_label': source_label,
      'bias': bias,
      'bias_level': bias_level,
      'article_title': '',
      'article_content': article_content,
      'article_url': article_url,
      'article_title': article_title,
    }
    return row
  # print('Failed to find content for ' + article_url)
  
def parse_source(bias_level, bias, source_label, source_name, source_url):
  try:
    feed = feedparser.parse(source_url)
  except Exception as e:
    print('Failed source: ' + source_name + ' ' + source_url)
    return []
  
  print('Parsing ' + str(len(feed['items'])) + ' articles for source ' + source_name)
  rows = []
  for article in feed['items']:
    rows.append(
      parse_article(bias_level, bias, source_label, source_name, article['link'], article['title'])
    )

  print('Successfully parsed ' + str(len(rows)) + ' articles for source ' + source_name)
  return rows
    
if __name__ == '__main__':
  print(datetime.now())
  get_lock()
  try:
    existing_df = get_todays_dataframe()
    rows = []
    for (bias_level, bias, source_label, source_name), source_url in sources.items():
      rows += parse_source(bias_level, bias, source_label, source_name, source_url)
    rows = [r for r in rows if r is not None]
    print('Successfully parsed ' + str(len(rows)) + ' articles')
    new_df = pd.DataFrame(rows)
    if existing_df is not None:
      merged_df = pd.concat([existing_df, new_df]).drop_duplicates(subset='article_url').reset_index(drop=True)
      print('Saving dataframe with shape: ' + str(merged_df.shape))
      save_data_frame(merged_df)
    else:
      print('Saving dataframe with shape: ' + str(new_df.shape))
      save_data_frame(new_df)
  finally:
    release_lock()