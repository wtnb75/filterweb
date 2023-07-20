from .input import InputBase, input_arg
import requests
from dataclasses import dataclass
from typing import Optional
from logging import getLogger

_log = getLogger(__name__)
try:
    from opentelemetry.instrumentation.requests import RequestsInstrumentor
    RequestsInstrumentor().instrument()
    _log.debug("requests instrumentor installed")
except ImportError:
    pass


@input_arg
@dataclass
class InputHTTPArg:
    url: str
    method: str = "GET"
    params: Optional[dict] = None


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
