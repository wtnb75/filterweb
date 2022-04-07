from .input import InputBase, input_arg
from dataclasses import field
from grpc_requests import Client
from pydantic.dataclasses import dataclass


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

    def read(self) -> dict:
        client = Client.get_by_endpoint(
            self.config.endpoint, **self.config.connect_params)
        return client.request(
            self.config.service_name,
            self.config.method, self.config.arg)
