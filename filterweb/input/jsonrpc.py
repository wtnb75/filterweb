from .input import InputBase, input_arg
import requests
from pydantic.dataclasses import dataclass


@input_arg
@dataclass
class InputJSONRPCArg:
    url: str
    method: str
    params: list


class InputJSONRPC(InputBase):
    config_cls = InputJSONRPCArg

    def read(self) -> dict:
        payload = {
            "method": self.config.method,
            "params": self.config.params,
            "jsonrpc": "2.0",
            "id": 0,
        }
        return requests.post(self.config.url, json=payload).json().get("result")
