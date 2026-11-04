"""Testes unitários para os nós da AST do PyToJava."""

import pytest

from src.parser import AssignNode, Node, ProgramNode, ReturnNode


def test_base_node_defaults() -> None:
    """Verifica os valores padrão e a instanciação do nó base Node."""
    node = Node()
    assert node.line == 0
    assert node.column == 0


def test_program_node_defaults() -> None:
    """Verifica a instanciação padrão do ProgramNode."""
    prog = ProgramNode()
    assert isinstance(prog, Node)
    assert prog.stmts == []
    assert prog.line == 0
    assert prog.column == 0


def test_program_node_custom() -> None:
    """Verifica a instanciação de ProgramNode com elementos e posições customizadas."""
    assign = AssignNode(target="x", op="=", value=None, line=2, column=5)
    prog = ProgramNode(stmts=[assign], line=1, column=1)
    assert len(prog.stmts) == 1
    assert prog.stmts[0] == assign
    assert prog.line == 1
    assert prog.column == 1


@pytest.mark.parametrize("op", ["=", "+=", "-="])
def test_assign_node_operators(op: str) -> None:
    """Verifica AssignNode com diferentes operadores de atribuição."""
    assign = AssignNode(target="total", op=op, value=None, line=3, column=4)
    assert assign.target == "total"
    assert assign.op == op
    assert assign.value is None
    assert assign.line == 3
    assert assign.column == 4
    assert isinstance(assign, Node)


def test_return_node_with_and_without_value() -> None:
    """Verifica ReturnNode com e sem expressão de valor."""
    ret_empty = ReturnNode(line=5, column=1)
    assert ret_empty.value is None
    assert ret_empty.line == 5
    assert ret_empty.column == 1

    assign = AssignNode(target="x", op="=", value=None)
    ret_val = ReturnNode(value=assign, line=6, column=1)
    assert ret_val.value == assign
    assert isinstance(ret_val, Node)
