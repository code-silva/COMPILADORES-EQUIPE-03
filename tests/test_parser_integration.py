"""Testes de integração do ponto de entrada ``Parser.parse()`` (#28).

Cobrem programas completos que combinam atribuições, retornos, expressões,
condicionais (``if``/``elif``/``else``) e laços (``while``), do código-fonte
até a árvore ``ProgramNode``.
"""

import pytest

from src.lexer.scanner import Scanner
from src.lexer.token_type import TokenType
from src.parser import (
    AssignNode,
    BinOpNode,
    BoolLiteralNode,
    ElifClauseNode,
    IdentifierNode,
    IfNode,
    IntLiteralNode,
    Parser,
    ParserError,
    ProgramNode,
    ReturnNode,
    StringLiteralNode,
    WhileNode,
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


def binop(left, op: str, right) -> BinOpNode:
    return BinOpNode(left=left, op=op, right=right)


def assign(target: str, op: str, value) -> AssignNode:
    return AssignNode(target=target, op=op, value=value)


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


# ---------------------------------------------- programas com controle de fluxo


PROGRAMA_FATORIAL = """\
# fatorial de 5 com while
n = 5
resultado = 1
while n > 1:
    resultado = resultado * n
    n -= 1

return resultado
"""


def test_programa_com_while() -> None:
    assert strip_positions(parse(PROGRAMA_FATORIAL)) == ProgramNode(
        stmts=[
            assign("n", "=", num(5)),
            assign("resultado", "=", num(1)),
            WhileNode(
                condition=binop(ident("n"), ">", num(1)),
                body=[
                    assign("resultado", "=", binop(ident("resultado"), "*", ident("n"))),
                    assign("n", "-=", num(1)),
                ],
            ),
            ReturnNode(value=ident("resultado")),
        ]
    )


PROGRAMA_CONCEITO = """\
nota = 8
if nota >= 9:
    conceito = "A"
elif nota >= 7:
    conceito = "B"
elif nota >= 5:
    conceito = "C"
else:
    conceito = "D"
return conceito
"""


def test_programa_com_if_elif_else() -> None:
    assert strip_positions(parse(PROGRAMA_CONCEITO)) == ProgramNode(
        stmts=[
            assign("nota", "=", num(8)),
            IfNode(
                condition=binop(ident("nota"), ">=", num(9)),
                then_body=[assign("conceito", "=", StringLiteralNode(value="A"))],
                elif_clauses=[
                    ElifClauseNode(
                        condition=binop(ident("nota"), ">=", num(7)),
                        body=[assign("conceito", "=", StringLiteralNode(value="B"))],
                    ),
                    ElifClauseNode(
                        condition=binop(ident("nota"), ">=", num(5)),
                        body=[assign("conceito", "=", StringLiteralNode(value="C"))],
                    ),
                ],
                else_body=[assign("conceito", "=", StringLiteralNode(value="D"))],
            ),
            ReturnNode(value=ident("conceito")),
        ]
    )


PROGRAMA_ANINHADO = """\
i = 0
menores = 0
while i < 10:
    if i < 5:
        menores += 1
    else:
        if i == 7:
            return menores
    i += 1
achou = True
"""


def test_programa_com_if_dentro_de_while_e_blocos_aninhados() -> None:
    assert strip_positions(parse(PROGRAMA_ANINHADO)) == ProgramNode(
        stmts=[
            assign("i", "=", num(0)),
            assign("menores", "=", num(0)),
            WhileNode(
                condition=binop(ident("i"), "<", num(10)),
                body=[
                    IfNode(
                        condition=binop(ident("i"), "<", num(5)),
                        then_body=[assign("menores", "+=", num(1))],
                        else_body=[
                            IfNode(
                                condition=binop(ident("i"), "==", num(7)),
                                then_body=[ReturnNode(value=ident("menores"))],
                            )
                        ],
                    ),
                    assign("i", "+=", num(1)),
                ],
            ),
            assign("achou", "=", BoolLiteralNode(value=True)),
        ]
    )


def test_bloco_no_fim_do_arquivo_sem_newline_final() -> None:
    ast = parse("x = 0\nwhile x < 3:\n    x += 1")
    assert strip_positions(ast.stmts) == [
        assign("x", "=", num(0)),
        WhileNode(
            condition=binop(ident("x"), "<", num(3)),
            body=[assign("x", "+=", num(1))],
        ),
    ]


def test_linhas_em_branco_e_comentarios_dentro_de_blocos() -> None:
    ast = parse("if True:\n\n    # comentário\n    x = 1\n\n    y = 2\nz = 3\n")
    assert strip_positions(ast.stmts) == [
        IfNode(
            condition=BoolLiteralNode(value=True),
            then_body=[assign("x", "=", num(1)), assign("y", "=", num(2))],
        ),
        assign("z", "=", num(3)),
    ]


def test_estruturas_mantem_a_linha_do_codigo() -> None:
    ast = parse(PROGRAMA_CONCEITO)
    se = ast.stmts[1]
    assert (se.line, se.column) == (2, 1)
    assert [c.line for c in se.elif_clauses] == [4, 6]
    assert se.then_body[0].line == 3
    assert se.else_body[0].line == 9
    assert ast.stmts[2].line == 10


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
        ("x = 1\nwhile x < 3\n    x += 1\n", 2),
        ("if x:\n    y = 1\nelse:\nz = 2\n", 4),
    ],
)
def test_erro_sintatico_interrompe_o_parse_com_a_linha_correta(source, line) -> None:
    with pytest.raises(ParserError) as exc_info:
        parse(source)
    assert exc_info.value.line == line
