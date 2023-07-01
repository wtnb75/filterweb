from .filter import FilterBase
from jinja2 import Template, Environment, FileSystemLoader
from typing import Optional, Union
from dataclasses import field
from pydantic.dataclasses import dataclass


@dataclass
class FilterJinjaArg:
    template: Optional[str] = None
    template_file: Optional[str] = None
    template_basedir: str = "./"
    base_key: Optional[str] = None
    params: dict = field(default_factory=dict)
    vars: Union[list, dict, None] = None


class FilterJinja(FilterBase):
    config_cls = FilterJinjaArg
    name = "jinja2"

    def __init__(self, config):
        super().__init__(config)
        if self.config.template:
            self.tmpl = Template(
                source=self.config.template, **self.config.params)
        elif self.config.template_file:
            env = Environment(loader=FileSystemLoader(
                self.config.template_basedir, encoding="utf-8"))
            self.tmpl = env.get_template(self.config.template_file)
        else:
            raise ValueError("either template or template_file must be set")

    def apply(self, args) -> str:
        if self.config.base_key:
            args = {self.config.base_key: args}
        if self.config.vars:
            if isinstance(args, dict) and isinstance(self.config.vars, dict):
                args.update(self.config.vars)
            elif isinstance(args, list) and isinstance(self.config.vars, list):
                args.extend(self.config.vars)
            else:
                raise TypeError(
                    f"type mismatch: args({type(args)}), vars({type(self.config.vars)})")
        return self.tmpl.render(args)
