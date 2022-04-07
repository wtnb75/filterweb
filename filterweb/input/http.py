from .input import InputBase, input_arg
import requests
from pydantic.dataclasses import dataclass


@input_arg
@dataclass
class InputHTTPArg:
    url: str
    method: str = "GET"


class InputHTTP(InputBase):
    config_cls = InputHTTPArg

    def read(self) -> str:
        res = requests.request(
            method=self.config.method,
            url=self.config.url)
        return res.text
