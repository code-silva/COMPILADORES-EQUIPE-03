"""Estrutura base de nós da Árvore Sintática Abstrata (AST) do compilador PyToJava."""
from __future__ import annotations
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

"""como bloco de códico de elif, else,
    if ou while pode ter mais de uma instrução 
    vamos utilizar aqui listas"""

"""essa classe representa a clásula elif em estruturas
ondicionais"""
@dataclass
class ElifClauseNode(Node):
    """Nó que representa uma cláusula 'elif' em blocos condicionais.
    
    Atributos:
        condition: Guarda a condição lógica do elif.
        body: Guarda a lista de instruções que serão executadas se o elif for verdadeiro.
    """
    condition: Node | None = None
    body: list[Node] = field(default_factory=list)

@dataclass
class ElseClauseNode(Node):
    """Nó que representa a cláusula 'else' em blocos condicionais.
    
    Atributos:
        body: Guarda a lista de instruções executadas quando nenhuma condição anterior for verdadeira.
    """
    body: list[Node] = field(default_factory=list)

"""Nó que representa uma estrutura condicional completa (if/elif/else)."""
@dataclass
class IfNode(Node):
    """aqui é o nossa condição do if """
    condition: Node | None = None
    """aqui temos a lista que guarda o código que será executado caso if seja verdadeira"""
    then_body: list[Node] = field(default_factory=list)
    """aqui é guardado os blocos de elif quando estiver presente no código"""
    elif_clauses: list[ElifClauseNode] = field(default_factory=list)
    """aqui é gradado o blocos de else, o qual não tem nenhuam condição, quando presente no código"""
    else_body: list[Node] = field(default_factory=list)

"""Nó que representa um laço de repetição (while)."""
@dataclass
class WhileNode(Node):
    condition: Node | None = None
    body: list[Node] = field(default_factory=list)
