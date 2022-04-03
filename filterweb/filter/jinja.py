from .filter import FilterBase
from jinja2 import Template, Environment, FileSystemLoader
from typing import Optional
from dataclasses import field
from pydantic.dataclasses import dataclass


@dataclass
class FilterJinjaArg:
    template: Optional[str] = None
    template_file: Optional[str] = None
    template_basedir: str = "./"
    params: dict = field(default_factory=dict)


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
        return self.tmpl.render(args)
