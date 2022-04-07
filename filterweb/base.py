from typing import Optional
from dataclasses import is_dataclass


class Base:
    config_cls = None
    name: Optional[str] = None

    def __init__(self, config: dict):
        if is_dataclass(self.config_cls):
            self.config = self.config_cls(**config)
        else:
            self.config = config
