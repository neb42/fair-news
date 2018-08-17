import os
import sys

module_path = os.path.abspath(os.path.join('../..'))
if module_path not in sys.path:
    sys.path.append(module_path)

import logging
from flask import Flask, send_from_directory
from datetime import datetime, timedelta
from flask import Flask, jsonify, request, abort, make_response

from models.source import Source
from models.source_bias import SourceBias

logging.basicConfig(level=logging.INFO)

PORT = 8000

app = Flask(__name__, static_folder='build')

@app.route('/api/source', methods=['GET'])
def get_source_list():
    sources = Source.load_from_db()
    return jsonify({ 'sources': list(map(lambda x: {
        'sourceId': x.source_id,
        'name': x.name,
        'description': x.description,
        'url': x.url,
        'languageCode': x.language_code,
        'countryCode': x.country_code,
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
    return political_bias, reliability

@app.route('/api/source/<source_id>/bias', methods=['POST'])
def submit_source_bias(source_id):
    political_bias, reliability = _parse_request_body()
    if request.headers.get("X-Forwarded-For"):
      ip = request.headers.get("X-Forwarded-For").split(', ')[0]
    else:
      ip = request.remote_addr
    logging.info('Submitting bias: source {}, ip {}, pb {}, rel {}'.format(source_id, ip, political_bias, reliability))
    SourceBias.insert_row(SourceBias(source_id, ip, political_bias, reliability))
    return ('', 204)

# Serve React App
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists('build/' + path):
        return send_from_directory('build', path)
    else:
        return send_from_directory('build', 'index.html')


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=PORT)