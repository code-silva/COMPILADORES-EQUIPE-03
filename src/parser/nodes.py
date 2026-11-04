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

"""essa classe é responsável armazenar o nome dos nossos atributos"""
@dataclass
class IdentifierNode(Node):
    """o nome usado como indentificador é do tipo string, pois pode ser com números e letras"""
    name: str = ""

"""essa é responsável por armazenar os número inteiros com, por exemplo, 1 ou 2"""
@dataclass(kw_only=True)
class IntLiteralNode(Node):
    value: int = 0

"""essa responsável por armazenar os números com ponto flutuante, por exemplo, 3.14"""
@dataclass(kw_only=True)
class FloatLiteralNode(Node):
    value: float = 0.0

"""essa armazena texto dentro de aspas simples ou duplas"""
@dataclass(kw_only=True)
class StringLiteralNode(Node):
    value: str = ""

"""essa responsável por armazenar valores boobleanos com TRUE ou FALSE"""
@dataclass(kw_only=True)
class BoolLiteralNode(Node):
    value: bool = False

"""essa armazena valores NULL ou NONE"""
@dataclass(kw_only=True)
class NoneLiteralNode(Node):
    pass