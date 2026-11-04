"""Suíte de Testes Unitários: Estrutura Base da AST e ProgramNode (Issue #20).

Valida a classe base ``Node`` (com ``kw_only=True``), o nó raiz ``ProgramNode``,
a rastreabilidade de coordenadas (``line`` e ``column``), a herança e a
compatibilidade de definição de subclasses com atributos posicionais e padrão.
"""

from dataclasses import dataclass

import pytest

from src.parser import AssignNode, Node, ProgramNode, ReturnNode


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

