"""Módulo do analisador léxico do compilador PyToJava."""

from .char_stream import CharStream
from .errors import LexicalError
from .indent_manager import (
    finalize_indentation,
    get_current_indent_level,
    process_indentation,
    reset_indent_manager,
)
from .symbol_table import (
    Symbol,
    SymbolTable,
    contains_symbol,
    create_symbol_table,
    insert_symbol,
    lookup_symbol,
)
from .token import Token
from .token_type import TokenType

__all__ = [
    "CharStream",
    "LexicalError",
    "Symbol",
    "SymbolTable",
    "contains_symbol",
    "create_symbol_table",
    "insert_symbol",
    "lookup_symbol",
    "Token",
    "TokenType",
    "reset_indent_manager",
    "get_current_indent_level",
    "process_indentation",
    "finalize_indentation",
]