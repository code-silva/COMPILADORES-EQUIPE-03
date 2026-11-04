"""Estrutura base de nós da Árvore Sintática Abstrata (AST) do compilador PyToJava."""

from dataclasses import dataclass, field


@dataclass(kw_only=True)
class Node:
    """Classe base para todos os nós da Árvore Sintática Abstrata (AST).

    Utiliza ``kw_only=True`` para permitir que subclasses definam atributos
    posicionais ou com valores padrão sem conflito de ordenação com os
    metadados de posição no código-fonte.

    Atributos:
        line: Linha no código-fonte onde a construção se inicia (padrão: 0).
        column: Coluna no código-fonte onde a construção se inicia (padrão: 0).
    """

    line: int = 0
    column: int = 0


@dataclass
class ProgramNode(Node):
    """Nó raiz da AST que representa o programa completo como uma sequência de instruções.

    Atributos:
        stmts: Lista ordenada de instruções (statements) de nível superior do programa.
        line: Linha de início do programa no código-fonte (herdado de ``Node``).
        column: Coluna de início do programa no código-fonte (herdado de ``Node``).
    """

    stmts: list[Node] = field(default_factory=list)
