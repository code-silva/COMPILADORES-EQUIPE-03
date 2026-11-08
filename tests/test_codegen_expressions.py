"""Testes unitários da geração de código Java para expressões (Issue #35).

Valida a conversão de literais (IntLiteralNode, FloatLiteralNode,
StringLiteralNode, BoolLiteralNode, NoneLiteralNode), identificadores
(IdentifierNode) e expressões binárias/unárias (BinOpNode) para a sintaxe
estrita de Java via ``CodeGenerator.gen_expression()``.
"""

import pytest

from src.codegen import CodeGenerator
from src.parser import (
    BinOpNode,
    BoolLiteralNode,
    FloatLiteralNode,
    IdentifierNode,
    IntLiteralNode,
    Node,
    NoneLiteralNode,
    Parser,
    StringLiteralNode,
)


def gen_expr(node: Node) -> str:
    """Atalho para invocar CodeGenerator().gen_expression(node)."""
    return CodeGenerator().gen_expression(node)


# ==============================================================================
# 1. Literais e Identificadores
# ==============================================================================


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (0, "0"),
        (1, "1"),
        (42, "42"),
        (999999, "999999"),
    ],
)
def test_gen_expression_int_literal(value: int, expected: str) -> None:
    """Verifica conversão de IntLiteralNode para representação inteira em Java."""
    assert gen_expr(IntLiteralNode(value=value)) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (0.0, "0.0"),
        (3.14, "3.14"),
        (0.5, "0.5"),
        (123.456, "123.456"),
    ],
)
def test_gen_expression_float_literal(value: float, expected: str) -> None:
    """Verifica conversão de FloatLiteralNode para ponto flutuante em Java."""
    assert gen_expr(FloatLiteralNode(value=value)) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("ola", '"ola"'),
        ("", '""'),
        ("PyToJava 1.0", '"PyToJava 1.0"'),
        ('texto com "aspas"', r'"texto com \"aspas\""'),
        ("linha1\nlinha2", r'"linha1\nlinha2"'),
        ("caminho\\arquivo", r'"caminho\\arquivo"'),
    ],
)
def test_gen_expression_string_literal(value: str, expected: str) -> None:
    """Verifica que StringLiteralNode gera literais entre aspas duplas em Java."""
    assert gen_expr(StringLiteralNode(value=value)) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (True, "true"),
        (False, "false"),
    ],
)
def test_gen_expression_bool_literal(value: bool, expected: str) -> None:
    """Verifica tradução de BoolLiteralNode (True -> 'true', False -> 'false')."""
    assert gen_expr(BoolLiteralNode(value=value)) == expected


def test_gen_expression_none_literal() -> None:
    """Verifica tradução de NoneLiteralNode para 'null' em Java."""
    assert gen_expr(NoneLiteralNode()) == "null"


@pytest.mark.parametrize(
    "name",
    ["x", "contador_1", "_temp", "totalGeral"],
)
def test_gen_expression_identifier(name: str) -> None:
    """Verifica que IdentifierNode retorna exatamente o nome do identificador."""
    assert gen_expr(IdentifierNode(name=name)) == name


# ==============================================================================
# 2. Expressões Binárias Simples (Aritméticas e Relacionais)
# ==============================================================================


@pytest.mark.parametrize("op", ["+", "-", "*", "/", "%"])
def test_gen_expression_simple_arithmetic_binop(op: str) -> None:
    """Verifica formatação de BinOpNode aritmético simples com parênteses."""
    node = BinOpNode(
        left=IntLiteralNode(value=10),
        op=op,
        right=IntLiteralNode(value=5),
    )
    assert gen_expr(node) == f"(10 {op} 5)"


@pytest.mark.parametrize("op", ["==", "!=", "<", "<=", ">", ">="])
def test_gen_expression_simple_relational_binop(op: str) -> None:
    """Verifica formatação de BinOpNode relacional simples com parênteses."""
    node = BinOpNode(
        left=IdentifierNode(name="a"),
        op=op,
        right=IntLiteralNode(value=0),
    )
    assert gen_expr(node) == f"(a {op} 0)"


def test_gen_expression_string_concatenation() -> None:
    """Verifica geração de concatenação de strings em Java."""
    node = BinOpNode(
        left=StringLiteralNode(value="Hello, "),
        op="+",
        right=IdentifierNode(name="nome"),
    )
    assert gen_expr(node) == '("Hello, " + nome)'


def test_gen_expression_boolean_comparison() -> None:
    """Verifica comparação envolvendo literais booleanos traduzidos para Java."""
    node = BinOpNode(
        left=IdentifierNode(name="ativo"),
        op="==",
        right=BoolLiteralNode(value=True),
    )
    assert gen_expr(node) == "(ativo == true)"


# ==============================================================================
# 3. Expressões Complexas Aninhadas e Integração com o Parser
# ==============================================================================


def test_gen_expression_nested_precedence_tree() -> None:
    """Verifica aninhamento recursivo preservando precedência: 2 + 3 * 4 -> (2 + (3 * 4))."""
    node = BinOpNode(
        left=IntLiteralNode(value=2),
        op="+",
        right=BinOpNode(
            left=IntLiteralNode(value=3),
            op="*",
            right=IntLiteralNode(value=4),
        ),
    )
    assert gen_expr(node) == "(2 + (3 * 4))"


def test_gen_expression_from_parsed_parenthesized_expression() -> None:
    """Verifica integração com Parser para '(2 + 3) * 4' -> '((2 + 3) * 4)'."""
    expr_node = Parser("(2 + 3) * 4").parse_expression()
    assert gen_expr(expr_node) == "((2 + 3) * 4)"


def test_gen_expression_from_parsed_unary_and_binary_expression() -> None:
    """Verifica geração de código para operadores unários (representados na AST como 0 - x)."""
    expr_node = Parser("-x + 5").parse_expression()
    assert gen_expr(expr_node) == "((0 - x) + 5)"


def test_gen_expression_complex_arithmetic_and_relational() -> None:
    """Verifica expressão complexa combinando variáveis, floats, aritmética e relacional."""
    expr_node = Parser("(nota1 + nota2) / 2.0 >= 7.0").parse_expression()
    assert gen_expr(expr_node) == "(((nota1 + nota2) / 2.0) >= 7.0)"


# ==============================================================================
# 4. Casos de Erro e Validação Defensiva
# ==============================================================================


def test_gen_expression_incomplete_binop_raises_value_error() -> None:
    """Garante ValueError se BinOpNode tiver operando left ou right ausente."""
    node = BinOpNode(left=IntLiteralNode(value=1), op="+", right=None)
    with pytest.raises(ValueError, match="ambos os operandos"):
        gen_expr(node)


def test_gen_expression_unsupported_node_raises_value_error() -> None:
    """Garante ValueError ao tentar converter um nó genérico que não é expressão."""
    with pytest.raises(ValueError, match="Nó de expressão não suportado"):
        gen_expr(Node())
