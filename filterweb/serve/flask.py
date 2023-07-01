import json
import functools
from logging import getLogger
from flask import Flask
from .serve import ServeBase
from pydantic.dataclasses import dataclass
from dataclasses import field

_log = getLogger(__name__)


@dataclass
class Endpoint:
    path: str
    method: str = "GET"
    sources: list[dict] = field(default_factory=list)
    filters: list[dict] = field(default_factory=list)


@dataclass
class ServeFlaskArg:
    host: str = "localhost"
    port: int = 0
    endpoints: list[Endpoint] = field(default_factory=list)
    server: str = "builtin"
    other_options: dict = field(default_factory=dict)


class ServeFlask(ServeBase):
    config_cls = ServeFlaskArg

    @staticmethod
    def do1(srv, ep: Endpoint):
        _log.debug("endpoint %s", ep)
        res = srv.process(ep.sources, ep.filters)
        return res

    def serve(self):
        app = Flask(__name__)
        _log.info("open server %s:%s", self.config.host, self.config.port)
        for ep in self.config.endpoints:
            app.route(ep.path, methods=[ep.method])(
                functools.wraps(self.do1)(functools.partial(self.do1, self, ep)))
        if self.config.server == "builtin":
            app.run(self.config.host, self.config.port,
                    **self.config.other_options)
        elif self.config.server == "waitress":
            from waitress import serve
            serve(app, host=self.config.host, port=self.config.port,
                  **self.config.other_options)
        elif self.config.server == "gunicorn":
            from gunicorn.app import serve
            serve(app, self.config.other_options,
                  host=self.config.host, port=self.config.port)
