from ntu_learn_downloader.tests.mock_server import start_mock_server

server = None


def setup_package():
    global server
    server = start_mock_server(8082)  # for fake API server


def teardown_package():
    server.shutdown()
