from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import re
import socket
from threading import Thread
import os

from urllib.parse import urlparse, parse_qsl
import requests

FIXTURES_PATH = os.path.join(os.path.dirname(__file__), "fixtures")

MOCK_CONSTANTS = {
    "GET_COURSES_URL": "http://localhost:8082/webapps/blackboard/execute/globalCourseNavMenuSection",
    "GET_CONTENT_IDS_URL": "http://localhost:8082/webapps/blackboard/execute/announcement",
    "GET_CONTENT_LIST_URL": "http://localhost:8082/webapps/blackboard/content/listContent.jsp",
    "NTULEARN_URL": "http://localhost:8082"
}

# load all of the json files
fixtures = []

for root, _subdirs, files in os.walk(FIXTURES_PATH):
    for file in files:
        if not file.endswith(".json"):
            continue
        with open(os.path.join(root, file)) as json_file:
            fixtures.append(json.load(json_file))


class MockServerRequestHandler(BaseHTTPRequestHandler):
    def handle_HEAD_GET_request(self, method=str):
        def match(request_handler: BaseHTTPRequestHandler, fixture) -> bool:
            parsed_url = urlparse(request_handler.path)
            query_params = dict(parse_qsl(parsed_url.query))

            request = fixture["request"]

            return (
                request_handler.command == request["method"]
                and parsed_url.path == request["request_path"]
                and query_params == request.get("query", {})
            )

        # DEBUGGING
        # parsed_url = urlparse(self.path)
        # query_params = dict(parse_qsl(parsed_url.query))
        # print(self.command, parsed_url.path, query_params)

        try:
            response = next(fix["response"] for fix in fixtures if match(self, fix))
        except StopIteration:
            raise Exception("Not fixture found for request: {}".format(self.path))

        # Add response content.
        self.send_response(response["status_code"])
        # Add response headers if present in captured response
        if response.get('headers', None):
            for key, val in response['headers'].items():
                self.send_header(key, val)
        else:
            self.send_header("Content-Type", "application/json; charset=utf-8")
        if 'url' in response:
            self.send_header("Location", response['url'])
        self.end_headers()
        # only include response content if GET method
        if method == "GET":
            response_content = response["body"]
            self.wfile.write(response_content.encode("utf-8"))
        

    def do_HEAD(self):
        self.handle_HEAD_GET_request(method="HEAD")

    def do_GET(self):
        self.handle_HEAD_GET_request(method="GET")


def get_free_port():
    s = socket.socket(socket.AF_INET, type=socket.SOCK_STREAM)
    s.bind(("localhost", 0))
    __address, port = s.getsockname()
    s.close()
    return port


def start_mock_server(port):
    mock_server = HTTPServer(("localhost", port), MockServerRequestHandler)
    mock_server_thread = Thread(target=mock_server.serve_forever)
    mock_server_thread.setDaemon(True)
    mock_server_thread.start()

    return mock_server
