"""Testes de integração do ponto de entrada ``Parser.parse()`` (#28).

Os programas com ``if``/``while`` serão acrescentados quando o parser de
estruturas de controle (#27) estiver disponível.
"""

import pytest

from src.lexer.scanner import Scanner
from src.lexer.token_type import TokenType
from src.parser import (
    AssignNode,
    BinOpNode,
    IdentifierNode,
    IntLiteralNode,
    Parser,
    ParserError,
    ProgramNode,
    ReturnNode,
    StringLiteralNode,
)
from tests.parser_helpers import strip_positions


def tokenize(source: str):
    """Executa o Scanner até o EOF, como o Driver fará."""
    scanner = Scanner(source)
    tokens = []
    while True:
        token = scanner.next_token()
        tokens.append(token)
        if token.type == TokenType.EOF:
            return tokens


def parse(source: str) -> ProgramNode:
    return Parser(tokenize(source)).parse()


def ident(name: str) -> IdentifierNode:
    return IdentifierNode(name=name)


def num(value: int) -> IntLiteralNode:
    return IntLiteralNode(value=value)


# ------------------------------------------------------------- programa vazio


@pytest.mark.parametrize(
    "source", ["", "\n", "\n\n\n", "# só comentário\n", "   \n# comentário\n\n"]
)
def test_programa_vazio(source: str) -> None:
    assert strip_positions(parse(source)) == ProgramNode(stmts=[])


def test_parse_retorna_program_node_na_posicao_inicial() -> None:
    ast = parse("x = 1")
    assert isinstance(ast, ProgramNode)
    assert (ast.line, ast.column) == (1, 1)


def test_parse_aceita_lista_de_tokens_e_codigo_fonte() -> None:
    source = "x = 1\nreturn x\n"
    assert Parser(tokenize(source)).parse() == Parser(source).parse()


# ------------------------------------------------------------ escopo global


def test_newlines_extras_no_escopo_global_sao_ignorados() -> None:
    ast = parse("\n\nx = 1\n\n\n\ny = 2\n\n")
    assert strip_positions(ast.stmts) == [
        AssignNode(target="x", op="=", value=num(1)),
        AssignNode(target="y", op="=", value=num(2)),
    ]


def test_arquivo_sem_newline_final() -> None:
    assert len(parse("x = 1\ny = 2").stmts) == 2


def test_instrucoes_mantem_a_ordem_e_a_linha_do_codigo() -> None:
    ast = parse("a = 1\n\n# meio\nb = 2\nreturn a\n")
    assert [(type(s).__name__, s.line) for s in ast.stmts] == [
        ("AssignNode", 1),
        ("AssignNode", 4),
        ("ReturnNode", 5),
    ]


# -------------------------------------------------------- programas completos


PROGRAMA = """\
# calcula a média de duas notas
nota1 = 7
nota2 = 9
soma = nota1 + nota2
soma -= 0
media = soma / 2
mensagem = "ok"

return media >= 7
"""


def test_programa_completo_com_instrucoes_simples() -> None:
    assert strip_positions(parse(PROGRAMA)) == ProgramNode(
        stmts=[
            AssignNode(target="nota1", op="=", value=num(7)),
            AssignNode(target="nota2", op="=", value=num(9)),
            AssignNode(
                target="soma",
                op="=",
                value=BinOpNode(left=ident("nota1"), op="+", right=ident("nota2")),
            ),
            AssignNode(target="soma", op="-=", value=num(0)),
            AssignNode(
                target="media",
                op="=",
                value=BinOpNode(left=ident("soma"), op="/", right=num(2)),
            ),
            AssignNode(target="mensagem", op="=", value=StringLiteralNode(value="ok")),
            ReturnNode(
                value=BinOpNode(left=ident("media"), op=">=", right=num(7))
            ),
        ]
    )


def test_return_vazio_no_fim_do_arquivo() -> None:
    assert strip_positions(parse("x += 1\nreturn").stmts) == [
        AssignNode(target="x", op="+=", value=num(1)),
        ReturnNode(value=None),
    ]


# ---------------------------------------------------------------------- erros


def test_indentacao_inesperada_no_escopo_global() -> None:
    with pytest.raises(ParserError, match="Indentação inesperada") as exc_info:
        parse("x = 1\n    y = 2\n")
    assert exc_info.value.line == 2


@pytest.mark.parametrize(
    ("source", "line"),
    [
        ("x = 1\ny = * 2\n", 2),
        ("x = 1\n\n\nreturn 1 2\n", 4),
    ],
)
def test_erro_sintatico_interrompe_o_parse_com_a_linha_correta(source, line) -> None:
    with pytest.raises(ParserError) as exc_info:
        parse(source)
    assert exc_info.value.line == line
