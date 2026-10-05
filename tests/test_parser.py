"""Testes da primeira gramática reconhecida pelo analisador sintático."""

import pytest

from src.parser import Parser, ParserError


@pytest.mark.parametrize(
    "source",
    [
        "42",
        "3.14",
        '"texto"',
        "True",
        "False",
        "None",
        "variavel",
        "-10",
        "+2.5",
        "1 + 2 * 3",
        "(1 + 2) * 3",
        "a / b - c",
        "idade >= 18",
        "1 < x <= 10",
        "resultado = 1 + 2 * 3",
        "contador += 1",
        "contador -= 1",
        "x = 1\ny = x + 2\n",
    ],
)
def test_accepts_initial_grammar(source: str) -> None:
    Parser(source).parse()


@pytest.mark.parametrize(
    ("source", "expected_message"),
    [
        ("x =", "esperada uma expressão"),
        ("1 + * 2", "esperada uma expressão"),
        ("(1 + 2", "esperado ')'"),
        ("1 2", "esperado fim de linha"),
        ("= 10", "esperada uma expressão"),
    ],
)
def test_rejects_invalid_syntax(source: str, expected_message: str) -> None:
    with pytest.raises(ParserError) as exc_info:
        Parser(source).parse()
    assert expected_message in str(exc_info.value)


def test_error_reports_source_position() -> None:
    with pytest.raises(ParserError) as exc_info:
        Parser("x = 1\ny = * 2\n").parse()

    error = exc_info.value
    assert error.line == 2
    assert error.column == 5
    assert "encontrado '*'" in str(error)


def test_rejects_compound_statement_not_yet_in_grammar() -> None:
    with pytest.raises(ParserError, match="esperada uma expressão"):
        Parser("if True:\n    x = 1\n").parse()
