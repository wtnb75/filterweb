from abc import ABCMeta, abstractmethod

from ..base import Base


class FilterBase(Base, metaclass=ABCMeta):
    @abstractmethod
    def apply(self, args) -> str:
        pass
