"""Testes da instrução ``print`` do parser ao código Java."""

import pytest

from src.cli import compile_source
from src.codegen import CodeGenerator
from src.parser import (
    BinOpNode,
    IntLiteralNode,
    Parser,
    ParserError,
    PrintNode,
    StringLiteralNode,
)
from src.semantic import SemanticError


def parse_stmts(source: str):
    return Parser(source).parse().stmts


def body(source: str) -> list[str]:
    lines = compile_source(source).splitlines()
    return [line.strip() for line in lines[2:-2]]


# --- Parser -------------------------------------------------------------------


def test_parse_print_com_literal() -> None:
    (node,) = parse_stmts('print("oi")\n')
    assert isinstance(node, PrintNode)
    assert isinstance(node.value, StringLiteralNode)
    assert (node.line, node.column) == (1, 1)


def test_parse_print_com_expressao() -> None:
    (node,) = parse_stmts("print(1 + 2)\n")
    assert isinstance(node, PrintNode)
    assert isinstance(node.value, BinOpNode)


def test_parse_print_vazio() -> None:
    (node,) = parse_stmts("print()\n")
    assert isinstance(node, PrintNode)
    assert node.value is None


def test_parse_print_dentro_de_bloco() -> None:
    (node,) = parse_stmts("if 1 < 2:\n    print(1)\n")
    assert isinstance(node.then_body[0], PrintNode)


@pytest.mark.parametrize(
    "source",
    ["print(1\n", "print(1 2)\n", "print(1) 2\n"],
)
def test_parse_print_malformado(source: str) -> None:
    with pytest.raises(ParserError):
        parse_stmts(source)


def test_print_sem_parenteses_continua_sendo_identificador() -> None:
    (node,) = parse_stmts("print\n")
    assert not isinstance(node, PrintNode)


# --- Semântico ----------------------------------------------------------------


def test_print_de_variavel_nao_declarada_falha() -> None:
    with pytest.raises(SemanticError):
        compile_source("print(y)\n")


# --- Codegen ------------------------------------------------------------------


def test_codegen_print_expressao() -> None:
    assert body("x = 2\nprint(x * 3)\n") == [
        "int x = 2;",
        "System.out.println((x * 3));",
    ]


def test_codegen_print_string_e_vazio() -> None:
    assert body('print("a\\nb")\nprint()\n') == [
        'System.out.println("a\\nb");',
        "System.out.println();",
    ]


def test_codegen_print_dentro_de_while() -> None:
    assert body("i = 0\nwhile i < 2:\n    print(i)\n    i += 1\n") == [
        "int i = 0;",
        "while ((i < 2)) {",
        "System.out.println(i);",
        "i += 1;",
        "}",
    ]


def test_visit_print_direto() -> None:
    gen = CodeGenerator()
    gen.visit(PrintNode(value=IntLiteralNode(value=7)))
    assert gen.code_lines == ["System.out.println(7);"]
