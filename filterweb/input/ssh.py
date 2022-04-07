from .input import InputBase, input_arg
from typing import Optional
import paramiko
from pydantic.dataclasses import dataclass
from dataclasses import field


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

    def read(self) -> str:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(self.missing_host_key_map.get(
            self.config.missing_host_key, paramiko.WarningPolicy)())
        client.connect(hostname=self.config.hostname, **self.config.params)
        stdin, stdout, stderr = client.exec_command(
            command=self.config.command,
            environment=self.config.env,
            get_pty=self.config.get_pty,
            timeout=self.config.timeout)
        if self.config.input:
            stdin.write(self.config.input)
        stdin.close()
        res = stdout.read()
        client.close()
        del stdin, stdout, stderr, client
        return res
