from dataclasses import dataclass

from pygments import highlight
from pygments.formatters import get_formatter_by_name
from pygments.lexers import get_lexer_by_name, guess_lexer

from ..trace import tracer
from .filter import FilterBase


@dataclass
class FilterPygmentsArg:
    formatter: str
    lexer: str | None = None


class FilterPygments(FilterBase):
    config_cls = FilterPygmentsArg

    def __init__(self, config):
        super().__init__(config)
        if self.config.lexer:
            self.lexer = get_lexer_by_name(self.config.lexer)
        else:
            self.lexer = None
        self.formatter = get_formatter_by_name(self.config.formatter)

    @tracer.start_as_current_span(__name__)
    def apply(self, args) -> str:
        if self.lexer:
            lexer = self.lexer
        else:
            lexer = guess_lexer(args)
        return highlight(args, lexer, self.formatter)
