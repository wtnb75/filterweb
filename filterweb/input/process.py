import subprocess
from dataclasses import dataclass, field

from ..trace import tracer
from .input import InputBase, input_arg


@input_arg
@dataclass
class InputProcessArg:
    command: list[str]
    input: str = ""
    params: dict = field(default_factory=dict)


class InputProcess(InputBase):
    config_cls = InputProcessArg

    @tracer.start_as_current_span(__name__)
    def read(self) -> str:
        return subprocess.check_output(self.config.command, input=self.config.input, **self.config.params)
