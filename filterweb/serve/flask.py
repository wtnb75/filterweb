import functools
from logging import getLogger
from flask import Flask, request
from .serve import ServeBase
from dataclasses import field, dataclass
from ..trace import get_context, context
_log = getLogger(__name__)

try:
    from opentelemetry.instrumentation.flask import FlaskInstrumentor
    FlaskInstrumentor().instrument(enable_commenter=True, commenter_options={})
    _log.debug("flask instrumentor installed")
except ImportError:
    pass


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
        ctx = get_context(request.headers)
        token = context.attach(ctx)
        try:
            _log.debug("endpoint %s", ep)
            _log.debug("headers: %s", str(dict(request.headers)))
            res = srv.process(ep.sources, ep.filters)
            return res
        finally:
            context.detach(token)

    def serve(self):
        self.app = Flask(__name__)
        _log.info("open server %s:%s by %s", self.config.host,
                  self.config.port, self.config.server)
        for ep in self.config.endpoints:
            self.app.add_url_rule(
                ep.path, endpoint=ep.path, methods=[ep.method],
                view_func=functools.partial(self.do1, self, ep))
        if self.config.server == "builtin":
            from werkzeug.serving import make_server
            self.server = make_server(
                self.config.host, self.config.port, self.app, **self.config.other_options)
            _log.info("server %s", self.server)
            self.server.serve_forever()
        elif self.config.server == "waitress":
            from waitress import create_server
            self.server = create_server(
                self.app, host=self.config.host, port=self.config.port, **self.config.other_options)
            _log.info("server %s", self.server)
            self.server.run()
        elif self.config.server == "gunicorn":
            from gunicorn.app import serve
            serve(self.app, self.config.other_options,
                  host=self.config.host, port=self.config.port)
        else:
            raise NotImplementedError(f"server {self.config.server} not found")

    def shutdown(self):
        if self.config.server == "builtin":
            self.server.shutdown()
        elif self.config.server == "waitress":
            self.server.close()
        elif self.config.server == "gunicorn":
            raise NotImplementedError("gunicorn shutdown")
