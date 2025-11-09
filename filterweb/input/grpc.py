from .input import InputBase, input_arg
from dataclasses import field, dataclass
from grpc_requests import Client
from ..trace import tracer


@input_arg
@dataclass
class InputGRPCArg:
    endpoint: str
    service_name: str
    method: str
    arg: dict = field(default_factory=dict)
    connect_params: dict = field(default_factory=dict)


class InputGRPC(InputBase):
    config_cls = InputGRPCArg

    @tracer.start_as_current_span(__name__)
    def read(self) -> dict:
        client = Client.get_by_endpoint(self.config.endpoint, **self.config.connect_params)
        return client.request(self.config.service_name, self.config.method, self.config.arg)
