import csv
import json
import re
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from logging import getLogger

import jsonpointer
import xmltodict
import yaml

from ..base import Base
from ..trace import tracer

_log = getLogger(__name__)


def input_arg(c):
    @dataclass
    class wrap(c):
        dest: str | int | None = None
        parse: str | None = None
        select: str | None = None
        convert_params: dict | None = None
        __qualname__ = c.__qualname__

    return wrap


@input_arg
@dataclass
class InputArg:
    pass


class InputBase(Base, metaclass=ABCMeta):
    config_cls = InputArg

    @abstractmethod
    def read(self) -> dict | str:
        pass

    @tracer.start_as_current_span(__name__)
    def convert(self, data: dict | str) -> dict | str:
        if isinstance(data, (str, bytes)):
            def_parse = "json"
        else:
            def_parse = "raw"
        parse = getattr(self.config, "parse", def_parse)
        conv_params = self.config.convert_params or {}
        if parse is None:
            parse = def_parse
        if parse == "json":
            res = json.loads(data, **conv_params)
        elif parse == "jsonl":
            decoder = json.JSONDecoder(**conv_params)
            res = []
            idx = 0
            while idx != len(data):
                r, idx = decoder.raw_decode(data, idx)
                res.append(r)
        elif parse == "yaml":
            res = yaml.safe_load(data)
        elif parse == "yamls":
            res = yaml.safe_load_all(data)
        elif parse == "csv":
            rd = csv.DictReader(data.splitlines(), **conv_params)
            res = list(rd)
        elif parse == "xml":
            res = xmltodict.parse(data, **conv_params)
        elif parse == "regex":
            m = re.compile(conv_params.get("pattern"))
            res = []
            for i in data.splitlines():
                p = m.search(i)
                if p:
                    res.append(p.groupdict())
        else:
            res = data
        _log.debug("data: %s", res)
        ptr = self.config.select
        if ptr:
            res = jsonpointer.resolve_pointer(res, ptr)
            _log.debug("selected: %s", res)
        return res

    def process(self) -> dict | str:
        return self.convert(self.read())
