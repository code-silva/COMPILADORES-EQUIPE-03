"""Interface pública do analisador sintático."""

from .errors import ParserError
from .parser import Parser

__all__ = ["Parser", "ParserError"]
