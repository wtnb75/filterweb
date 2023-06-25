from .input import InputBase, input_arg
import requests
from pydantic.dataclasses import dataclass
from typing import Optional


@input_arg
@dataclass
class InputHTTPArg:
    url: str
    method: str = "GET"
    params: Optional[dict]= None


class InputHTTP(InputBase):
    config_cls = InputHTTPArg

    def read(self) -> str:
        if self.config.params is None:
            args = {}
        else:
            args = self.config.params
        res = requests.request(
            method=self.config.method,
            url=self.config.url, **args)
        return res.text
