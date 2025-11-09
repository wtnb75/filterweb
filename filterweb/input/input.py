from ..base import Base
from abc import ABCMeta, abstractmethod
from typing import Union, Optional
import csv
import json
import yaml
import xmltodict
import jsonpointer
import re
from dataclasses import dataclass
from logging import getLogger
from ..trace import tracer

_log = getLogger(__name__)


def input_arg(c):
    @dataclass
    class wrap(c):
        dest: Union[str, int, None] = None
        parse: Optional[str] = None
        select: Optional[str] = None
        convert_params: Optional[dict] = None
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

    @tracer.start_as_current_span(__name__)
    def convert(self, data: Union[dict, str]) -> Union[dict, str]:
        if isinstance(data, (str, bytes)):
            def_parse = "json"
        else:
            def_parse = "raw"
        parse = getattr(self.config, "parse", def_parse)
        conv_params = getattr(self.config, "convert_params") or {}
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
        ptr = getattr(self.config, "select")
        if ptr:
            res = jsonpointer.resolve_pointer(res, ptr)
            _log.debug("selected: %s", res)
        return res

    def process(self) -> Union[dict, str]:
        return self.convert(self.read())
