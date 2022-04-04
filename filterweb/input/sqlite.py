from .input import InputBase, input_arg
import sqlite3
from pydantic.dataclasses import dataclass
from dataclasses import field


@input_arg
@dataclass
class InputSQLite3Arg:
    database: str
    query: str
    read_only: bool = True
    connect_params: dict = field(default_factory=dict)
    params: list[str] = field(default_factory=list)


class InputSQLite3(InputBase):
    config_cls = InputSQLite3Arg

    def __init__(self, config):
        super().__init__(config)
        if self.config.read_only:
            self.db = sqlite3.connect(
                f"file:{self.config.database}?mode=ro", uri=True, **self.config.connect_params)
        else:
            self.db = sqlite3.connect(
                self.config.database, **self.config.connect_params)

    def read(self) -> list[dict]:
        cur = self.db.execute(self.config.query, self.config.params)
        keys = [x[0] for x in cur.description]
        return [dict(zip(keys, x)) for x in cur.fetchall()]
