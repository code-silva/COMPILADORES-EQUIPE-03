"""Módulo de definição dos tipos de tokens suportados pelo PyToJava."""

from enum import Enum, auto


class TokenType(Enum):
    """Enumeração de todos os tipos de tokens léxicos da linguagem."""

    # Palavras reservadas (Keywords)
    KW_CLASS = auto()
    KW_DEF = auto()
    KW_SELF = auto()
    KW_IF = auto()
    KW_ELIF = auto()
    KW_ELSE = auto()
    KW_WHILE = auto()
    KW_RETURN = auto()
    KW_TRUE = auto()
    KW_FALSE = auto()
    KW_NONE = auto()

    # Identificadores
    IDENTIFIER = auto()

    # Literais
    INT_LITERAL = auto()
    FLOAT_LITERAL = auto()
    STRING_LITERAL = auto()

    # Operadores aritméticos e atribuição
    OP_PLUS = auto()        # +
    OP_MINUS = auto()       # -
    OP_MULT = auto()        # *
    OP_DIV = auto()         # /
    OP_ASSIGN = auto()      # =
    OP_ADD_ASSIGN = auto()  # +=
    OP_SUB_ASSIGN = auto()  # -=

    # Operadores relacionais
    OP_EQ = auto()          # ==
    OP_NEQ = auto()         # !=
    OP_LT = auto()          # <
    OP_LTE = auto()         # <=
    OP_GT = auto()          # >
    OP_GTE = auto()         # >=

    # Delimitadores
    COLON = auto()          # :
    LPAREN = auto()         # (
    RPAREN = auto()         # )

    # Controle sintético de blocos e fluxo
    INDENT = auto()
    DEDENT = auto()
    NEWLINE = auto()
    EOF = auto()
    ERROR = auto()
