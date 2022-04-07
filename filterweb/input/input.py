from ..base import Base
from abc import ABCMeta, abstractmethod
from typing import Union, Optional
import csv
import json
import yaml
import xmltodict
import jsonpointer
from pydantic.dataclasses import dataclass
from logging import getLogger

_log = getLogger(__name__)


def input_arg(c):
    @dataclass
    class wrap(c):
        dest: Union[str, int, None] = None
        parse: Optional[str] = None
        select: Optional[str] = None
        __qualname__ = c.__qualname__
    return wrap


@input_arg
@dataclass
class InputArg:
    pass


class InputBase(Base, metaclass=ABCMeta):
    config_cls = InputArg

    @abstractmethod
    def read(self) -> Union[dict, str]:
        pass

    def convert(self, data: Union[dict, str]) -> dict:
        if isinstance(data, str):
            def_parse = "json"
        else:
            def_parse = "raw"
        parse = getattr(self.config, "parse", def_parse)
        if parse is None:
            parse = def_parse
        if parse == "json":
            res = json.loads(data)
        elif parse == "jsonl":
            decoder = json.JSONDecoder()
            res = []
            idx = 0
            while idx != len(data):
                r, idx = decoder.raw_decode(data, idx)
                res.append(r)
        elif parse == "yaml":
            res = yaml.safe_load(data)
        elif parse == "csv":
            rd = csv.DictReader(data.splitlines())
            res = list(rd)
        elif parse == "xml":
            res = xmltodict.parse(data)
        else:
            res = data
        _log.debug("data: %s", res)
        ptr = getattr(self.config, "select")
        if ptr:
            res = jsonpointer.resolve_pointer(res, ptr)
            _log.debug("selected: %s", res)
        return res

    def process(self) -> dict:
        return self.convert(self.read())
