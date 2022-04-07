import unittest
import threading
import filterweb.input
from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler


class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)


class MyServer(SimpleXMLRPCServer):
    def kill(self):
        self.shutdown()
        self.server_close()


class TestInputXMLRPC(unittest.TestCase):
    def setUp(self):
        self.srv = MyServer(("127.0.0.1", 0))
        self.srv.register_function(lambda f: {"hello": f}, name="hello")
        self.url = f"http://{self.srv.server_address[0]}:{self.srv.server_address[1]}/RPC2"
        self.th = threading.Thread(
            target=self.srv.serve_forever, name="xmlrpc")
        self.th.start()

    def tearDown(self):
        self.srv.kill()
        self.th.join()

    def test_xmlrpc(self):
        ifp = filterweb.input.InputXMLRPC({
            "uri": self.url,
            "method": "hello",
            "args": ["world"]
        })
        res = ifp.process()
        self.assertEqual({"hello": "world"}, res)
