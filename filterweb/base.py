from typing import Optional, Union
from dataclasses import is_dataclass
from dacite import from_dict


class Base:
    config_cls = None
    config: Union[config_cls, dict, None] = None
    name: Optional[str] = None

    def __init__(self, config: dict):
        if is_dataclass(self.config_cls):
            self.config = from_dict(data_class=self.config_cls, data=config)
        else:
            self.config = config
