"""Suíte de Testes Unitários: Nós da AST (Issues #20 e #23).

Valida a classe base ``Node`` (com ``kw_only=True``), o nó raiz ``ProgramNode``,
o nó de expressões binárias ``BinOpNode`` (operadores aritméticos, relacionais e
aninhamento recursivo para precedência), a rastreabilidade de coordenadas
(``line`` e ``column``) e a herança.
"""

from dataclasses import dataclass

import pytest

from src.parser import BinOpNode, Node, ProgramNode


def test_node_default_instantiation() -> None:
    """Verifica instanciação padrão de Node com line=0 e column=0."""
    node = Node()
    assert node.line == 0
    assert node.column == 0


def test_node_custom_position_keyword_only() -> None:
    """Verifica que Node aceita line e column por keyword e rejeita argumentos posicionais."""
    node = Node(line=10, column=4)
    assert node.line == 10
    assert node.column == 4

    with pytest.raises(TypeError):
        Node(10, 4)  # type: ignore[misc]


def test_program_node_default_instantiation() -> None:
    """Verifica instanciação de ProgramNode padrão (stmts=[], line=0, column=0)."""
    program = ProgramNode()
    assert program.stmts == []
    assert program.line == 0
    assert program.column == 0


def test_program_node_mutable_default_isolation() -> None:
    """Garante que listas padrão de stmts não sejam compartilhadas entre instâncias."""
    prog_a = ProgramNode()
    prog_b = ProgramNode()
    prog_a.stmts.append(Node(line=1, column=1))

    assert len(prog_a.stmts) == 1
    assert prog_b.stmts == []


def test_program_node_with_custom_elements_and_positions() -> None:
    """Verifica instanciação de ProgramNode contendo elementos e posições customizadas."""
    stmt1 = Node(line=1, column=1)
    stmt2 = Node(line=2, column=5)

    program = ProgramNode(stmts=[stmt1, stmt2], line=1, column=1)

    assert len(program.stmts) == 2
    assert program.stmts[0] == stmt1
    assert program.stmts[1] == stmt2
    assert program.line == 1
    assert program.column == 1


def test_program_node_positional_stmts() -> None:
    """Verifica que ProgramNode permite passar stmts posicionalmente graças ao kw_only na base."""
    stmt = Node(line=3, column=2)
    program = ProgramNode([stmt], line=3, column=2)

    assert program.stmts == [stmt]
    assert program.line == 3
    assert program.column == 2


def test_program_node_inheritance() -> None:
    """Valida a relação de herança com isinstance(ProgramNode(), Node)."""
    program = ProgramNode()
    assert isinstance(program, Node)
    assert issubclass(ProgramNode, Node)


def test_kw_only_allows_subclasses_with_positional_and_default_fields() -> None:
    """Garante que kw_only permite criar subclasses sem conflito na ordem de atributos padrão."""

    @dataclass
    class DummyLiteralNode(Node):
        value: int
        raw: str = ""

    lit = DummyLiteralNode(42, line=5, column=12)
    assert isinstance(lit, Node)
    assert lit.value == 42
    assert lit.raw == ""
    assert lit.line == 5
    assert lit.column == 12


# ==============================================================================
# Testes de BinOpNode (Issue #23)
# ==============================================================================


def test_binop_node_default_instantiation() -> None:
    """Verifica instanciação padrão de BinOpNode (left=None, op='', right=None, line=0, column=0)."""
    node = BinOpNode()
    assert isinstance(node, Node)
    assert node.left is None
    assert node.op == ""
    assert node.right is None
    assert node.line == 0
    assert node.column == 0


@pytest.mark.parametrize("operator", ["+", "-", "*", "/"])
def test_binop_node_arithmetic_operators(operator: str) -> None:
    """Valida a criação de BinOpNode com todos os operadores aritméticos (+, -, *, /)."""
    left_operand = Node(line=1, column=1)
    right_operand = Node(line=1, column=5)

    expr = BinOpNode(left=left_operand, op=operator, right=right_operand, line=1, column=3)

    assert expr.left == left_operand
    assert expr.op == operator
    assert expr.right == right_operand
    assert expr.line == 1
    assert expr.column == 3


@pytest.mark.parametrize("operator", ["==", "!=", "<", "<=", ">", ">="])
def test_binop_node_relational_operators(operator: str) -> None:
    """Valida a criação de BinOpNode com todos os operadores relacionais (==, !=, <, <=, >, >=)."""
    left_operand = Node(line=2, column=4)
    right_operand = Node(line=2, column=10)

    expr = BinOpNode(left_operand, operator, right_operand, line=2, column=6)

    assert expr.left == left_operand
    assert expr.op == operator
    assert expr.right == right_operand
    assert expr.line == 2
    assert expr.column == 6


def test_binop_node_right_nesting_precedence() -> None:
    """Testa aninhamento em right simulando a precedência de '2 + 3 * 4'."""

    @dataclass
    class IntStub(Node):
        value: int = 0

    two = IntStub(2, line=1, column=1)
    three = IntStub(3, line=1, column=5)
    four = IntStub(4, line=1, column=9)

    mult_node = BinOpNode(left=three, op="*", right=four, line=1, column=7)
    root_node = BinOpNode(left=two, op="+", right=mult_node, line=1, column=3)

    assert root_node.op == "+"
    assert root_node.left == two
    assert isinstance(root_node.right, BinOpNode)
    assert root_node.right.op == "*"
    assert root_node.right.left == three
    assert root_node.right.right == four


def test_binop_node_left_nesting_and_relational_combination() -> None:
    """Testa aninhamento em left e combinação aritmética/relacional simulando '(10 - 2) / 4 <= 5'."""

    @dataclass
    class IntStub(Node):
        value: int = 0

    sub_node = BinOpNode(
        left=IntStub(10, line=1, column=2),
        op="-",
        right=IntStub(2, line=1, column=7),
        line=1,
        column=5,
    )
    div_node = BinOpNode(
        left=sub_node,
        op="/",
        right=IntStub(4, line=1, column=12),
        line=1,
        column=10,
    )
    rel_node = BinOpNode(
        left=div_node,
        op="<=",
        right=IntStub(5, line=1, column=17),
        line=1,
        column=14,
    )

    assert rel_node.op == "<="
    assert isinstance(rel_node.left, BinOpNode)
    assert rel_node.left.op == "/"
    assert isinstance(rel_node.left.left, BinOpNode)
    assert rel_node.left.left.op == "-"
