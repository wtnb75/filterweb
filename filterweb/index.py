from . import filter as fw_filter
from . import input as fw_input
from . import serve as fw_serve
from logging import getLogger

_log = getLogger(__name__)


def open_cls(mod, base_cls, prefix: str, name: str, config: dict):
    _log.debug("open mod=%s, base=%s, prefix=%s, name=%s",
               str(mod), str(base_cls), prefix, name)
    for k in dir(mod):
        _log.debug("check %s", k)
        if not k.startswith(prefix):
            _log.debug("skip by prefix %s / %s", k, prefix)
            continue
        if k.endswith("Base"):
            _log.debug("skip by Base %s", k)
            continue
        v = getattr(mod, k)
        _log.debug("v = %s", v)
        if issubclass(v, base_cls):
            _log.debug("subclass %s", k)
            if k.lower() == (prefix + name).lower():
                return v(config)
            _log.debug("does not match %s / %s + %s", k, prefix, name)
    raise ModuleNotFoundError(f"{name} not found")


def open_filter(name: str, config: dict) -> fw_filter.FilterBase:
    return open_cls(
        mod=fw_filter, base_cls=fw_filter.FilterBase, prefix="Filter",
        name=name, config=config)


def open_input(name: str, config: dict) -> fw_input.InputBase:
    return open_cls(
        mod=fw_input, base_cls=fw_input.InputBase, prefix="Input",
        name=name, config=config)


def open_serve(name: str, config: dict) -> fw_serve.ServeBase:
    return open_cls(
        mod=fw_serve, base_cls=fw_serve.ServeBase, prefix="Serve",
        name=name, config=config)
