"""Suíte de Testes Unitários: Casos Felizes do Lexer (Issue #9).

Valida o reconhecimento correto de todos os tokens válidos do subconjunto
procedural do Python: palavras-chave, identificadores, literais, operadores,
delimitadores, comentários e rastreabilidade de coordenadas (linha e coluna).
"""

import pytest

from src.lexer.scanner import Scanner
from src.lexer.token import Token
from src.lexer.token_type import TokenType


def scan_all(source_code: str) -> list[Token]:
    """Utilitário para coletar todos os tokens gerados até EOF."""
    scanner = Scanner(source_code)
    tokens: list[Token] = []
    while True:
        token = scanner.next_token()
        tokens.append(token)
        if token.type == TokenType.EOF:
            break
    return tokens


def get_token_types(source_code: str) -> list[TokenType]:
    """Utilitário para extrair apenas a sequência de tipos dos tokens."""
    return [token.type for token in scan_all(source_code)]


# ==============================================================================
# 1. Palavras-Chave e Identificadores
# ==============================================================================

@pytest.mark.parametrize(
    ("keyword", "expected_type"),
    [
        ("def", TokenType.KW_DEF),
        ("if", TokenType.KW_IF),
        ("elif", TokenType.KW_ELIF),
        ("else", TokenType.KW_ELSE),
        ("while", TokenType.KW_WHILE),
        ("return", TokenType.KW_RETURN),
        ("True", TokenType.KW_TRUE),
        ("False", TokenType.KW_FALSE),
        ("None", TokenType.KW_NONE),
        ("class", TokenType.KW_CLASS),
        ("self", TokenType.KW_SELF),
    ],
)
def test_keywords_recognition(keyword: str, expected_type: TokenType) -> None:
    """Verifica se todas as palavras-chave são devidamente mapeadas."""
    tokens = scan_all(keyword)
    assert len(tokens) == 2  # KEYWORD + EOF
    assert tokens[0].type == expected_type
    assert tokens[0].lexeme == keyword


@pytest.mark.parametrize(
    "identifier",
    [
        "x",
        "variavel_1",
        "totalGeral",
        "_contador",
        "__interno__",
        "valor25",
        "soma_dos_quadrados",
    ],
)
def test_valid_identifiers(identifier: str) -> None:
    """Verifica se identificadores comuns são reconhecidos como IDENTIFIER."""
    tokens = scan_all(identifier)
    assert len(tokens) == 2  # IDENTIFIER + EOF
    assert tokens[0].type == TokenType.IDENTIFIER
    assert tokens[0].lexeme == identifier
    assert tokens[0].literal is None


@pytest.mark.parametrize(
    "pseudo_keyword",
    [
        "define",
        "def_func",
        "ifx",
        "while_loop",
        "return_val",
        "TrueValue",
        "Falsehood",
        "NoneType",
        "DEF",
        "If",
        "WHILE",
    ],
)
def test_keywords_not_matched_on_prefixes_or_casing(pseudo_keyword: str) -> None:
    """Verifica case-sensitivity e palavras que têm keywords como prefixo."""
    tokens = scan_all(pseudo_keyword)
    assert tokens[0].type == TokenType.IDENTIFIER
    assert tokens[0].lexeme == pseudo_keyword


# ==============================================================================
# 2. Literais (Inteiros, Floats, Strings)
# ==============================================================================

@pytest.mark.parametrize(
    ("source", "expected_val"),
    [
        ("0", 0),
        ("42", 42),
        ("1000", 1000),
        ("999999", 999999),
    ],
)
def test_int_literals(source: str, expected_val: int) -> None:
    """Verifica o reconhecimento de literais inteiros e conversão de valor."""
    tokens = scan_all(source)
    assert tokens[0].type == TokenType.INT_LITERAL
    assert tokens[0].lexeme == source
    assert tokens[0].literal == expected_val


@pytest.mark.parametrize(
    ("source", "expected_val"),
    [
        ("0.0", 0.0),
        ("3.14", 3.14),
        ("0.5", 0.5),
        ("123.456", 123.456),
    ],
)
def test_float_literals(source: str, expected_val: float) -> None:
    """Verifica o reconhecimento de ponto flutuante e conversão de valor."""
    tokens = scan_all(source)
    assert tokens[0].type == TokenType.FLOAT_LITERAL
    assert tokens[0].lexeme == source
    assert tokens[0].literal == pytest.approx(expected_val)


