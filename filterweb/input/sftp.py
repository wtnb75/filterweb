from .input import InputBase, input_arg
import paramiko
from dataclasses import field, dataclass
from ..trace import tracer


@input_arg
@dataclass
class InputSFTPArg:
    hostname: str
    filename: str
    params: dict = field(default_factory=dict)
    missing_host_key: str = "Warning"


class InputSFTP(InputBase):
    config_cls = InputSFTPArg

    missing_host_key_map = {
        "Warning": paramiko.WarningPolicy,
        "AutoAdd": paramiko.AutoAddPolicy,
        "Reject": paramiko.RejectPolicy,
    }

    @tracer.start_as_current_span(__name__)
    def read(self) -> str:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(self.missing_host_key_map.get(
            self.config.missing_host_key, paramiko.WarningPolicy)())
        client.connect(hostname=self.config.hostname, **self.config.params)
        sftp = client.open_sftp()
        fp = sftp.file(filename=self.config.filename)
        res = fp.read()
        fp.close()
        client.close()
        return res
