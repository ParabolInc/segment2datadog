import hmac
import hashlib
import logging
import os
from flask import Flask, jsonify, request, abort
from datadog import initialize, api, statsd

# get keys from enfironment variables
SEGMENT_SHARED_SECRET = os.environ['SEGMENT_SHARED_SECRET']
DATADOG_API_KEY = os.environ['DD_API_KEY']
DATADOG_APP_KEY = os.environ['DD_APP_KEY']

# initialize datadog
options = {
    'api_key': DATADOG_API_KEY,
    'app_key': DATADOG_APP_KEY
}
initialize(**options)

app = Flask(__name__)
app.logger.setLevel(logging.INFO)
app.logger.info('event: %r', options)

@app.route('/')
def index():
    app.logger.info('viewed root route')
    return "Segment2Datadog is up and running!"

@app.route('/api/<string:source>', methods=['POST'])
def segment2datadog(source):
    # check signature
    signature = request.headers['x-signature']
    digest = hmac.new(SEGMENT_SHARED_SECRET.encode(), msg=request.data, digestmod=hashlib.sha1).hexdigest()
    if digest != signature:
        abort(403, 'Signature not valid.')
    if not source:
        abort(404, 'Source parameter not present.')
    content = request.get_json(silent=True)
    # increment event counter in datadog
    if content['type'] == 'track':
        app.logger.info(
          '{ event: "%s", userId: "%s" }',
          '-'.join(content['event'].split()),
          content['userId']
        )
        statsd.increment(
          'segment.event',
          tags = [
            'source:' + source,
            'event:' + '-'.join(content['event'].split()),
            'type:' + content['type'],
            'user-id:' + content['userId'].replace('|','_')
          ]
        )
    return jsonify({'source': source, 'data': content})
