"""Suíte de Testes Unitários: Nós da AST (Issues #20, #23 e #24).

Valida a classe base ``Node`` (com ``kw_only=True``), o nó raiz ``ProgramNode``,
o nó de expressões binárias ``BinOpNode``, a rastreabilidade de coordenadas
(``line`` e ``column``), a herança e os nós folha (identificadores e literais
primitivos), incluindo cenários de borda e rejeição de argumentos posicionais.
"""
from dataclasses import dataclass

import pytest

from src.parser import (
    AssignNode,
    BinOpNode,
    BoolLiteralNode,
    ElifClauseNode,
    ElseClauseNode,
    FloatLiteralNode,
    IdentifierNode,
    IfNode,
    IntLiteralNode,
    Node,
    NoneLiteralNode,
    ProgramNode,
    ReturnNode,
    StringLiteralNode,
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

LEAF_NODE_CLASSES: list[type[Node]] = [
    IdentifierNode,
    IntLiteralNode,
    FloatLiteralNode,
    StringLiteralNode,
    BoolLiteralNode,
    NoneLiteralNode,
]

LEAF_NODE_FIELDS: list[tuple[type[Node], dict[str, object]]] = [
    (IdentifierNode, {"name": "x"}),
    (IntLiteralNode, {"value": 1}),
    (FloatLiteralNode, {"value": 1.5}),
    (StringLiteralNode, {"value": "texto"}),
    (BoolLiteralNode, {"value": True}),
    (NoneLiteralNode, {}),
]


@pytest.mark.parametrize(
    "name",
    ["x", "contador_1", "_temp", "totalGeral", "__interno__"],
)
def test_identifier_node_stores_valid_names(name: str) -> None:
    """Verifica que IdentifierNode armazena nomes simples e com caracteres válidos."""
    node = IdentifierNode(name=name, line=1, column=1)

    assert node.name == name
    assert node.line == 1
    assert node.column == 1


def test_identifier_node_default_name() -> None:
    """Verifica que IdentifierNode inicia com nome vazio."""
    node = IdentifierNode()

    assert node.name == ""
    assert node.line == 0
    assert node.column == 0


@pytest.mark.parametrize("value", [0, 1, 42, -7, -1024])
def test_int_literal_node_stores_values(value: int) -> None:
    """Verifica que IntLiteralNode armazena inteiros positivos, negativos e zero."""
    node = IntLiteralNode(value=value, line=2, column=5)

    assert node.value == value
    assert isinstance(node.value, int)
    assert node.line == 2
    assert node.column == 5


@pytest.mark.parametrize("value", [0.0, 3.14, -0.5, 1e-3, 123.456])
def test_float_literal_node_stores_values(value: float) -> None:
    """Verifica que FloatLiteralNode armazena valores decimais variados."""
    node = FloatLiteralNode(value=value, line=3, column=7)

    assert node.value == pytest.approx(value)
    assert isinstance(node.value, float)
    assert node.line == 3
    assert node.column == 7


@pytest.mark.parametrize(
    "value",
    [
        "",
        "olá mundo",
        "PyToJava",
        'aspas "duplas"',
        "linha 1\nlinha 2",
        r"barra \ invertida",
        "símbolos @#$%",
    ],
)
def test_string_literal_node_stores_values(value: str) -> None:
    """Verifica StringLiteralNode com strings vazias, convencionais e especiais."""
    node = StringLiteralNode(value=value, line=4, column=9)

    assert node.value == value
    assert node.line == 4
    assert node.column == 9


@pytest.mark.parametrize("value", [True, False], ids=["true", "false"])
def test_bool_literal_node_stores_value(value: bool) -> None:
    """Verifica explicitamente que BoolLiteralNode armazena True e False."""
    node = BoolLiteralNode(value=value, line=5, column=4)

    assert node.value is value
    assert isinstance(node.value, bool)
    assert node.line == 5
    assert node.column == 4


def test_none_literal_node_instantiation_without_value() -> None:
    """Verifica que NoneLiteralNode é instanciado sem argumento de valor."""
    node = NoneLiteralNode(line=7, column=1)

    assert node.line == 7
    assert node.column == 1
    assert not hasattr(node, "value")


def test_none_literal_node_default_instantiation() -> None:
    """Verifica que NoneLiteralNode usa os metadados padrão quando vazio."""
    node = NoneLiteralNode()

    assert node.line == 0
    assert node.column == 0


def test_none_literal_node_rejects_value_field() -> None:
    """Verifica que NoneLiteralNode não possui campo de valor."""
    with pytest.raises(TypeError):
        NoneLiteralNode(value=None)  # type: ignore[call-arg]


@pytest.mark.parametrize("node_class", LEAF_NODE_CLASSES)
def test_leaf_nodes_inherit_from_node(node_class: type[Node]) -> None:
    """Verifica que os 6 nós folha herdam de Node."""
    node = node_class()

    assert isinstance(node, Node)
    assert issubclass(node_class, Node)


@pytest.mark.parametrize(("node_class", "fields"), LEAF_NODE_FIELDS)
def test_leaf_nodes_propagate_position_metadata(
    node_class: type[Node],
    fields: dict[str, object],
) -> None:
    """Verifica o repasse de line e column via argumentos nomeados em todos os nós folha."""
    node = node_class(line=10, column=5, **fields)

    assert node.line == 10
    assert node.column == 5


@pytest.mark.parametrize("node_class", LEAF_NODE_CLASSES)
def test_leaf_nodes_reject_positional_metadata(node_class: type[Node]) -> None:
    """Verifica que line e column posicionais são rejeitados por causa de kw_only=True."""
    with pytest.raises(TypeError):
        node_class(10, 5)  # type: ignore[misc]
