from flask import Flask, request, Response
import requests
from requests.models import HTTPError
import re
import json
import os
import logging

app = Flask(__name__)
logs_api_endpoint = os.environ.get('LOGS_API_ENDPOINT')

# New Relic Logs API
class HeaderlessLogAPI:

    def __init__(self, endpoint) -> None:
        self.endpoint = endpoint
    
    # Send message to Logs API endpoint
    def send_message(self, data):
        try:
            print(f"headerlessLogAPI send_message")
            # Decode data
            decoded_data = data.decode('utf8').replace("'", '"')

            # Retrieve JSON object from incoming data
            json_data = re.search('{(.*)}', decoded_data)
            json_string = "{" + json_data.group(1)+ "}"
            json_object = json.loads(json_string)

            # Send retrieved JSON with POST request to Logs API endpoint
            repsonse = requests.post(url=self.endpoint, json=json_object)

            # Print response
            print(f"headerlessLogAPI response status code: {repsonse.status_code}")
            print(f"headerlessLogAPI response text: {repsonse.text}")
        except HTTPError as e:
            # Print error
            print(e)

@app.route('/')
def index():
    return 'Welcome to logs forwarder!'

@app.route('/logs', methods=['POST'])
def send_logs():
    app.logger.info(f"Incoming data: {request.data}")
    return Response(status=200)

# Set Logging
if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

if __name__ == '__main__':
    logs_api = HeaderlessLogAPI(endpoint=logs_api_endpoint)
    app.run(host='127.0.0.1', debug=True)