"""Suíte de Testes Unitários: Parser de Expressões e Precedência de Operadores (Issue #25).

Valida a classe ``Parser`` em ``src/parser/parser.py``, cobrindo:
1. Métodos auxiliares de navegação (``peek``, ``advance``, ``match``, ``expect``).
2. ``parse_primary()`` para literais, identificadores e keywords (``True``, ``False``, ``None``).
3. Expressões agrupadas por parênteses ``(expr)`` e aninhamentos.
4. Operadores unários prefixados (``+expr``, ``-expr``).
5. Precedência e associatividade à esquerda de operadores binários via Precedence Climbing.
"""

import pytest

from src.lexer.scanner import Scanner
from src.lexer.token import Token
from src.lexer.token_type import TokenType
from src.parser import (
    BinOpNode,
    BoolLiteralNode,
    FloatLiteralNode,
    IdentifierNode,
    IntLiteralNode,
    Node,
    NoneLiteralNode,
    Parser,
    ParserError,
    StringLiteralNode,
)


def tokenize(source_code: str) -> list[Token]:
    """Auxiliar para converter código-fonte em lista de tokens usando o Scanner."""
    scanner = Scanner(source_code)
    tokens: list[Token] = []
    while True:
        tok = scanner.next_token()
        tokens.append(tok)
        if tok.type == TokenType.EOF:
            break
    return tokens


def parse_expr(source_code: str) -> Node:
    """Auxiliar para instanciar o Parser com os tokens do Scanner e analisar uma expressão."""
    tokens = tokenize(source_code)
    parser = Parser(tokens)
    return parser.parse_expression()


# ==============================================================================
# 1. Navegação de Tokens (peek, advance, match, expect)
# ==============================================================================


def test_parser_navigation_helpers() -> None:
    """Verifica o funcionamento de peek(), advance(), match() e expect()."""
    tokens = tokenize("10 + 20")
    parser = Parser(tokens)

    assert parser.peek().type == TokenType.INT_LITERAL
    assert parser.peek().lexeme == "10"
    assert parser.peek(1).type == TokenType.OP_PLUS

    first = parser.advance()
    assert first.type == TokenType.INT_LITERAL
    assert parser.peek().type == TokenType.OP_PLUS

    assert parser.match(TokenType.OP_MINUS) is False
    assert parser.match(TokenType.OP_PLUS) is True

    second = parser.expect(TokenType.INT_LITERAL)
    assert second.lexeme == "20"
    assert parser.peek().type == TokenType.EOF


def test_parser_expect_raises_parser_error_on_mismatch() -> None:
    """Verifica que expect() lança ParserError com linha e coluna quando o token não corresponde."""
    tokens = tokenize("42")
    parser = Parser(tokens)

    with pytest.raises(ParserError) as exc_info:
        parser.expect(TokenType.RPAREN)

    assert exc_info.value.line == 1
    assert exc_info.value.column == 1


# ==============================================================================
# 2. Expressões Primárias: Literais, Identificadores e Keywords
# ==============================================================================


@pytest.mark.parametrize(
    ("source", "expected_value"),
    [
        ("0", 0),
        ("42", 42),
        ("1024", 1024),
    ],
)
def test_parse_primary_int_literal(source: str, expected_value: int) -> None:
    """Verifica que INT_LITERAL produz IntLiteralNode com valor e posição corretos."""
    node = parse_expr(source)
    assert isinstance(node, IntLiteralNode)
    assert node.value == expected_value
    assert node.line == 1
    assert node.column == 1


@pytest.mark.parametrize(
    ("source", "expected_value"),
    [
        ("3.14", 3.14),
        ("0.5", 0.5),
        ("100.0", 100.0),
    ],
)
def test_parse_primary_float_literal(source: str, expected_value: float) -> None:
    """Verifica que FLOAT_LITERAL produz FloatLiteralNode."""
    node = parse_expr(source)
    assert isinstance(node, FloatLiteralNode)
    assert node.value == pytest.approx(expected_value)
    assert node.line == 1
    assert node.column == 1


