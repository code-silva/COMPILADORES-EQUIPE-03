"""Suíte de Testes Unitários: Nós da AST (Issues #20 e #23).

Valida a classe base ``Node`` (com ``kw_only=True``), o nó raiz ``ProgramNode``,
o nó de expressões binárias ``BinOpNode`` (operadores aritméticos, relacionais e
aninhamento recursivo para precedência), a rastreabilidade de coordenadas
(``line`` e ``column``) e a herança.
"""
from dataclasses import dataclass

import pytest

from src.parser import (
    AssignNode,
    BinOpNode,
    ElifClauseNode,
    ElseClauseNode,
    IfNode,
    Node,
    ProgramNode,
    ReturnNode,
    WhileNode,
)


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


def test_assign_node_instantiation() -> None:
    """Verifica instanciação e herança de AssignNode."""
    val_node = Node(line=1, column=10)
    assign = AssignNode(target="x", op="=", value=val_node, line=1, column=5)

    assert isinstance(assign, Node)
    assert assign.target == "x"
    assert assign.op == "="
    assert assign.value == val_node
    assert assign.line == 1
    assert assign.column == 5


@pytest.mark.parametrize("op", ["=", "+=", "-="])
def test_assign_node_operators(op: str) -> None:
    """Valida AssignNode com diferentes operadores de atribuição (=, +=, -=)."""
    val_node = Node(line=1, column=5)
    assign = AssignNode(target="var", op=op, value=val_node, line=1, column=1)

    assert isinstance(assign, Node)
    assert isinstance(assign, AssignNode)
    assert assign.target == "var"
    assert assign.op == op
    assert assign.value == val_node
    assert assign.line == 1
    assert assign.column == 1


def test_return_node_instantiation() -> None:
    """Verifica instanciação e herança de ReturnNode."""
    val_node = Node(line=2, column=12)
    ret = ReturnNode(value=val_node, line=2, column=5)

    assert isinstance(ret, Node)
    assert ret.value == val_node
    assert ret.line == 2
    assert ret.column == 5

    ret_empty = ReturnNode(line=3, column=1)
    assert ret_empty.value is None
    assert ret_empty.line == 3
    assert ret_empty.column == 1


@pytest.mark.parametrize("value_node", [Node(line=2, column=10), None])
def test_return_node_variants(value_node: Node | None) -> None:
    """Valida ReturnNode com e sem expressão (value)."""
    ret = ReturnNode(value=value_node, line=2, column=1)

    assert isinstance(ret, Node)
    assert isinstance(ret, ReturnNode)
    assert ret.value == value_node
    assert ret.line == 2
    assert ret.column == 1


def test_assign_and_return_nodes_inheritance_and_metadata() -> None:
    """Valida herança de Node e rastreabilidade de line e column para AssignNode e ReturnNode."""
    assign = AssignNode(target="x", op="=", line=10, column=20)
    ret = ReturnNode(line=15, column=25)

    assert isinstance(assign, Node)
    assert assign.line == 10
    assert assign.column == 20

    assert isinstance(ret, Node)
    assert ret.line == 15
    assert ret.column == 25


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
def test_elif_clause_node_default_values() -> None:
    """Verifica que ElifClauseNode inicia com condition=None e body vazio."""
    node = ElifClauseNode()
    assert node.condition is None
    assert node.body == []
    assert node.line == 0
    assert node.column == 0


def test_elif_clause_node_with_values() -> None:
    """Verifica que ElifClauseNode armazena condition e body corretamente."""
    condition = Node(line=3, column=5)
    body_stmt = Node(line=4, column=9)
    node = ElifClauseNode(condition=condition, body=[body_stmt], line=3, column=1)

    assert node.condition is condition
    assert len(node.body) == 1
    assert node.body[0] is body_stmt
    assert node.line == 3


def test_elif_clause_node_inherits_from_node() -> None:
    """Verifica que ElifClauseNode é instância de Node."""
    assert isinstance(ElifClauseNode(), Node)
    assert issubclass(ElifClauseNode, Node)

def test_else_clause_node_default_values() -> None:
    """Verifica que ElseClauseNode inicia com body vazio."""
    node = ElseClauseNode()
    assert node.body == []
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
def test_else_clause_node_with_body() -> None:
    """Verifica que ElseClauseNode armazena body corretamente."""
    stmt = Node(line=5, column=9)
    node = ElseClauseNode(body=[stmt], line=5, column=1)

    assert len(node.body) == 1
    assert node.body[0] is stmt


def test_else_clause_node_inherits_from_node() -> None:
    """Verifica que ElseClauseNode é instância de Node."""
    assert isinstance(ElseClauseNode(), Node)
    assert issubclass(ElseClauseNode, Node)

def test_if_node_default_values() -> None:
    """Verifica que IfNode inicia com todos os campos no valor padrão."""
    node = IfNode()
    assert node.condition is None
    assert node.then_body == []
    assert node.elif_clauses == []
    assert node.else_body == []
    assert node.line == 0
    assert node.column == 0


def test_if_node_without_elif_and_else() -> None:
    """Verifica IfNode simples sem cláusulas elif/else."""
    condition = Node(line=2, column=4)
    stmt = Node(line=3, column=9)
    node = IfNode(condition=condition, then_body=[stmt], line=2, column=1)

    assert node.condition is condition
    assert len(node.then_body) == 1
    assert node.elif_clauses == []
    assert node.else_body == []


