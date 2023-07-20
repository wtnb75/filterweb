from .input import InputBase, input_arg
import requests
from dataclasses import dataclass
from ..trace import tracer


@input_arg
@dataclass
class InputJSONRPCArg:
    url: str
    method: str
    params: list


class InputJSONRPC(InputBase):
    config_cls = InputJSONRPCArg

    @tracer.start_as_current_span(__name__)
    def read(self) -> dict:
        payload = {
            "method": self.config.method,
            "params": self.config.params,
            "jsonrpc": "2.0",
            "id": 0,
        }
        return requests.post(self.config.url, json=payload).json().get("result")