@pytest.mark.parametrize(
    ("source", "expected_value"),
    [
        ('"ola mundo"', "ola mundo"),
        ("'compiladores'", "compiladores"),
        ('""', ""),
    ],
)
def test_parse_primary_string_literal(source: str, expected_value: str) -> None:
    """Verifica que STRING_LITERAL produz StringLiteralNode."""
    node = parse_expr(source)
    assert isinstance(node, StringLiteralNode)
    assert node.value == expected_value
    assert node.line == 1
    assert node.column == 1


@pytest.mark.parametrize("identifier", ["x", "contador_1", "_temp", "totalGeral"])
def test_parse_primary_identifier(identifier: str) -> None:
    """Verifica que IDENTIFIER produz IdentifierNode."""
    node = parse_expr(identifier)
    assert isinstance(node, IdentifierNode)
    assert node.name == identifier
    assert node.line == 1
    assert node.column == 1


def test_parse_primary_keywords_true_false_none() -> None:
    """Verifica o mapeamento de KW_TRUE, KW_FALSE e KW_NONE para nós literais."""
    true_node = parse_expr("True")
    assert isinstance(true_node, BoolLiteralNode)
    assert true_node.value is True

    false_node = parse_expr("False")
    assert isinstance(false_node, BoolLiteralNode)
    assert false_node.value is False

    none_node = parse_expr("None")
    assert isinstance(none_node, NoneLiteralNode)
    assert none_node.line == 1
    assert none_node.column == 1


# ==============================================================================
# 3. Expressões Agrupadas com Parênteses
# ==============================================================================


def test_parse_parenthesized_single_literal() -> None:
    """Verifica que parênteses em torno de um literal retornam o nó interno."""
    node = parse_expr("(99)")
    assert isinstance(node, IntLiteralNode)
    assert node.value == 99


def test_parse_nested_parentheses() -> None:
    """Verifica que múltiplos níveis de parênteses são resolvidos corretamente."""
    node = parse_expr("(((variavel)))")
    assert isinstance(node, IdentifierNode)
    assert node.name == "variavel"


def test_parse_parentheses_override_precedence() -> None:
    """Verifica que (2 + 3) * 4 coloca a soma como filha esquerda da multiplicação."""
    node = parse_expr("(2 + 3) * 4")
    assert isinstance(node, BinOpNode)
    assert node.op == "*"

    assert isinstance(node.left, BinOpNode)
    assert node.left.op == "+"
    assert isinstance(node.left.left, IntLiteralNode)
    assert node.left.left.value == 2
    assert isinstance(node.left.right, IntLiteralNode)
    assert node.left.right.value == 3

    assert isinstance(node.right, IntLiteralNode)
    assert node.right.value == 4


def test_parse_unclosed_parenthesis_raises_parser_error() -> None:
    """Verifica que parêntese aberto sem fechamento lança ParserError."""
    with pytest.raises(ParserError):
        parse_expr("(2 + 3")


# ==============================================================================
# 4. Operadores Unários (+ e -)
# ==============================================================================


def test_parse_unary_minus_and_plus() -> None:
    """Verifica o parsing de operadores unários prefixados (-expr e +expr)."""
    neg_node = parse_expr("-15")
    assert isinstance(neg_node, BinOpNode)
    assert neg_node.op == "-"
    assert isinstance(neg_node.right, IntLiteralNode)
    assert neg_node.right.value == 15

    pos_node = parse_expr("+3.5")
    assert isinstance(pos_node, BinOpNode)
    assert pos_node.op == "+"
    assert isinstance(pos_node.right, FloatLiteralNode)
    assert pos_node.right.value == pytest.approx(3.5)


def test_parse_chained_unary_operators() -> None:
    """Verifica chamadas recursivas em parse_unary() como --x ou -+5."""
    node = parse_expr("--x")
    assert isinstance(node, BinOpNode)
    assert node.op == "-"
    assert isinstance(node.right, BinOpNode)
    assert node.right.op == "-"
    assert isinstance(node.right.right, IdentifierNode)
    assert node.right.right.name == "x"


def test_parse_unary_precedence_over_binary() -> None:
    """Verifica que o operador unário tem maior precedência que operadores binários (-2 * 3)."""
    node = parse_expr("-2 * 3")
    assert isinstance(node, BinOpNode)
    assert node.op == "*"
    assert isinstance(node.left, BinOpNode)
    assert node.left.op == "-"
    assert isinstance(node.left.right, IntLiteralNode)
    assert node.left.right.value == 2
    assert isinstance(node.right, IntLiteralNode)
    assert node.right.value == 3


