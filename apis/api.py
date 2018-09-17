import logging
from datetime import datetime, timedelta

import pandas as pd
from flask import Flask, jsonify, request, abort, make_response

from classifiers import BiasClassifier, SimilarArticleClassifier
from models.article import Article

logging.basicConfig(level=logging.INFO)

flask_server = Flask(__name__)

PORT = 8000


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
    url = _parse_url_params()
    test_article = Article(url, '', '', '')
    bias_pkl = load_bias_pkl_for_date(test_article.published_at)
    bias_classifier = BiasClassifier(model=bias_pkl)
    // make bias prediction // test_article_bias = ...

    similar_articles_classifier = SimilarArticleClassifier()
    similar_articles = similar_articles_classifier.predict(test_article)

    // make bias prediction // similar_articles_bias = ...

    // decide which articles to return

    return jsonify({})

if __name__ == '__main__':
    logging.info('Listening on port {}'.format(PORT))
    flask_server.run(debug=True, host='127.0.0.1', port=PORT)
