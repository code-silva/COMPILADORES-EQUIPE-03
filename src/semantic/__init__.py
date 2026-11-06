"""Analisador semântico do compilador PyToJava."""

from .analyzer import SemanticAnalyzer
from .errors import SemanticError
from .symbol_table import Symbol, SymbolTable

__all__ = [
    "SemanticAnalyzer",
    "SemanticError",
    "Symbol",
    "SymbolTable",
]
