# coding: utf-8

import logging
from datetime import datetime, timedelta
from flask import Flask, jsonify, request, abort, make_response

from models.source import Source
from models.source_bias import SourceBias

logging.basicConfig(level=logging.INFO)

flask_server = Flask(__name__)

PORT = 8000

@flask_server.route('/source', methods=['GET'])
def get_sources():
    sources = Source.load_from_db()
    return jsonify({ 'sources': list(map(lambda x: {
        'source_id': x.source_id,
        'name': x.name,
        'description': x.description,
        'url': x.url,
        'language_code': x.language_code,
        'country_code': x.country_code,
    }, sources)) })


def _parse_request_body():
    request_body = request.get_json(force=True)
    try:
        political_bias = request_body['politicalBias']
        reliability = request_body['reliability']
    except KeyError:
        logging.info('Badly formatted request body: {}'.format(request_body))
        response_body = {
            'error': "Missing 'politicalBias' or 'reliability' key in request body"
        }
        response = make_response(jsonify(response_body), 400)
        abort(response)
    return politicalBias, reliability


@flask_server.route('/source/<source_id>', methods=['POST'])
def create_source_bias(source_id):
    political_bias, reliability = _parse_request_body()
    SourceBias.insert_row(SourceBias(source_id, request.remote_addr, political_bias, reliability))
    return ('', 201)

if __name__ == '__main__':
    logging.info('Listening on port {}'.format(PORT))
    flask_server.run(debug=True, host='127.0.0.1', port=PORT)