from .input import InputBase, input_arg
import sqlite3
from pydantic.dataclasses import dataclass
from dataclasses import field


@input_arg
@dataclass
class InputSQLite3Arg:
    database: str
    query: str
    params: list[str] = field(default_factory=list)


class InputSQLite3(InputBase):
    config_cls = InputSQLite3Arg

    def __init__(self, config):
        super().__init__(config)
        self.db = sqlite3.connect(self.config.database)

    def read(self) -> dict:
        cur = self.db.execute(self.config.query, self.config.params)
        keys = [x[0] for x in cur.description]
        return [dict(zip(keys, x)) for x in cur.fetchall()]
