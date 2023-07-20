from .input import InputBase, input_arg
from dataclasses import dataclass
from ..trace import tracer


@input_arg
@dataclass
class InputFileArg:
    filename: str


class InputFile(InputBase):
    config_cls = InputFileArg

    @tracer.start_as_current_span(__name__)
    def read(self) -> str:
        with open(self.config.filename, "r") as fp:
            return fp.read()
