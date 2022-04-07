from ..base import Base
from abc import abstractmethod, ABCMeta


class FilterBase(Base, metaclass=ABCMeta):
    @abstractmethod
    def apply(self, args) -> str:
        pass