# ==============================================================================
# 5. Precedência e Associatividade de Operadores Binários
# ==============================================================================


def test_multiplicative_precedence_over_additive() -> None:
    """Verifica que 2 + 3 * 4 agrupa 3 * 4 na sub-árvore direita da adição."""
    node = parse_expr("2 + 3 * 4")
    assert isinstance(node, BinOpNode)
    assert node.op == "+"
    assert isinstance(node.left, IntLiteralNode)
    assert node.left.value == 2

    assert isinstance(node.right, BinOpNode)
    assert node.right.op == "*"
    assert isinstance(node.right.left, IntLiteralNode)
    assert node.right.left.value == 3
    assert isinstance(node.right.right, IntLiteralNode)
    assert node.right.right.value == 4


def test_division_precedence_over_subtraction() -> None:
    """Verifica que 10 - 8 / 2 agrupa 8 / 2 na sub-árvore direita da subtração."""
    node = parse_expr("10 - 8 / 2")
    assert isinstance(node, BinOpNode)
    assert node.op == "-"
    assert isinstance(node.left, IntLiteralNode)
    assert node.left.value == 10

    assert isinstance(node.right, BinOpNode)
    assert node.right.op == "/"
    assert isinstance(node.right.left, IntLiteralNode)
    assert node.right.left.value == 8
    assert isinstance(node.right.right, IntLiteralNode)
    assert node.right.right.value == 2


def test_left_associativity_additive_operators() -> None:
    """Verifica que 10 - 3 - 2 é agrupado à esquerda como (10 - 3) - 2."""
    node = parse_expr("10 - 3 - 2")
    assert isinstance(node, BinOpNode)
    assert node.op == "-"

    assert isinstance(node.left, BinOpNode)
    assert node.left.op == "-"
    assert isinstance(node.left.left, IntLiteralNode)
    assert node.left.left.value == 10
    assert isinstance(node.left.right, IntLiteralNode)
    assert node.left.right.value == 3

    assert isinstance(node.right, IntLiteralNode)
    assert node.right.value == 2


def test_left_associativity_multiplicative_operators() -> None:
    """Verifica que 24 / 4 * 2 é agrupado à esquerda como (24 / 4) * 2."""
    node = parse_expr("24 / 4 * 2")
    assert isinstance(node, BinOpNode)
    assert node.op == "*"

    assert isinstance(node.left, BinOpNode)
    assert node.left.op == "/"
    assert isinstance(node.left.left, IntLiteralNode)
    assert node.left.left.value == 24
    assert isinstance(node.left.right, IntLiteralNode)
    assert node.left.right.value == 4

    assert isinstance(node.right, IntLiteralNode)
    assert node.right.value == 2


@pytest.mark.parametrize("rel_op", ["==", "!=", "<", "<=", ">", ">="])
def test_relational_operators_lower_precedence_than_arithmetic(rel_op: str) -> None:
    """Verifica que operadores relacionais têm menor precedência que aritméticos."""
    node = parse_expr(f"a + 1 {rel_op} b * 2")
    assert isinstance(node, BinOpNode)
    assert node.op == rel_op

    assert isinstance(node.left, BinOpNode)
    assert node.left.op == "+"
    assert isinstance(node.left.left, IdentifierNode)
    assert node.left.left.name == "a"
    assert isinstance(node.left.right, IntLiteralNode)
    assert node.left.right.value == 1

    assert isinstance(node.right, BinOpNode)
    assert node.right.op == "*"
    assert isinstance(node.right.left, IdentifierNode)
    assert node.right.left.name == "b"
    assert isinstance(node.right.right, IntLiteralNode)
    assert node.right.right.value == 2


def test_invalid_primary_token_raises_parser_error() -> None:
    """Verifica que um operador binário sem operando esquerdo lança ParserError."""
    with pytest.raises(ParserError) as exc_info:
        parse_expr("* 5")

    assert exc_info.value.line == 1
    assert exc_info.value.column == 1
