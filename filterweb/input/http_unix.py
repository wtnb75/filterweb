from .input import InputBase, input_arg
import os
import urllib.parse
import requests_unixsocket
from dataclasses import dataclass


@input_arg
@dataclass
class InputHTTPUnixArg:
    sockpath: str
    path: str
    method: str = "GET"


class InputHTTPUnix(InputBase):
    config_cls = InputHTTPUnixArg

    def read(self) -> str:
        sess = requests_unixsocket.Session()
        url = os.path.join("http+unix://" + urllib.parse.quote(self.config.sockpath), self.config.path)
        res = sess.request(method=self.config.method, url=url)
        return res.text