@pytest.mark.parametrize(
    ("source", "expected_literal"),
    [
        ('"ola"', "ola"),
        ("'mundo'", "mundo"),
        ('""', ""),
        ("''", ""),
        ('"com espacos no meio"', "com espacos no meio"),
        (r'"com \"escape\""', 'com "escape"'),
        (r"'com \'escape\''", "com 'escape'"),
        (r'"linha 1\nlinha 2"', "linha 1\nlinha 2"),
        (r'"barra \\ invertida"', "barra \\ invertida"),
    ],
)
def test_string_literals(source: str, expected_literal: str) -> None:
    """Verifica literais de string com aspas simples, duplas e escapes."""
    tokens = scan_all(source)
    assert tokens[0].type == TokenType.STRING_LITERAL
    assert tokens[0].literal == expected_literal


# ==============================================================================
# 3. Operadores e Delimitadores
# ==============================================================================

@pytest.mark.parametrize(
    ("op_str", "expected_type"),
    [
        ("+", TokenType.OP_PLUS),
        ("-", TokenType.OP_MINUS),
        ("*", TokenType.OP_MULT),
        ("/", TokenType.OP_DIV),
        ("=", TokenType.OP_ASSIGN),
        ("+=", TokenType.OP_ADD_ASSIGN),
        ("-=", TokenType.OP_SUB_ASSIGN),
        ("==", TokenType.OP_EQ),
        ("!=", TokenType.OP_NEQ),
        ("<", TokenType.OP_LT),
        ("<=", TokenType.OP_LTE),
        (">", TokenType.OP_GT),
        (">=", TokenType.OP_GTE),
        (":", TokenType.COLON),
        ("(", TokenType.LPAREN),
        (")", TokenType.RPAREN),
    ],
)
def test_operators_and_delimiters(op_str: str, expected_type: TokenType) -> None:
    """Verifica todos os operadores aritméticos, relacionais, de atribuição e delimitadores."""
    tokens = scan_all(op_str)
    assert tokens[0].type == expected_type
    assert tokens[0].lexeme == op_str


def test_compound_operator_maximal_munch() -> None:
    """Garante que operadores compostos (<=, >=, ==, +=, -=) não sejam divididos em dois."""
    cases = [
        ("<=", TokenType.OP_LTE),
        (">=", TokenType.OP_GTE),
        ("==", TokenType.OP_EQ),
        ("!=", TokenType.OP_NEQ),
        ("+=", TokenType.OP_ADD_ASSIGN),
        ("-=", TokenType.OP_SUB_ASSIGN),
    ]
    for src, expected_type in cases:
        tokens = scan_all(src)
        assert len(tokens) == 2  # [TOKEN, EOF]
        assert tokens[0].type == expected_type
        assert tokens[0].lexeme == src


# ==============================================================================
# 4. Comentários e Espaços em Branco
# ==============================================================================

def test_full_line_comment_ignored() -> None:
    """Garante que linhas inteiras com comentários não geram tokens."""
    source = "# este comentário deve ser completamente descartado\n"
    tokens = scan_all(source)
    assert len(tokens) == 1
    assert tokens[0].type == TokenType.EOF


def test_inline_comment_ignored() -> None:
    """Garante que comentários ao final de linha não afetam o código anterior."""
    source = "total = 100  # atribui valor total\n"
    expected = [
        TokenType.IDENTIFIER,
        TokenType.OP_ASSIGN,
        TokenType.INT_LITERAL,
        TokenType.NEWLINE,
        TokenType.EOF,
    ]
    assert get_token_types(source) == expected


def test_multiple_spaces_and_tabs_ignored() -> None:
    """Verifica se múltiplos espaços e tabulações no meio da linha são ignorados."""
    source = "x    + \t \t  y"
    expected = [
        TokenType.IDENTIFIER,
        TokenType.OP_PLUS,
        TokenType.IDENTIFIER,
        TokenType.EOF,
    ]
    assert get_token_types(source) == expected


# ==============================================================================
# 5. Rastreabilidade de Coordenadas (Linha e Coluna)
# ==============================================================================

