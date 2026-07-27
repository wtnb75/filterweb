import subprocess
from dataclasses import dataclass, field
from logging import getLogger

from ..trace import tracer
from .filter import FilterBase

_log = getLogger(__name__)


@dataclass
class FilterProcessArg:
    command: list[str] = field(default_factory=list)
    params: dict = field(default_factory=dict)


class FilterProcess(FilterBase):
    config_cls = FilterProcessArg

    @tracer.start_as_current_span(__name__)
    def apply(self, args) -> str:
        p = subprocess.Popen(
            args=self.config.command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            **self.config.params,
        )
        stdout, stderr = p.communicate(args)
        if p.returncode:
            _log.info("exit code: %s", p.returncode)
        if stderr:
            _log.info("stderr: %s", stderr)
        return stdout
