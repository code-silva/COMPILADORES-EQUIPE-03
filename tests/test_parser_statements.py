"""Testes do parser de instruções simples: atribuições e ``return`` (#26)."""

import pytest

from src.lexer.token_type import TokenType
from src.parser import (
    AssignNode,
    BinOpNode,
    BoolLiteralNode,
    IdentifierNode,
    IntLiteralNode,
    NoneLiteralNode,
    Parser,
    ParserError,
    ReturnNode,
    StringLiteralNode,
)
from tests.parser_helpers import strip_positions


def parse_one(source: str):
    """Analisa uma única instrução e devolve o nó sem posições."""
    return strip_positions(Parser(source).parse_statement())


# ---------------------------------------------------------------- atribuições


def test_atribuicao_simples() -> None:
    assert parse_one("x = 10") == AssignNode(
        target="x", op="=", value=IntLiteralNode(value=10)
    )


@pytest.mark.parametrize("op", ["+=", "-="])
def test_atribuicoes_acumulativas(op: str) -> None:
    assert parse_one(f"contador {op} 1") == AssignNode(
        target="contador", op=op, value=IntLiteralNode(value=1)
    )


def test_atribuicao_com_expressao_respeita_precedencia() -> None:
    assert parse_one("total = a + b * 2") == AssignNode(
        target="total",
        op="=",
        value=BinOpNode(
            left=IdentifierNode(name="a"),
            op="+",
            right=BinOpNode(
                left=IdentifierNode(name="b"), op="*", right=IntLiteralNode(value=2)
            ),
        ),
    )


@pytest.mark.parametrize(
    ("source", "expected_value"),
    [
        ('nome = "Ana"', StringLiteralNode(value="Ana")),
        ("ativo = True", BoolLiteralNode(value=True)),
        ("ativo = False", BoolLiteralNode(value=False)),
        ("vazio = None", NoneLiteralNode()),
        ("y = x", IdentifierNode(name="x")),
    ],
)
def test_atribuicao_de_literais_e_identificadores(source, expected_value) -> None:
    assert parse_one(source).value == expected_value


def test_atribuicao_guarda_posicao_do_alvo() -> None:
    parser = Parser("x = 1\nvalor += 2\n")
    parser.parse_statement()
    node = parser.parse_statement()
    assert (node.line, node.column) == (2, 1)
    assert (node.value.line, node.value.column) == (2, 10)


def test_parse_assignment_chamado_diretamente() -> None:
    node = Parser("x -= y").parse_assignment()
    assert strip_positions(node) == AssignNode(
        target="x", op="-=", value=IdentifierNode(name="y")
    )


def test_parse_assignment_exige_operador_de_atribuicao() -> None:
    with pytest.raises(ParserError, match="operador de atribuição"):
        Parser("x + 1").parse_assignment()


# --------------------------------------------------------------------- return


def test_return_com_expressao() -> None:
    assert parse_one("return x + 1") == ReturnNode(
        value=BinOpNode(
            left=IdentifierNode(name="x"), op="+", right=IntLiteralNode(value=1)
        )
    )


@pytest.mark.parametrize("source", ["return", "return\n"])
def test_return_sem_expressao(source: str) -> None:
    assert parse_one(source) == ReturnNode(value=None)


def test_return_guarda_posicao_da_palavra_chave() -> None:
    node = Parser("return 0").parse_statement()
    assert (node.line, node.column) == (1, 1)


def test_parse_return_statement_chamado_diretamente() -> None:
    node = Parser("return None").parse_return_statement()
    assert strip_positions(node) == ReturnNode(value=NoneLiteralNode())


# ------------------------------------------------------------ parse_statement


def test_parse_statement_roteia_cada_tipo_de_instrucao() -> None:
    parser = Parser("x = 1\nreturn x\nx\n")
    assert isinstance(parser.parse_statement(), AssignNode)
    assert isinstance(parser.parse_statement(), ReturnNode)
    assert isinstance(parser.parse_statement(), IdentifierNode)
    assert parser.peek().type == TokenType.EOF


def test_identificador_seguido_de_operador_nao_e_atribuicao() -> None:
    assert parse_one("x + 1") == BinOpNode(
        left=IdentifierNode(name="x"), op="+", right=IntLiteralNode(value=1)
    )


def test_instrucao_consome_o_newline_final() -> None:
    parser = Parser("x = 1\ny = 2\n")
    parser.parse_statement()
    assert parser.peek().lexeme == "y"


# ---------------------------------------------------------------------- erros


@pytest.mark.parametrize(
    ("source", "expected_message"),
    [
        ("x =", "Token inesperado"),
        ("x += ", "Token inesperado"),
        ("x = 1 2", "Esperado fim de linha"),
        ("return 1 2", "Esperado fim de linha"),
        ("x = (1 + 2", "Esperado ')'"),
    ],
)
def test_instrucoes_invalidas(source: str, expected_message: str) -> None:
    with pytest.raises(ParserError) as exc_info:
        Parser(source).parse_statement()
    assert expected_message in str(exc_info.value)


def test_erro_informa_linha_e_coluna() -> None:
    parser = Parser("x = 1\ny = * 2\n")
    parser.parse_statement()
    with pytest.raises(ParserError) as exc_info:
        parser.parse_statement()
    assert (exc_info.value.line, exc_info.value.column) == (2, 5)
