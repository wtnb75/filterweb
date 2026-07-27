import os
import urllib.parse
from dataclasses import dataclass

import requests_unixsocket

from .input import InputBase, input_arg


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
