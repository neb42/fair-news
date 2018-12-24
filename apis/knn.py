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
from sherlockml.datasets.session import SherlockMLDatasetsError

from models.article import Article

logging.basicConfig(level=logging.INFO)

flask_server = Flask(__name__)

PORT = 8000

class BaseException(Exception):
    def __init__(self, message=None, status_code=None, payload=None):
        Exception.__init__(self)
        if message is not None:
            self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv

class BadlyFormattedRequestBody(BaseException):
    status_code = 400
    message = ''

class NoNamedEntities(BaseException):
    status_code = 400
    message = ''

class NoArticlesFound(BaseException):
    status_code = 404
    message = ''

@flask_server.errorhandler(BadlyFormattedRequestBody)
def handle_badly_formatted_request_body(error):
    return handle_custom_exception(error)

@flask_server.errorhandler(NoNamedEntities)
def handle_no_named_entities(error):
    return handle_custom_exception(error)

@flask_server.errorhandler(NoArticlesFound)
def handle_no_articles_found(error):
    return handle_custom_exception(error)

def handle_custom_exception(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

class NewsArticleClassifier(object):
    def predict(self, url):
        # TODO: url results can be cached
        # Get named entities for requested url
        test_article = Article(url, '', '', '')

        # Return an error if no named entities were found
        if len(test_article.named_entities) == 0:
            raise NoNamedEntities()

        # TODO: Add some caching for this
        # Fetch articles with the same publish date
        try:
            articles = Article.load_articles_from_datasets(
                test_article.published_at.strftime('%Y-%m-%d')
            )
        except SherlockMLDatasetsError:
            raise NoArticlesFound()

        # Return an error if no articles were found for the published date
        if len(articles) == 0:
            raise NoArticlesFound()

        # List of named entities
        named_entities_list = list(map(lambda x: ' '.join(x.named_entities), articles))
        named_entities_list.append(' '.join(test_article.named_entities))

        # TF-IDF matrix
        tfidf_vectorizer = TfidfVectorizer()
        tfidf_matrix = tfidf_vectorizer.fit_transform(named_entities_list)

        # Fit KNN
        nbrs = NearestNeighbors(n_neighbors=20)
        nbrs.fit(tfidf_matrix)

        # Predict
        test_row = tfidf_matrix.getrow(len(named_entities_list) - 1)
        distances, indices = nbrs.kneighbors(test_row)

        # Format predictions
        similar_articles = {
            'left': None,
            'center': None,
            'right': None,
        }
        for idx, val in enumerate(indices.flatten()[1:]):
            if val == len(articles):
                continue

            article = articles[val]

            if article.url == test_article.url or len(article.named_entities) == 0:
                continue

            distance = distances.flatten()[idx]
            bias = article.bias
            article_json = {
                'distance': distance,
                'title': article.title,
                'url': article.url,
                'description': article.description,
                'source_id': article.source_id,
                'named_entities': article.named_entities,
            }

            if bias == 1:
                current_left = similar_articles['left']
                if current_left is None or distance < current_left['distance']:
                    similar_articles['left'] = article_json
            elif bias == 0:
                current_center = similar_articles['center']
                if current_center is None or distance < current_center['distance']:
                    similar_articles['center'] = article_json
            elif bias == -1:
                current_right = similar_articles['right']
                if current_right is None or distance < current_right['distance']:
                    similar_articles['right'] = article_json

        return similar_articles


classifier = NewsArticleClassifier()

def _parse_url_params():
    try:
        url = request.args['url']
    except KeyError:
        logging.info('Badly formatted request body: {}'.format(request_body))
        raise BadlyFormattedRequestBody()
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
