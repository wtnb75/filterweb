from .input import InputBase, input_arg
from typing import Optional
import paramiko
from dataclasses import field, dataclass
from logging import getLogger
from ..trace import tracer

_log = getLogger(__name__)


@input_arg
@dataclass
class InputSSHArg:
    hostname: str
    command: str
    input: Optional[str] = None
    params: dict = field(default_factory=dict)
    env: Optional[dict] = None
    get_pty: bool = False
    timeout: Optional[int] = None
    missing_host_key: str = "Warning"


class InputSSH(InputBase):
    config_cls = InputSSHArg

    missing_host_key_map = {
        "Warning": paramiko.WarningPolicy,
        "AutoAdd": paramiko.AutoAddPolicy,
        "Reject": paramiko.RejectPolicy,
    }

    @tracer.start_as_current_span(__name__)
    def read(self) -> str:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(
            self.missing_host_key_map.get(self.config.missing_host_key, paramiko.WarningPolicy)()
        )
        client.connect(hostname=self.config.hostname, **self.config.params)
        stdin, stdout, stderr = client.exec_command(
            command=self.config.command,
            environment=self.config.env,
            get_pty=self.config.get_pty,
            timeout=self.config.timeout,
        )
        if self.config.input:
            stdin.write(self.config.input)
        exit_code = stdout.channel.recv_exit_status()
        if exit_code != 0:
            _log.info("exit code: %s", exit_code)
        stdin.close()
        res = stdout.read()
        client.close()
        err_str = stderr.read()
        if err_str:
            _log.info("stderr: %s", err_str)
        del stdin, stdout, stderr, client
        return res
