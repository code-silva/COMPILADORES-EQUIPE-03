"""Testes da checagem e do registro de tipos em atribuições (#32)."""

import pytest

from src.parser import (
    AssignNode,
    BinOpNode,
    BoolLiteralNode,
    FloatLiteralNode,
    IdentifierNode,
    IntLiteralNode,
    StringLiteralNode,
)
from src.semantic import SemanticAnalyzer, SemanticError, Symbol


def assignment(
    target: str,
    value,
    *,
    op: str = "=",
    line: int = 0,
    column: int = 0,
) -> AssignNode:
    """Cria um ``AssignNode`` para os testes de atribuição."""
    return AssignNode(target=target, op=op, value=value, line=line, column=column)


def test_assignment_registers_new_symbol() -> None:
    """Garante que uma atribuição nova registra o símbolo com tipo e posição."""
    analyzer = SemanticAnalyzer()

    result = analyzer.visit_AssignNode(
        assignment("total", IntLiteralNode(value=10), line=3, column=5)
    )

    symbol = analyzer.global_scope.lookup("total")
    assert result == "int"
    assert symbol is not None
    assert symbol.type == "int"
    assert symbol.line == 3
    assert symbol.column == 5


def test_assignment_allows_int_to_float_coercion() -> None:
    """Permite atribuir int a uma variável já declarada como float."""
    analyzer = SemanticAnalyzer()
    analyzer.global_scope.define(Symbol(name="taxa", type="float", line=1))

    result = analyzer.visit_AssignNode(
        assignment("taxa", IntLiteralNode(value=2), line=4, column=8)
    )

    symbol = analyzer.global_scope.lookup("taxa")
    assert result == "int"
    assert symbol is not None
    assert symbol.type == "float"


@pytest.mark.parametrize(
    ("declared_type", "value"),
    [
        ("int", IntLiteralNode(value=1)),
        ("float", FloatLiteralNode(value=1.5)),
        ("String", StringLiteralNode(value="ok")),
        ("boolean", BoolLiteralNode(value=True)),
    ],
)
def test_assignment_accepts_compatible_types(declared_type: str, value) -> None:
    """Aceita atribuições com tipos equivalentes."""
    analyzer = SemanticAnalyzer()
    analyzer.global_scope.define(
        Symbol(name="valor", type=declared_type, line=1)
    )

    analyzer.visit_AssignNode(assignment("valor", value))

    symbol = analyzer.global_scope.lookup("valor")
    assert symbol is not None
    assert symbol.type == declared_type


@pytest.mark.parametrize(
    ("declared_type", "value", "value_type"),
    [
        ("int", StringLiteralNode(value="x"), "String"),
        ("int", FloatLiteralNode(value=1.5), "float"),
        ("float", StringLiteralNode(value="x"), "String"),
        ("String", IntLiteralNode(value=1), "int"),
        ("boolean", IntLiteralNode(value=1), "int"),
        ("None", BoolLiteralNode(value=True), "boolean"),
    ],
)
def test_assignment_rejects_incompatible_types(
    declared_type: str, value, value_type: str
) -> None:
    """Bloqueia atribuições incompatíveis informando tipos e posição."""
    analyzer = SemanticAnalyzer()
    analyzer.global_scope.define(
        Symbol(name="valor", type=declared_type, line=1)
    )

    with pytest.raises(SemanticError, match="Tipo incompatível na atribuição") as exc_info:
        analyzer.visit_AssignNode(
            assignment("valor", value, line=6, column=11)
        )

    message = str(exc_info.value)
    assert declared_type in message
    assert value_type in message
    assert exc_info.value.line == 6
    assert exc_info.value.column == 11


def test_assignment_registers_symbol_in_current_scope() -> None:
    """Garante que o novo símbolo pertence ao escopo ativo, sem vazar para o pai."""
    analyzer = SemanticAnalyzer()
    analyzer.enter_scope()

    analyzer.visit_AssignNode(assignment("local", IntLiteralNode(value=1)))

    assert analyzer.current_scope.lookup_current_scope("local") is not None
    assert analyzer.global_scope.lookup("local") is None


def test_assignment_to_outer_symbol_does_not_shadow_it() -> None:
    """Atribuições a variáveis visíveis no pai não criam símbolo local."""
    analyzer = SemanticAnalyzer()
    analyzer.global_scope.define(Symbol(name="x", type="int", line=1))
    analyzer.enter_scope()

    analyzer.visit_AssignNode(assignment("x", IntLiteralNode(value=2)))

    assert analyzer.current_scope.lookup_current_scope("x") is None
    assert analyzer.global_scope.lookup("x") is not None


def test_assignment_uses_inferred_binop_type() -> None:
    """Registra o tipo resultante de uma expressão binária atribuída."""
    analyzer = SemanticAnalyzer()

    analyzer.visit_AssignNode(
        assignment(
            "media",
            BinOpNode(
                left=IntLiteralNode(value=7),
                op="/",
                right=IntLiteralNode(value=2),
            ),
        )
    )

    symbol = analyzer.global_scope.lookup("media")
    assert symbol is not None
    assert symbol.type == "float"


def test_assignment_propagates_undeclared_identifier_location() -> None:
    """Propaga a posição do identificador não declarado no lado direito."""
    analyzer = SemanticAnalyzer()

    with pytest.raises(SemanticError, match="Variável 'origem' não declarada") as exc_info:
        analyzer.visit_AssignNode(
            assignment(
                "destino",
                IdentifierNode(name="origem", line=2, column=3),
                line=1,
                column=1,
            )
        )

    assert exc_info.value.line == 2
    assert exc_info.value.column == 3


def test_assignment_without_value_raises_semantic_error() -> None:
    """Garante erro controlado para atribuição sem expressão de valor."""
    analyzer = SemanticAnalyzer()

    with pytest.raises(SemanticError, match="Atribuição sem expressão") as exc_info:
        analyzer.visit_AssignNode(assignment("x", None, line=9, column=4))

    assert exc_info.value.line == 9
    assert exc_info.value.column == 4
