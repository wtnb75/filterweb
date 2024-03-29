from typing import Union
from ..base import Base
from abc import ABCMeta, abstractmethod
import jsonpointer
from logging import getLogger
from ..trace import tracer

_log = getLogger(__name__)


class ServeBase(Base, metaclass=ABCMeta):
    @abstractmethod
    def serve(self):
        pass

    @abstractmethod
    def shutdown(self):
        pass

    @tracer.start_as_current_span("process")
    def process(self, sources: list[dict], filters: list[dict]):
        from ..index import open_input, open_filter

        data: Union[None, list, dict] = None
        for i in sources:
            i2 = i.copy()
            name = i2.pop("name", "http")
            dest = i2.pop("dest", "/")
            merge = i2.pop("merge", True)
            ip = open_input(name, i2)
            d1 = ip.process()
            if data is None:
                data = d1
                continue
            ptr = jsonpointer.JsonPointer(dest)
            try:
                if merge:
                    ptr.resolve(data).update(d1)
                else:
                    ptr.set(data, d1)
            except jsonpointer.JsonPointerException:
                cur = data
                for i in ptr.parts:
                    if i not in cur:
                        cur[i] = {}
                    cur = cur[i]
                if merge:
                    ptr.resolve(data).update(d1)
                else:
                    ptr.set(data, d1)
        res = data
        for i in filters:
            i2 = i.copy()
            name = i2.pop("name", "jinja")
            fp = open_filter(name, i2)
            _log.debug("arg=%s", str(res))
            res = fp.apply(res)
        return res


class ServeGRPC(ServeBase):
    pass


class ServeXMLRPC(ServeBase):
    pass


class ServeJSONRPC(ServeBase):
    pass
