from .input import InputBase, input_arg
import subprocess
from dataclasses import field, dataclass
from ..trace import tracer


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
