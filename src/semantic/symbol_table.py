"""Tabela de símbolos com escopos aninhados usada pelo analisador semântico.

Cada ``SymbolTable`` representa um escopo (o programa, o corpo de um ``if``,
de um ``while``...) e guarda um link para o escopo pai. A busca de um nome
começa no escopo atual e sobe pela cadeia de pais até o escopo global.

Exemplo::

    global_scope = SymbolTable()
    global_scope.define(Symbol(name="x", type="int", line=1))

    bloco = SymbolTable(parent=global_scope)
    bloco.lookup("x")                # encontra no escopo pai
    bloco.lookup_current_scope("x")  # None: não foi definido no bloco
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Symbol:
    """Variável registrada na tabela de símbolos.

    Atributos:
        name: Nome do identificador no código-fonte.
        type: Tipo primitivo inferido para a variável
            (ex.: ``"int"``, ``"float"``, ``"str"``, ``"bool"``, ``"None"``).
        line: Linha em que a variável foi definida pela primeira vez.
        column: Coluna em que a variável foi definida (opcional, padrão 0).
    """

    name: str
    type: str
    line: int
    column: int = 0


class SymbolTable:
    """Um escopo da tabela de símbolos, encadeado ao escopo pai.

    Atributos:
        symbols: Símbolos definidos neste escopo, indexados pelo nome.
        parent: Escopo que contém este, ou ``None`` no escopo global.
    """

    def __init__(self, parent: SymbolTable | None = None) -> None:
        self.symbols: dict[str, Symbol] = {}
        self.parent: SymbolTable | None = parent

    def define(self, symbol: Symbol) -> Symbol:
        """Registra ``symbol`` no escopo atual.

        Raises:
            ValueError: se já existir um símbolo com o mesmo nome neste
                escopo (redeclaração). Um nome igual em um escopo pai não é
                redeclaração: o novo símbolo apenas o sombreia.
        """
        existing = self.symbols.get(symbol.name)
        if existing is not None:
            raise ValueError(
                f"Variável '{symbol.name}' já declarada neste escopo "
                f"(linha {existing.line})"
            )
        self.symbols[symbol.name] = symbol
        return symbol

    def lookup(self, name: str) -> Symbol | None:
        """Busca ``name`` no escopo atual e, se não achar, nos escopos pais.

        Returns:
            O símbolo do escopo mais próximo que define o nome, ou ``None``
            se a variável não foi declarada em nenhum escopo visível.
        """
        scope: SymbolTable | None = self
        while scope is not None:
            symbol = scope.symbols.get(name)
            if symbol is not None:
                return symbol
            scope = scope.parent
        return None

    def lookup_current_scope(self, name: str) -> Symbol | None:
        """Busca ``name`` apenas no escopo atual, sem consultar os pais."""
        return self.symbols.get(name)

    def __contains__(self, name: str) -> bool:
        """Permite ``"x" in tabela``, equivalente a ``lookup(name) is not None``."""
        return self.lookup(name) is not None

    @property
    def depth(self) -> int:
        """Profundidade do escopo: 0 no global, 1 em um bloco dentro dele..."""
        return 0 if self.parent is None else self.parent.depth + 1

    def __repr__(self) -> str:
        return f"SymbolTable(symbols={list(self.symbols)}, depth={self.depth})"
