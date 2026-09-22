"""Modelo de representação de um Token léxico no compilador PyToJava."""

from dataclasses import dataclass
from typing import Any

from .token_type import TokenType


@dataclass(frozen=True)
class Token:
    """Estrutura imutável que representa uma unidade léxica identificada pelo scanner.

    Atributos:
        type: Categoria enumerada do token (TokenType).
        lexeme: Texto original no código-fonte.
        literal: Valor convertido em tipo nativo Python (int, float, str, bool, etc.).
        line: Linha no código-fonte (iniciando em 1).
        column: Coluna no código-fonte (iniciando em 1).
    """

    type: TokenType
    lexeme: str
    literal: Any = None
    line: int = 1
    column: int = 1

    def __repr__(self) -> str:
        return f'Token[{self.line}:{self.column}, {self.type}, "{self.lexeme}"]'

    def __str__(self) -> str:
        return self.__repr__()
