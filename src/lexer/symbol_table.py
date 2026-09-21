"""Tabela de símbolos básica usada pelo analisador léxico."""

from dataclasses import dataclass

from .token_type import TokenType


@dataclass(frozen=True)
class Symbol:
    """Registra os dados da primeira ocorrência de um identificador."""

    name: str
    token_type: TokenType
    first_declared_line: int
    first_declared_col: int


class SymbolTable:
    """Armazena símbolos por nome e preserva sua primeira ocorrência."""

    def __init__(self) -> None:
        self.symbols: dict[str, Symbol] = {}

    def insert(
        self,
        name: str,
        token_type: TokenType,
        line: int,
        col: int,
    ) -> Symbol:
        """Insere um símbolo novo ou retorna o registro já existente."""
        if name not in self.symbols:
            self.symbols[name] = Symbol(name, token_type, line, col)
        return self.symbols[name]

    def lookup(self, name: str) -> Symbol | None:
        """Retorna o símbolo associado ao nome, quando existente."""
        return self.symbols.get(name)

    def contains(self, name: str) -> bool:
        """Informa se o nome já está registrado na tabela."""
        return name in self.symbols

    def all_symbols(self) -> list[Symbol]:
        """Retorna todos os símbolos na ordem em que foram inseridos."""
        return list(self.symbols.values())
