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


@dataclass(kw_only=True)
class IdentifierNode(Node):
    """Nó folha da AST que representa um identificador (nome de variável ou símbolo).

    Atributos:
        name: Nome textual do identificador no código-fonte.
        line: Linha no código-fonte (herdado de ``Node``).
        column: Coluna no código-fonte (herdado de ``Node``).
    """

    name: str = ""


@dataclass(kw_only=True)
class IntLiteralNode(Node):
    """Nó folha da AST que armazena um literal numérico inteiro.

    Atributos:
        value: Valor inteiro representado pelo literal.
        line: Linha no código-fonte (herdado de ``Node``).
        column: Coluna no código-fonte (herdado de ``Node``).
    """

    value: int = 0


@dataclass(kw_only=True)
class FloatLiteralNode(Node):
    """Nó folha da AST que armazena um literal numérico de ponto flutuante.

    Atributos:
        value: Valor float representado pelo literal.
        line: Linha no código-fonte (herdado de ``Node``).
        column: Coluna no código-fonte (herdado de ``Node``).
    """

    value: float = 0.0


@dataclass(kw_only=True)
class StringLiteralNode(Node):
    """Nó folha da AST que armazena um literal de texto (string).

    Atributos:
        value: Conteúdo textual da string (sem as aspas delimitadoras).
        line: Linha no código-fonte (herdado de ``Node``).
        column: Coluna no código-fonte (herdado de ``Node``).
    """

    value: str = ""


@dataclass(kw_only=True)
class BoolLiteralNode(Node):
    """Nó folha da AST que armazena um literal booleano (``True`` ou ``False``).

    Atributos:
        value: Valor booleano nativo (``True`` ou ``False``).
        line: Linha no código-fonte (herdado de ``Node``).
        column: Coluna no código-fonte (herdado de ``Node``).
    """

    value: bool = False


@dataclass(kw_only=True)
class NoneLiteralNode(Node):
    """Nó folha da AST que representa o literal nulo (``None``)."""


@dataclass
class ElifClauseNode(Node):
    """Nó que representa uma cláusula ``elif`` em blocos condicionais.

    Atributos:
        condition: Condição lógica da cláusula.
        body: Lista de instruções executadas quando a condição é verdadeira.
        line: Linha no código-fonte (herdado de ``Node``).
        column: Coluna no código-fonte (herdado de ``Node``).
    """

    condition: Node | None = None
    body: list[Node] = field(default_factory=list)


@dataclass
class ElseClauseNode(Node):
    """Nó que representa a cláusula ``else`` em blocos condicionais.

    Atributos:
        body: Lista de instruções executadas quando nenhuma condição anterior é verdadeira.
        line: Linha no código-fonte (herdado de ``Node``).
        column: Coluna no código-fonte (herdado de ``Node``).
    """

    body: list[Node] = field(default_factory=list)


@dataclass
class IfNode(Node):
    """Nó que representa uma estrutura condicional completa (if/elif/else).

    Atributos:
        condition: Condição lógica do ``if``.
        then_body: Instruções executadas quando a condição é verdadeira.
        elif_clauses: Cláusulas ``elif`` associadas.
        else_body: Instruções executadas quando nenhuma condição é verdadeira.
        line: Linha no código-fonte (herdado de ``Node``).
        column: Coluna no código-fonte (herdado de ``Node``).
    """

    condition: Node | None = None
    then_body: list[Node] = field(default_factory=list)
    elif_clauses: list[ElifClauseNode] = field(default_factory=list)
    else_body: list[Node] = field(default_factory=list)


@dataclass
class WhileNode(Node):
    """Nó que representa um laço de repetição (``while``).

    Atributos:
        condition: Condição de continuação do laço.
        body: Lista de instruções executadas a cada iteração.
        line: Linha no código-fonte (herdado de ``Node``).
        column: Coluna no código-fonte (herdado de ``Node``).
    """

    condition: Node | None = None
    body: list[Node] = field(default_factory=list)


@dataclass
class AssignNode(Node):
    """Nó da AST que representa operações de atribuição (=, +=, -=).

    Atributos:
        target: Identificador ou alvo da atribuição.
        op: Operador de atribuição ('=', '+=', '-=').
        value: Expressão atribuída ao alvo.
        line: Linha no código-fonte (herdado de ``Node``).
        column: Coluna no código-fonte (herdado de ``Node``).
    """

    target: str = ""
    op: str = ""
    value: Node | None = None


@dataclass
class ReturnNode(Node):
    """Nó da AST que representa instruções de retorno (return expr ou return).

    Atributos:
        value: Expressão opcional retornada pela instrução.
        line: Linha no código-fonte (herdado de ``Node``).
        column: Coluna no código-fonte (herdado de ``Node``).
    """

    value: Node | None = None


@dataclass
class PrintNode(Node):
    """Nó da AST que representa a instrução ``print(expr)`` ou ``print()``.

    Atributos:
        value: Expressão impressa, ou ``None`` para ``print()`` (linha vazia).
        line: Linha no código-fonte (herdado de ``Node``).
        column: Coluna no código-fonte (herdado de ``Node``).
    """

    value: Node | None = None
