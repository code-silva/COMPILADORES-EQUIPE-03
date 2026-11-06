"""Testes do parser de controle de fluxo: blocos, ``if``/``elif``/``else`` e ``while``."""

import pytest

from src.lexer.scanner import Scanner
from src.lexer.token_type import TokenType
from src.parser import (
    AssignNode,
    BinOpNode,
    ElifClauseNode,
    IdentifierNode,
    IfNode,
    IntLiteralNode,
    Parser,
    ParserError,
    ProgramNode,
    WhileNode,
)
from tests.parser_helpers import strip_positions


def parse(source: str) -> ProgramNode:
    """Analisa o programa completo a partir do código-fonte."""
    return Parser(source).parse()


def parse_stmt(source: str):
    """Analisa uma única instrução composta (``if`` ou ``while``)."""
    return Parser(source).parse_statement()


def ident(name: str) -> IdentifierNode:
    return IdentifierNode(name=name)


def num(value: int) -> IntLiteralNode:
    return IntLiteralNode(value=value)


def assign(target: str, value: int, op: str = "=") -> AssignNode:
    return AssignNode(target=target, op=op, value=num(value))


def tokenize(source: str):
    """Executa o Scanner até o EOF, devolvendo todos os tokens."""
    scanner = Scanner(source)
    tokens = []
    while True:
        token = scanner.next_token()
        tokens.append(token)
        if token.type == TokenType.EOF:
            return tokens


# ------------------------------------------------------------------ blocos


def test_parse_block_analisa_multiplas_instrucoes_e_consome_dedent() -> None:
    parser = Parser(":\n    a = 1\n    b = 2\n")

    body = parser.parse_block()

    assert strip_positions(body) == [assign("a", 1), assign("b", 2)]
    assert parser.peek().type == TokenType.EOF


def test_parse_block_exige_dois_pontos() -> None:
    with pytest.raises(ParserError, match="Esperado ':'"):
        Parser("    a = 1\n").parse_block()


# --------------------------------------------------------------- if simples


def test_if_simples_gera_if_node_com_condicao_e_then_body() -> None:
    ast = parse("if x > 0:\n    y = 1\n")

    assert strip_positions(ast.stmts) == [
        IfNode(
            condition=BinOpNode(left=ident("x"), op=">", right=num(0)),
            then_body=[assign("y", 1)],
        )
    ]


def test_if_simples_nao_tem_elif_nem_else() -> None:
    node = parse_stmt("if ativo:\n    x = 1\n")

    assert isinstance(node, IfNode)
    assert node.elif_clauses == []
    assert node.else_body == []


def test_if_guarda_posicao_da_palavra_chave_e_do_corpo() -> None:
    node = parse_stmt("if x:\n    y = 1\n")

    assert (node.line, node.column) == (1, 1)
    assert (node.then_body[0].line, node.then_body[0].column) == (2, 5)


# ------------------------------------------------------------- if / else


def test_if_else_preenche_then_body_e_else_body() -> None:
    ast = parse("if ativo:\n    x = 1\nelse:\n    x = 2\n")

    assert strip_positions(ast.stmts) == [
        IfNode(
            condition=ident("ativo"),
            then_body=[assign("x", 1)],
            else_body=[assign("x", 2)],
        )
    ]


def test_if_else_sem_elif() -> None:
    node = parse_stmt("if ativo:\n    x = 1\nelse:\n    x = 2\n")

    assert node.elif_clauses == []
    assert len(node.then_body) == 1
    assert len(node.else_body) == 1


# ------------------------------------------------------- if / elif / else


def test_if_elif_else_cria_elif_clause_node() -> None:
    ast = parse(
        "if x > 0:\n"
        "    r = 1\n"
        "elif x == 0:\n"
        "    r = 0\n"
        "else:\n"
        "    r = 2\n"
    )

    assert strip_positions(ast.stmts) == [
        IfNode(
            condition=BinOpNode(left=ident("x"), op=">", right=num(0)),
            then_body=[assign("r", 1)],
            elif_clauses=[
                ElifClauseNode(
                    condition=BinOpNode(left=ident("x"), op="==", right=num(0)),
                    body=[assign("r", 0)],
                )
            ],
            else_body=[assign("r", 2)],
        )
    ]


def test_if_com_multiplos_elif_mantem_ordem_das_clausulas() -> None:
    ast = parse(
        "if x > 0:\n"
        "    r = 1\n"
        "elif x == 0:\n"
        "    r = 0\n"
        "elif x < 0:\n"
        "    r = 3\n"
        "else:\n"
        "    r = 2\n"
    )

    node = ast.stmts[0]
    assert isinstance(node, IfNode)
    assert len(node.elif_clauses) == 2
    assert [clause.body[0].value.value for clause in node.elif_clauses] == [0, 3]
    assert [clause.condition.op for clause in node.elif_clauses] == ["==", "<"]
    assert node.else_body[0].value.value == 2


def test_elif_sem_else_e_permitido() -> None:
    node = parse_stmt("if x:\n    y = 1\nelif z:\n    y = 2\n")

    assert len(node.elif_clauses) == 1
    assert node.else_body == []


def test_elif_guarda_posicao_da_palavra_chave() -> None:
    node = parse_stmt("if x:\n    y = 1\nelif z:\n    y = 2\n")

    assert (node.elif_clauses[0].line, node.elif_clauses[0].column) == (3, 1)


