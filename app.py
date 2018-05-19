import hmac
import hashlib
import os
from flask import Flask, jsonify, request, abort
from datadog import initialize, api, statsd

# get keys from enfironment variables
SEGMENT_SHARED_SECRET = os.environ['SEGMENT_SHARED_SECRET']

# initialize datadog
options = {
    'statsd_host': os.getenv('DATADOG_STATSD_HOST', None)
}

initialize(**options)

app = Flask(__name__)

@app.route('/')
def index():
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
        statsd.increment('segment.event', tags = ['source:' + source, 'event:' + '-'.join(content['event'].split()), 'type:' + content['type']])
    return jsonify({'source': source, 'data': content})