def test_if_node_with_elif_clauses() -> None:
    """Verifica IfNode com uma ou mais cláusulas elif."""
    condition = Node(line=2, column=4)
    elif1 = ElifClauseNode(condition=Node(line=4, column=6), line=4, column=1)
    elif2 = ElifClauseNode(condition=Node(line=6, column=6), line=6, column=1)
    node = IfNode(
        condition=condition,
        then_body=[Node(line=3, column=9)],
        elif_clauses=[elif1, elif2],
        line=2,
        column=1,
    )

    assert len(node.elif_clauses) == 2
    assert node.elif_clauses[0] is elif1
    assert node.elif_clauses[1] is elif2
    assert node.else_body == []


def test_if_node_with_else_clause() -> None:
    """Verifica IfNode com cláusula else."""
    else_stmt = Node(line=6, column=9)
    node = IfNode(
        condition=Node(line=2, column=4),
        then_body=[Node(line=3, column=9)],
        else_body=[else_stmt],
        line=2,
        column=1,
    )

    assert len(node.else_body) == 1
    assert node.else_body[0] is else_stmt
    assert node.elif_clauses == []


def test_if_node_complete_if_elif_else() -> None:
    """Verifica IfNode completo com condition, then_body, elif_clauses e else_body."""
    node = IfNode(
        condition=Node(line=2, column=4),
        then_body=[Node(line=3, column=9)],
        elif_clauses=[ElifClauseNode(condition=Node(line=5, column=6), line=5, column=1)],
        else_body=[Node(line=7, column=9)],
        line=2,
        column=1,
    )

    assert node.condition is not None
    assert len(node.then_body) == 1
    assert len(node.elif_clauses) == 1
    assert len(node.else_body) == 1


def test_if_node_inherits_from_node() -> None:
    """Verifica que IfNode é instância de Node."""
    assert isinstance(IfNode(), Node)
    assert issubclass(IfNode, Node)

def test_while_node_default_values() -> None:
    """Verifica que WhileNode inicia com condition=None e body vazio."""
    node = WhileNode()
    assert node.condition is None
    assert node.body == []
    assert node.line == 0
    assert node.column == 0


def test_while_node_with_values() -> None:
    """Verifica que WhileNode armazena condition e body corretamente."""
    condition = Node(line=5, column=7)
    stmt = Node(line=6, column=9)
    node = WhileNode(condition=condition, body=[stmt], line=5, column=1)

    assert node.condition is condition
    assert len(node.body) == 1
    assert node.body[0] is stmt


def test_while_node_inherits_from_node() -> None:
    """Verifica que WhileNode é instância de Node."""
    assert isinstance(WhileNode(), Node)
    assert issubclass(WhileNode, Node)

from src.parser import (
    IdentifierNode,
    IntLiteralNode,
    FloatLiteralNode,
    StringLiteralNode,
    BoolLiteralNode,
    NoneLiteralNode,
)

def test_identifier_node_stores_name() -> None:
    """Verifica que IdentifierNode armazena o nome corretamente."""
    node = IdentifierNode("total", line=1, column=1)
    assert node.name == "total"
    assert node.line == 1
    assert node.column == 1


def test_identifier_node_inherits_from_node() -> None:
    """Verifica que IdentifierNode herda de Node."""
    assert isinstance(IdentifierNode(), Node)
    assert issubclass(IdentifierNode, Node)


def test_int_literal_node_stores_value() -> None:
    """Verifica que IntLiteralNode armazena o valor inteiro usando kw_only herdado."""
    node = IntLiteralNode(value=10, line=2, column=5)
    assert node.value == 10
    assert node.line == 2
    assert node.column == 5


def test_int_literal_node_inherits_from_node() -> None:
    """Verifica que IntLiteralNode herda de Node."""
    assert isinstance(IntLiteralNode(), Node)
    assert issubclass(IntLiteralNode, Node)


def test_float_literal_node_stores_value() -> None:
    """Verifica que FloatLiteralNode armazena o valor float corretamente."""
    node = FloatLiteralNode(value=3.14, line=3, column=7)
    assert node.value == pytest.approx(3.14)
    assert node.line == 3
    assert node.column == 7


def test_float_literal_node_inherits_from_node() -> None:
    """Verifica que FloatLiteralNode herda de Node."""
    assert isinstance(FloatLiteralNode(), Node)
    assert issubclass(FloatLiteralNode, Node)


def test_string_literal_node_stores_value() -> None:
    """Verifica que StringLiteralNode armazena o texto corretamente."""
    node = StringLiteralNode(value="olá mundo", line=4, column=9)
    assert node.value == "olá mundo"
    assert node.line == 4
    assert node.column == 9


def test_string_literal_node_inherits_from_node() -> None:
    """Verifica que StringLiteralNode herda de Node."""
    assert isinstance(StringLiteralNode(), Node)
    assert issubclass(StringLiteralNode, Node)


def test_bool_literal_node_true() -> None:
    """Verifica que BoolLiteralNode armazena True corretamente."""
    node = BoolLiteralNode(value=True, line=5, column=4)
    assert node.value is True
    assert node.line == 5
    assert node.column == 4


def test_bool_literal_node_false() -> None:
    """Verifica que BoolLiteralNode armazena False corretamente."""
    node = BoolLiteralNode(value=False, line=6, column=4)
    assert node.value is False
    assert node.line == 6
    assert node.column == 4


def test_bool_literal_node_inherits_from_node() -> None:
    """Verifica que BoolLiteralNode herda de Node."""
    assert isinstance(BoolLiteralNode(), Node)
    assert issubclass(BoolLiteralNode, Node)


def test_none_literal_node_instantiation() -> None:
    """Verifica que NoneLiteralNode pode ser criado com coordenadas."""
    node = NoneLiteralNode(line=7, column=1)
    assert node.line == 7
    assert node.column == 1


def test_none_literal_node_inherits_from_node() -> None:
    """Verifica que NoneLiteralNode herda de Node."""
    assert isinstance(NoneLiteralNode(), Node)
    assert issubclass(NoneLiteralNode, Node)