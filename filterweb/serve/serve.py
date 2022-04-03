from ..base import Base
from abc import ABCMeta, abstractmethod


class ServeBase(Base, metaclass=ABCMeta):
    @abstractmethod
    def serve(self):
        pass


class ServeFlask(ServeBase):
    pass


class ServeGRPC(ServeBase):
    pass


class ServeXMLRPC(ServeBase):
    pass


class ServeJSONRPC(ServeBase):
    pass
