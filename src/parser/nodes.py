"""Estrutura de nós da Árvore Sintática Abstrata (AST) do compilador PyToJava."""

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


@dataclass
class BinOpNode(Node):
    """Nó da AST que representa uma expressão binária (aritmética ou relacional).

    Permite o aninhamento recursivo nos operandos ``left`` e ``right`` para
    estruturar a precedência e a associatividade dos operadores na árvore sintática.

    Atributos:
        left: Sub-árvore ou nó correspondente ao operando esquerdo.
        op: Símbolo textual do operador (ex.: ``"+"``, ``"*"``, ``"=="``, ``"<="``).
        right: Sub-árvore ou nó correspondente ao operando direito.
        line: Linha no código-fonte onde a operação ocorre (herdado de ``Node``).
        column: Coluna no código-fonte onde a operação ocorre (herdado de ``Node``).
    """

    left: Node | None = None
    op: str = ""
    right: Node | None = None


@dataclass
class IdentifierNode(Node):
    """Nó folha da AST que representa um identificador (nome de variável ou símbolo).

    Atributos:
        name: Nome textual do identificador no código-fonte.
        line: Linha no código-fonte (herdado de ``Node``).
        column: Coluna no código-fonte (herdado de ``Node``).
    """

    name: str = ""


@dataclass
class IntLiteralNode(Node):
    """Nó folha da AST que armazena um literal numérico inteiro.

    Atributos:
        value: Valor inteiro representado pelo literal.
        line: Linha no código-fonte (herdado de ``Node``).
        column: Coluna no código-fonte (herdado de ``Node``).
    """

    value: int = 0


@dataclass
class FloatLiteralNode(Node):
    """Nó folha da AST que armazena um literal numérico de ponto flutuante.

    Atributos:
        value: Valor float representado pelo literal.
        line: Linha no código-fonte (herdado de ``Node``).
        column: Coluna no código-fonte (herdado de ``Node``).
    """

    value: float = 0.0


@dataclass
class StringLiteralNode(Node):
    """Nó folha da AST que armazena um literal de texto (string).

    Atributos:
        value: Conteúdo textual da string (sem as aspas delimitadoras).
        line: Linha no código-fonte (herdado de ``Node``).
        column: Coluna no código-fonte (herdado de ``Node``).
    """

    value: str = ""


@dataclass
class BoolLiteralNode(Node):
    """Nó folha da AST que armazena um literal booleano (``True`` ou ``False``).

    Atributos:
        value: Valor booleano nativo (``True`` ou ``False``).
        line: Linha no código-fonte (herdado de ``Node``).
        column: Coluna no código-fonte (herdado de ``Node``).
    """

    value: bool = False


@dataclass
class NoneLiteralNode(Node):
    """Nó folha da AST que representa o literal nulo (``None``)."""
