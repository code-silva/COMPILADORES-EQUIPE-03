"""Módulo de definição dos nós da Árvore de Sintaxe Abstrata (AST) para o PyToJava."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Node:
    """Classe base para todos os nós da AST do compilador PyToJava.

    Atributos:
        line: Linha no código-fonte onde o nó se origina (iniciando em 1).
        column: Coluna no código-fonte onde o nó se origina (iniciando em 1).
    """

    line: int = 0
    column: int = 0


@dataclass(frozen=True)
class ProgramNode(Node):
    """Nó raiz que representa um programa completo contendo uma lista de instruções."""

    stmts: list[Node] = field(default_factory=list)


@dataclass(frozen=True)
class AssignNode(Node):
    """Representa um comando de atribuição imperativa (simples ou acumulativa).

    Exemplos: x = 10, x += 1, x -= 5.
    """

    target: str = ""
    op: str = ""
    value: Node | None = None


@dataclass(frozen=True)
class ReturnNode(Node):
    """Representa uma instrução de retorno de função (return expr ou return)."""

    value: Node | None = None
