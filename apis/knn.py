# coding: utf-8

import os
import sys
module_path = os.path.abspath(os.path.join('..'))
if module_path not in sys.path:
    sys.path.append(module_path)

import logging
from datetime import datetime, timedelta
from flask import Flask, jsonify, request, abort, make_response
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from sklearn.feature_extraction.text import TfidfVectorizer

from models.article import Article

logging.basicConfig(level=logging.INFO)

flask_server = Flask(__name__)

PORT = 8000

class NewsArticleClassifier(object):
    def predict(self, url):
        # Load today's articles from database
        from_date = datetime.today().date()
        to_date = datetime.today().date() + timedelta(days=1)
        articles = Article.load_articles_from_db(from_date, to_date)
        
        test_article = Article(url, '', '', '', datetime.now())
        
        # List of named entities
        named_entities_list = list(map(lambda x: ' '.join(x.named_entities), articles))
        named_entities_list.append(' '.join(test_article.named_entities))
        
        # TF-IDF matrix
        tfidf_vectorizer = TfidfVectorizer()
        tfidf_matrix = tfidf_vectorizer.fit_transform(named_entities_list)
        
        # Fit KNN
        nbrs = NearestNeighbors(n_neighbors=10) 
        nbrs.fit(tfidf_matrix)
        
        # Predict
        test_row = tfidf_matrix.getrow(len(named_entities_list) - 1)
        distances, indices = nbrs.kneighbors(test_row)
        
        # Format predictions
        similar_articles = []
        for idx, val in enumerate(indices.flatten()[1:]):
            article = articles[val]
            distance = distances.flatten()[idx]
            similar_articles.append({
                'distance': distance,
                'title': article.title,
                'url': article.url,
                'description': article.description,
            })
        return similar_articles
     
        

classifier = NewsArticleClassifier()

def _parse_url_params():

    try:
        url = request.args['url']
    except KeyError:
        logging.info('Badly formatted request body: {}'.format(request_body))
        response_body = {
            'error': "Missing 'url' in url params"
        }
        response = make_response(jsonify(response_body), 400)
        abort(response)
    return url

@flask_server.route('/predict', methods=['GET'])
def predict():
    """Respond to requests for a prediction."""
    
    url = _parse_url_params()
    similar_articles = classifier.predict(url)
    return jsonify({ 'similar_articles': similar_articles })

if __name__ == '__main__':
    logging.info('Listening on port {}'.format(PORT))
    flask_server.run(debug=True, host='127.0.0.1', port=PORT)