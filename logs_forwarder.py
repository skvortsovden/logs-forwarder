from flask import Flask, request, Response
import requests
from requests.models import HTTPError
import re
import json
import os
import logging

app = Flask(__name__)
logs_api_endpoints = os.environ.get('LOGS_API_ENDPOINTS')

# New Relic Logs API
class HeaderlessLogAPI:

    def __init__(self) -> None:
        self.endpoint = None
    
    # Send message to Logs API endpoint
    def send_message(self, data):

            print(f"headerlessLogAPI send_message")
            # Decode data
            decoded_data = data.decode('utf8')

            for line in decoded_data.split('\\n'):
                # Retrieve JSON object from incoming data
                json_data = re.search('{(.*)}', line)
                json_string = "{" + json_data.group(1)+ "}"
                json_object = json.loads(json_string)
                app.logger.info(f"Outcoming data: {json_object}")

                # Get API endpoint for incoming data entity
                if logs_api_endpoints:
                    logs_api_endpoints_json = json.loads(logs_api_endpoints)
                    for key, value in logs_api_endpoints_json.items():
                        if key == json_object['entity.name']:
                            logs_api_endpoint = value
                    # Send retrieved JSON with POST request to Logs API endpoint
                    app.logger.info(f"Sending data to New Relic for entity: {json_object['entity.name']}")
                    try:
                        repsonse = requests.post(url=logs_api_endpoint, json=json_object)
                        # Print response
                        app.logger.info(f"New Relic Log API response status code: {repsonse.status_code}")
                        app.logger.info(f"New Relic Log API response text: {repsonse.text}")
                    except HTTPError as e:
                        # Print error
                        print(e)
                else:
                    app.logger.info(f"Endpoint NOT_FOUND for: {json_object['entity.name']}")


@app.route('/')
def index():
    return 'Welcome to logs forwarder!'

@app.route('/logs', methods=['POST'])
def send_logs():
    app.logger.info(f"Incoming data: {request.data}")
    logs_api.send_message(data=request.data)
    return Response(status=200)

# Set Logging
if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

    logs_api = HeaderlessLogAPI()

if __name__ == '__main__':
    app.run(host='127.0.0.1', debug=True)