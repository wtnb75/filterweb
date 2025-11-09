import json
import io
from logging import getLogger
from http.server import HTTPServer, BaseHTTPRequestHandler
from .serve import ServeBase
from dataclasses import field, dataclass
from ..trace import tracer, get_context, context

_log = getLogger(__name__)


@dataclass
class Endpoint:
    path: str
    method: str = "GET"
    sources: list[dict] = field(default_factory=list)
    filters: list[dict] = field(default_factory=list)


@dataclass
class ServeHTTPArg:
    host: str = "localhost"
    port: int = 0
    endpoints: list[Endpoint] = field(default_factory=list)


class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        ctx = get_context(self.headers)
        token = context.attach(ctx)
        try:
            with tracer.start_as_current_span("GET"):
                out = io.StringIO()
                ep = self.server.srv.get_endpoint(method="GET", path=self.path)
                _log.debug("endpoint %s", ep)
                _log.debug("headers: %s", str(dict(self.headers)))
                res = self.server.srv.process(ep.sources, ep.filters)
                self.send_response(200)
                if isinstance(res, (dict, tuple, list)):
                    self.send_header("content-type", "application/json")
                    json.dump(res, out, ensure_ascii=False)
                else:
                    out.write(res)
                    head100 = out.getvalue()[:100]
                    if "?xml" in head100:
                        self.send_header("content-type", "application/xml; charset=utf-8")
                    elif "DOCTYPE" in head100 or "<html" in head100:
                        self.send_header("content-type", "text/html; charset=utf-8")
                    else:
                        self.send_header("content-type", "text/plain; charset=utf-8")
                outb = out.getvalue().encode("utf-8")
                self.send_header("content-length", str(len(outb)))
                self.end_headers()
                self.wfile.write(out.getvalue().encode("utf-8"))
                return
        finally:
            context.detach(token)


class ServeHTTP(ServeBase):
    config_cls = ServeHTTPArg

    @tracer.start_as_current_span("endpoint")
    def get_endpoint(self, method, path) -> Endpoint:
        for ep in self.config.endpoints:
            if ep.method.lower() != method.lower():
                continue
            if ep.path != path:
                continue
            return ep
        raise FileNotFoundError(f"{method} {path} not found")

    def serve(self):
        host = self.config.host
        port = self.config.port
        _log.info("open server %s:%s", host, port)
        self.server = HTTPServer((host, port), RequestHandler)
        self.server.srv = self
        self.server.serve_forever()

    def shutdown(self):
        self.server.shutdown()
