from .input import InputBase, input_arg
from pydantic.dataclasses import dataclass


@input_arg
@dataclass
class InputFileArg:
    filename: str


class InputFile(InputBase):
    config_cls = InputFileArg

    def read(self) -> str:
        with open(self.config.filename, "r") as fp:
            return fp.read()
