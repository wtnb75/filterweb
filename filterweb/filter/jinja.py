from dataclasses import dataclass, field
from logging import getLogger

from jinja2 import Environment, FileSystemLoader, Template

from .filter import FilterBase

_log = getLogger(__name__)
try:
    from opentelemetry.instrumentation.jinja2 import Jinja2Instrumentor

    Jinja2Instrumentor().instrument()
    _log.debug("jinja2 instrumentor installed")
except ImportError:
    pass


@dataclass
class FilterJinjaArg:
    template: str | None = None
    template_file: str | None = None
    template_basedir: str = "./"
    base_key: str | None = None
    params: dict = field(default_factory=dict)
    vars: list | dict | None = None


class FilterJinja(FilterBase):
    config_cls = FilterJinjaArg
    name = "jinja2"

    def __init__(self, config):
        super().__init__(config)
        if self.config.template:
            self.tmpl = Template(source=self.config.template, **self.config.params)
        elif self.config.template_file:
            env = Environment(loader=FileSystemLoader(self.config.template_basedir, encoding="utf-8"))
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
                raise TypeError(f"type mismatch: args({type(args)}), vars({type(self.config.vars)})")
        return self.tmpl.render(args)
