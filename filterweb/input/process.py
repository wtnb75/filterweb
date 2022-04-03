from .input import InputBase, input_arg
import subprocess
from pydantic.dataclasses import dataclass


@input_arg
@dataclass
class InputProcessArg:
    command: list[str]
    input: str = ""


class InputProcess(InputBase):
    config_cls = InputProcessArg

    def read(self) -> str:
        return subprocess.check_output(self.config.command, input=self.config.input)