# ----------------------------------------------------------------- while


def test_while_simples_gera_while_node() -> None:
    ast = parse("while contador <= 10:\n    contador += 1\n")

    assert strip_positions(ast.stmts) == [
        WhileNode(
            condition=BinOpNode(left=ident("contador"), op="<=", right=num(10)),
            body=[assign("contador", 1, op="+=")],
        )
    ]


def test_while_com_multiplas_instrucoes_no_corpo() -> None:
    ast = parse(
        "while x < 10:\n"
        "    total += x\n"
        "    x += 1\n"
        "    x = x * 2\n"
    )

    node = ast.stmts[0]
    assert isinstance(node, WhileNode)
    assert len(node.body) == 3
    assert strip_positions(node.body) == [
        AssignNode(target="total", op="+=", value=ident("x")),
        assign("x", 1, op="+="),
        AssignNode(
            target="x",
            op="=",
            value=BinOpNode(left=ident("x"), op="*", right=num(2)),
        ),
    ]


def test_while_guarda_posicao_da_palavra_chave() -> None:
    node = parse_stmt("while x:\n    x -= 1\n")

    assert (node.line, node.column) == (1, 1)


# ------------------------------------------------- escopos e aninhamento


def test_if_aninhado_dentro_de_while() -> None:
    ast = parse(
        "while x < 10:\n"
        "    if x > 5:\n"
        "        y = 1\n"
        "    else:\n"
        "        y = 2\n"
        "    x += 1\n"
    )

    while_node = ast.stmts[0]
    assert isinstance(while_node, WhileNode)
    assert [type(stmt) for stmt in while_node.body] == [IfNode, AssignNode]

    inner_if = while_node.body[0]
    assert isinstance(inner_if, IfNode)
    assert strip_positions(inner_if.then_body) == [assign("y", 1)]
    assert strip_positions(inner_if.else_body) == [assign("y", 2)]


def test_while_aninhado_dentro_de_if() -> None:
    ast = parse(
        "if ativo:\n"
        "    while x < 3:\n"
        "        x += 1\n"
        "    y = x\n"
    )

    outer_if = ast.stmts[0]
    assert isinstance(outer_if, IfNode)
    assert [type(stmt) for stmt in outer_if.then_body] == [WhileNode, AssignNode]

    inner_while = outer_if.then_body[0]
    assert isinstance(inner_while, WhileNode)
    assert strip_positions(inner_while.body) == [assign("x", 1, op="+=")]


def test_aninhamento_profundo_emparelha_indent_e_dedent() -> None:
    source = (
        "while x < 10:\n"
        "    if x > 5:\n"
        "        y = 1\n"
        "    else:\n"
        "        y = 2\n"
        "    x += 1\n"
    )
    tokens = tokenize(source)

    assert sum(t.type == TokenType.INDENT for t in tokens) == 3
    assert sum(t.type == TokenType.DEDENT for t in tokens) == 3

    ast = parse(source)
    assert len(ast.stmts) == 1
    assert isinstance(ast.stmts[0], WhileNode)


def test_if_aninhado_com_elif_e_else_no_mesmo_bloco() -> None:
    ast = parse(
        "if a:\n"
        "    if b:\n"
        "        x = 1\n"
        "    elif c:\n"
        "        x = 2\n"
        "    else:\n"
        "        x = 3\n"
        "    y = x\n"
    )

    outer_if = ast.stmts[0]
    assert isinstance(outer_if, IfNode)
    assert [type(stmt) for stmt in outer_if.then_body] == [IfNode, AssignNode]

    inner_if = outer_if.then_body[0]
    assert isinstance(inner_if, IfNode)
    assert len(inner_if.elif_clauses) == 1
    assert len(inner_if.else_body) == 1


def test_instrucoes_apos_bloco_voltam_ao_escopo_global() -> None:
    ast = parse("if x:\n    y = 1\nz = 2\n")

    assert [type(stmt) for stmt in ast.stmts] == [IfNode, AssignNode]
    assert strip_positions(ast.stmts[1]) == assign("z", 2)


# --------------------------------------------------------------- erros


def test_if_sem_dois_pontos_lanca_parser_error() -> None:
    with pytest.raises(ParserError, match="Esperado ':'"):
        parse("if x\n    y = 1\n")


def test_while_sem_dois_pontos_lanca_parser_error() -> None:
    with pytest.raises(ParserError, match="Esperado ':'"):
        parse("while x\n    y = 1\n")


def test_falta_de_indent_apos_dois_pontos_lanca_parser_error() -> None:
    with pytest.raises(ParserError, match="Esperado bloco indentado") as exc_info:
        parse("if x:\ny = 1\n")

    assert (exc_info.value.line, exc_info.value.column) == (2, 1)


def test_indentacao_inconsistente_lanca_parser_error() -> None:
    with pytest.raises(ParserError) as exc_info:
        parse("if x:\n    y = 1\n   z = 2\n")

    assert exc_info.value.line == 3


def test_bloco_sem_newline_apos_dois_pontos_lanca_parser_error() -> None:
    with pytest.raises(ParserError, match="Esperado fim de linha"):
        parse("if x: y = 1\n")
