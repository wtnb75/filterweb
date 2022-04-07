from .input import InputBase, input_arg
from xmlrpc.client import ServerProxy
from pydantic.dataclasses import dataclass
from dataclasses import field


@input_arg
@dataclass
class InputXMLRPCArg:
    uri: str
    method: str
    options: dict = field(default_factory=dict)
    args: list = field(default_factory=list)
    kwargs: dict = field(default_factory=dict)


class InputXMLRPC(InputBase):
    config_cls = InputXMLRPCArg

    def read(self):
        with ServerProxy(self.config.uri, **self.config.options) as srv:
            mtd = srv
            for i in self.config.method.split("."):
                mtd = getattr(mtd, i)
            return mtd(*self.config.args, **self.config.kwargs)
