import unittest
import tempfile
import filterweb
import json
import time
import threading
import requests


class TestServeHTTP(unittest.TestCase):
    def boot(self, config):
        self.srv = filterweb.open_serve("http", config)
        self.th = threading.Thread(target=self.srv.serve, name="http-server")
        self.th.start()
        while not hasattr(self.srv, "server"):
            time.sleep(0.5)
        self.url = f"http://{self.srv.server.server_address[0]}:{self.srv.server.server_address[1]}/"

    def setUp(self):
        self.tf = tempfile.NamedTemporaryFile("r+")
        json.dump({"hello": "world"}, self.tf)
        self.tf.flush()
        config = {
            "endpoints": [{
                "path": "/",
                "sources": [{
                    "name": "file",
                    "filename": self.tf.name,
                }],
                "filters": [{
                    "name": "jinja",
                    "template": "hello, {{hello}} from {{from}}",
                    "vars": {
                        "from": "you",
                    }
                }],
            }, {
                "path": "/source",
                "sources": [{
                    "name": "file",
                    "filename": self.tf.name,
                    "parse": "raw",
                }],
                "filters": [{
                    "name": "pygments",
                    "formatter": "html",
                    "lexer": "json",
                }],
            }, {
                "path": "/source/nolex",
                "sources": [{
                    "name": "file",
                    "filename": self.tf.name,
                    "parse": "raw",
                }],
                "filters": [{
                    "name": "pygments",
                    "formatter": "html",
                }],
            }]
        }
        self.boot(config)

    def tearDown(self):
        self.srv.shutdown()
        self.tf.close()
        self.th.join()
        del self.srv

    def test_file2text(self):
        res = requests.get(self.url)
        self.assertEqual("hello, world from you", res.text)

    def test_file2source(self):
        res = requests.get(self.url+"source")
        self.assertIn("&quot;hello&quot;", res.text)

    def test_file2source_nolex(self):
        res = requests.get(self.url+"source/nolex")
        self.assertIn("{&quot;hello&quot;: &quot;world&quot;}", res.text)


@unittest.skipUnless(hasattr(filterweb.serve, "ServeFlask"), "no flask installed")
class TestServeFlask(TestServeHTTP):
    def boot(self, config):
        self.srv = filterweb.open_serve("flask", config)
        self.th = threading.Thread(target=self.srv.serve, name="flask-server")
        self.th.start()
        while not hasattr(self.srv, "server"):
            time.sleep(0.5)
        self.url = f"http://{self.srv.server.server_address[0]}:{self.srv.server.server_address[1]}/"
