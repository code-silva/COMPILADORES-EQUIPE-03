"""Suíte de Testes Unitários: Estrutura Base da AST e ProgramNode (Issue #20).

Valida a classe base ``Node`` (com ``kw_only=True``), o nó raiz ``ProgramNode``,
a rastreabilidade de coordenadas (``line`` e ``column``), a herança e a
compatibilidade de definição de subclasses com atributos posicionais e padrão.
"""
from src.parser import IfNode, ElifClauseNode, ElseClauseNode, WhileNode

from dataclasses import dataclass

import pytest

from src.parser import Node, ProgramNode


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