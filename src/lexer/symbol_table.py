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


SymbolTable = dict[str, Symbol]


def create_symbol_table() -> SymbolTable:
    """Cria e retorna uma tabela de símbolos vazia."""
    return {}


def insert_symbol(
    table: SymbolTable,
    name: str,
    token_type: TokenType,
    line: int,
    col: int,
) -> Symbol:
    """Insere um símbolo novo ou retorna o registro já existente."""
    if name not in table:
        table[name] = Symbol(name, token_type, line, col)
    return table[name]


def lookup_symbol(table: SymbolTable, name: str) -> Symbol | None:
    """Retorna o símbolo associado ao nome, quando existente."""
    return table.get(name)


def contains_symbol(table: SymbolTable, name: str) -> bool:
    """Informa se o nome já está registrado na tabela."""
    return name in table
