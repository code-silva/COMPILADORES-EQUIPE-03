"""Testes da inferência e compatibilidade de tipos em expressões binárias (#32)."""

import pytest

from src.parser import (
    BinOpNode,
    BoolLiteralNode,
    FloatLiteralNode,
    IdentifierNode,
    IntLiteralNode,
    StringLiteralNode,
)
from src.semantic import SemanticAnalyzer, SemanticError, Symbol


def infer_binop(
    op: str,
    left,
    right,
    *,
    line: int = 0,
    column: int = 0,
) -> str:
    """Cria e infere o tipo de um ``BinOpNode`` usando um analisador vazio."""
    node = BinOpNode(left=left, op=op, right=right, line=line, column=column)
    return SemanticAnalyzer().infer_type(node)


@pytest.mark.parametrize(
    ("op", "left", "right", "expected"),
    [
        ("+", IntLiteralNode(value=1), IntLiteralNode(value=2), "int"),
        ("-", IntLiteralNode(value=1), IntLiteralNode(value=2), "int"),
        ("*", IntLiteralNode(value=1), IntLiteralNode(value=2), "int"),
        ("%", IntLiteralNode(value=1), IntLiteralNode(value=2), "int"),
        ("/", IntLiteralNode(value=1), IntLiteralNode(value=2), "float"),
        ("+", FloatLiteralNode(value=1.0), FloatLiteralNode(value=2.0), "float"),
        ("+", IntLiteralNode(value=1), FloatLiteralNode(value=2.0), "float"),
        ("+", FloatLiteralNode(value=1.0), IntLiteralNode(value=2), "float"),
        ("-", IntLiteralNode(value=1), FloatLiteralNode(value=2.0), "float"),
        ("*", FloatLiteralNode(value=1.0), IntLiteralNode(value=2), "float"),
        ("/", IntLiteralNode(value=1), FloatLiteralNode(value=2.0), "float"),
        ("/", FloatLiteralNode(value=1.0), IntLiteralNode(value=2), "float"),
        ("%", IntLiteralNode(value=1), FloatLiteralNode(value=2.0), "float"),
        (
            "+",
            StringLiteralNode(value="a"),
            StringLiteralNode(value="b"),
            "String",
        ),
    ],
)
def test_arithmetic_type_inference(op, left, right, expected: str) -> None:
    """Valida os resultados e as promoções dos operadores aritméticos."""
    assert infer_binop(op, left, right) == expected


@pytest.mark.parametrize("op", ["==", "!=", "<", ">", "<=", ">="])
@pytest.mark.parametrize(
    ("left", "right"),
    [
        (IntLiteralNode(value=1), IntLiteralNode(value=2)),
        (FloatLiteralNode(value=1.0), FloatLiteralNode(value=2.0)),
        (IntLiteralNode(value=1), FloatLiteralNode(value=2.0)),
        (FloatLiteralNode(value=1.0), IntLiteralNode(value=2)),
        (BoolLiteralNode(value=True), BoolLiteralNode(value=False)),
    ],
)
def test_comparison_type_inference(op, left, right) -> None:
    """Valida que comparações entre tipos compatíveis resultam em boolean."""
    assert infer_binop(op, left, right) == "boolean"


@pytest.mark.parametrize(
    ("op", "left", "right", "types_in_message"),
    [
        ("+", IntLiteralNode(value=1), StringLiteralNode(value="x"), ("int", "String")),
        ("*", BoolLiteralNode(value=True), FloatLiteralNode(value=1.0), ("boolean", "float")),
        ("-", StringLiteralNode(value="a"), StringLiteralNode(value="b"), ("String",)),
        ("<", IntLiteralNode(value=1), StringLiteralNode(value="x"), ("int", "String")),
    ],
)
def test_incompatible_operations_raise_semantic_error(
    op, left, right, types_in_message
) -> None:
    """Garante erro tipado, com tipos e coordenadas exatas do BinOpNode."""
    node = BinOpNode(left=left, op=op, right=right, line=5, column=9)

    with pytest.raises(SemanticError) as exc_info:
        SemanticAnalyzer().infer_type(node)

    for type_name in types_in_message:
        assert type_name in str(exc_info.value)
    assert exc_info.value.line == 5
    assert exc_info.value.column == 9


def test_nested_binop_promotes_types() -> None:
    """Valida a inferência recursiva em expressões binárias aninhadas."""
    node = BinOpNode(
        left=BinOpNode(
            left=IntLiteralNode(value=1),
            op="+",
            right=FloatLiteralNode(value=2.5),
        ),
        op="*",
        right=IntLiteralNode(value=3),
    )

    assert SemanticAnalyzer().infer_type(node) == "float"


def test_binop_resolves_identifier_types() -> None:
    """Valida a inferência de operandos resolvidos na tabela de símbolos."""
    analyzer = SemanticAnalyzer()
    analyzer.current_scope.define(Symbol(name="peso", type="float", line=1))

    node = BinOpNode(
        left=IdentifierNode(name="peso"),
        op="*",
        right=IntLiteralNode(value=2),
    )

    assert analyzer.infer_type(node) == "float"


def test_binop_with_missing_operand_raises_semantic_error() -> None:
    """Garante erro controlado quando um operando binário está ausente."""
    node = BinOpNode(left=IntLiteralNode(value=1), op="+", line=7, column=2)

    with pytest.raises(SemanticError, match="operando ausente") as exc_info:
        SemanticAnalyzer().infer_type(node)

    assert exc_info.value.line == 7
    assert exc_info.value.column == 2


def test_binop_with_unsupported_operator_raises_semantic_error() -> None:
    """Garante erro controlado para operadores não mapeados pelo analisador."""
    node = BinOpNode(
        left=IntLiteralNode(value=1),
        op="**",
        right=IntLiteralNode(value=2),
        line=3,
        column=4,
    )

    with pytest.raises(SemanticError, match="Operador binário não suportado"):
        SemanticAnalyzer().infer_type(node)
