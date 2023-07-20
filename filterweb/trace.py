try:
    from opentelemetry import trace, context
    from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
    tracer = trace.get_tracer(__name__)

    def get_context(hdr):
        return TraceContextTextMapPropagator().extract(hdr)
except ImportError:
    from functools import wraps

    class tracer:
        @staticmethod
        def start_as_current_span(name="unknown"):
            def _span(func):
                @wraps(func)
                def _deco(*args, **kwargs):
                    return func(*args, **kwargs)
                return _deco
            return _span

    def get_context(hdr):
        return None

    class context:
        @staticmethod
        def attach(ctx):
            pass

        @staticmethod
        def detach(token):
            pass

__all__ = ["tracer"]