def test_token_coordinates_single_line() -> None:
    """Valida se line e column refletem exatamente as coordenadas no código-fonte."""
    # Colunas: 1:x, 3:=, 5:42
    source = "x = 42"
    tokens = scan_all(source)

    assert tokens[0].type == TokenType.IDENTIFIER
    assert tokens[0].lexeme == "x"
    assert (tokens[0].line, tokens[0].column) == (1, 1)

    assert tokens[1].type == TokenType.OP_ASSIGN
    assert tokens[1].lexeme == "="
    assert (tokens[1].line, tokens[1].column) == (1, 3)

    assert tokens[2].type == TokenType.INT_LITERAL
    assert tokens[2].lexeme == "42"
    assert (tokens[2].line, tokens[2].column) == (1, 5)


def test_token_coordinates_multiline() -> None:
    """Valida line e column através de múltiplas linhas de instruções."""
    source = (
        "a = 10\n"
        "b = 20.5\n"
    )
    tokens = scan_all(source)

    # Linha 1
    assert tokens[0].lexeme == "a"
    assert (tokens[0].line, tokens[0].column) == (1, 1)
    assert tokens[1].lexeme == "="
    assert (tokens[1].line, tokens[1].column) == (1, 3)
    assert tokens[2].lexeme == "10"
    assert (tokens[2].line, tokens[2].column) == (1, 5)
    assert tokens[3].type == TokenType.NEWLINE

    # Linha 2
    assert tokens[4].lexeme == "b"
    assert (tokens[4].line, tokens[4].column) == (2, 1)
    assert tokens[5].lexeme == "="
    assert (tokens[5].line, tokens[5].column) == (2, 3)
    assert tokens[6].lexeme == "20.5"
    assert (tokens[6].line, tokens[6].column) == (2, 5)
    assert tokens[7].type == TokenType.NEWLINE


# ==============================================================================
# 6. Programas Procedurais Completos (Happy Path Integrado)
# ==============================================================================

def test_happy_path_function_definition() -> None:
    """Valida tokenização de uma função procedural bem-formada com recuo."""
    source = (
        "def calcular_dobro(numero):\n"
        "    return numero * 2\n"
    )
    expected_sequence = [
        TokenType.KW_DEF,
        TokenType.IDENTIFIER,
        TokenType.LPAREN,
        TokenType.IDENTIFIER,
        TokenType.RPAREN,
        TokenType.COLON,
        TokenType.NEWLINE,
        TokenType.INDENT,
        TokenType.KW_RETURN,
        TokenType.IDENTIFIER,
        TokenType.OP_MULT,
        TokenType.INT_LITERAL,
        TokenType.NEWLINE,
        TokenType.DEDENT,
        TokenType.EOF,
    ]
    assert get_token_types(source) == expected_sequence


def test_happy_path_while_loop_with_compound_operator() -> None:
    """Valida tokenização de um loop while com operadores relacionais e de atribuição."""
    source = (
        "while contador <= 10:\n"
        "    contador += 1\n"
    )
    expected_sequence = [
        TokenType.KW_WHILE,
        TokenType.IDENTIFIER,
        TokenType.OP_LTE,
        TokenType.INT_LITERAL,
        TokenType.COLON,
        TokenType.NEWLINE,
        TokenType.INDENT,
        TokenType.IDENTIFIER,
        TokenType.OP_ADD_ASSIGN,
        TokenType.INT_LITERAL,
        TokenType.NEWLINE,
        TokenType.DEDENT,
        TokenType.EOF,
    ]
    assert get_token_types(source) == expected_sequence


def test_happy_path_conditional_statement() -> None:
    """Valida tokenização de estrutura condicional if/else."""
    source = (
        "if ativo == True:\n"
        "    resultado = 1\n"
        "else:\n"
        "    resultado = 0\n"
    )
    expected_sequence = [
        TokenType.KW_IF,
        TokenType.IDENTIFIER,
        TokenType.OP_EQ,
        TokenType.KW_TRUE,
        TokenType.COLON,
        TokenType.NEWLINE,
        TokenType.INDENT,
        TokenType.IDENTIFIER,
        TokenType.OP_ASSIGN,
        TokenType.INT_LITERAL,
        TokenType.NEWLINE,
        TokenType.DEDENT,
        TokenType.KW_ELSE,
        TokenType.COLON,
        TokenType.NEWLINE,
        TokenType.INDENT,
        TokenType.IDENTIFIER,
        TokenType.OP_ASSIGN,
        TokenType.INT_LITERAL,
        TokenType.NEWLINE,
        TokenType.DEDENT,
        TokenType.EOF,
    ]
    assert get_token_types(source) == expected_sequence
