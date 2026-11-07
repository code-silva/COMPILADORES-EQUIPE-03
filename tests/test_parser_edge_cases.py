"""Suíte de Testes Unitários: Erros Sintáticos e Casos de Borda do Parser (Issue #29).

Valida a resiliência da classe ``Parser`` e o lançamento de ``ParserError`` com
coordenadas exatas (``line`` e ``column``) em cenários de código malformado,
além do tratamento de arquivos vazios, comentários e sequências limítrofes.
"""

import pytest

from src.lexer.scanner import Scanner
from src.lexer.token import Token
from src.lexer.token_type import TokenType
from src.parser import Node, Parser, ParserError, ProgramNode


def tokenize(source_code: str) -> list[Token]:
    """Auxiliar para converter código-fonte em lista de tokens usando o Scanner."""
    scanner = Scanner(source_code)
    tokens: list[Token] = []
    while True:
        tok = scanner.next_token()
        tokens.append(tok)
        if tok.type == TokenType.EOF:
            break
    return tokens


def parse_program(source_code: str) -> ProgramNode:
    """Auxiliar para executar o parsing completo de um código-fonte."""
    return Parser(tokenize(source_code)).parse()


# ==============================================================================
# 1. Estrutura e Formatação de ParserError
# ==============================================================================


def test_parser_error_attributes_and_str_formatting() -> None:
    """Verifica que ParserError armazena message, line e column e formata __str__."""
    error = ParserError("Esperado ':' ao iniciar o bloco", line=3, column=12)

    assert isinstance(error, Exception)
    assert error.message == "Esperado ':' ao iniciar o bloco"
    assert error.line == 3
    assert error.column == 12
    assert str(error) == (
        "Erro Sintático [Linha 3, Coluna 12]: Esperado ':' ao iniciar o bloco"
    )


def test_parser_error_default_coordinates() -> None:
    """Verifica que ParserError possui line=0 e column=0 como padrão."""
    error = ParserError("Erro sintático genérico")
    assert error.line == 0
    assert error.column == 0
    assert "Linha 0, Coluna 0" in str(error)


# ==============================================================================
# 2. Validações Rigorosas em expect() e match()
# ==============================================================================


def test_expect_rejects_invalid_token_type_argument() -> None:
    """Garante que expect() lança TypeError se o argumento não for um TokenType."""
    parser = Parser("x = 1")
    with pytest.raises(TypeError, match="Esperado TokenType"):
        parser.expect("IDENTIFIER")  # type: ignore[arg-type]


def test_match_rejects_invalid_token_type_argument() -> None:
    """Garante que match() lança TypeError se algum argumento não for um TokenType."""
    parser = Parser("x = 1")
    with pytest.raises(TypeError, match="Esperado TokenType"):
        parser.match(TokenType.IDENTIFIER, "NEWLINE")  # type: ignore[arg-type]


def test_expect_and_match_raise_parser_error_on_lexical_error_token() -> None:
    """Garante que tokens sintéticos TokenType.ERROR disparam ParserError com linha e coluna."""
    error_token = Token(
        TokenType.ERROR,
        "recuo desalinhado com a pilha de indentação",
        None,
        line=4,
        column=3,
    )
    eof_token = Token(TokenType.EOF, "", None, line=4, column=3)

    parser_match = Parser([error_token, eof_token])
    with pytest.raises(ParserError, match="recuo desalinhado") as exc_match:
        parser_match.match(TokenType.NEWLINE)
    assert (exc_match.value.line, exc_match.value.column) == (4, 3)

    parser_expect = Parser([error_token, eof_token])
    with pytest.raises(ParserError, match="recuo desalinhado") as exc_expect:
        parser_expect.expect(TokenType.IDENTIFIER)
    assert (exc_expect.value.line, exc_expect.value.column) == (4, 3)


def test_parser_handles_empty_token_list_gracefully() -> None:
    """Verifica que passar uma lista vazia de tokens sintetiza EOF e retorna ProgramNode vazio."""
    parser = Parser([])
    program = parser.parse()
    assert isinstance(program, ProgramNode)
    assert program.stmts == []


def test_parser_appends_eof_when_missing_from_token_list() -> None:
    """Verifica que uma lista de tokens sem EOF explícito recebe EOF automaticamente."""
    tokens = [
        Token(TokenType.IDENTIFIER, "x", None, line=1, column=1),
        Token(TokenType.OP_ASSIGN, "=", None, line=1, column=3),
        Token(TokenType.INT_LITERAL, "10", 10, line=1, column=5),
    ]
    program = Parser(tokens).parse()
    assert len(program.stmts) == 1


# ==============================================================================
# 3. Arquivos Vazios, Linhas em Branco e Comentários
# ==============================================================================


@pytest.mark.parametrize(
    "source",
    [
        "",
        "   ",
        "\t\t  \t",
        "\n",
        "\n\n\n\n",
        "\r\n\r\n",
        "# apenas um comentário sem quebra de linha",
        "# comentário 1\n# comentário 2\n",
        "   # comentário indentado\n\n   \t  \n# outro comentário\n\n",
    ],
)
def test_empty_and_comment_only_sources_return_empty_program(source: str) -> None:
    """Verifica que entradas vazias ou apenas com comentários/espaços geram ProgramNode vazio."""
    program = parse_program(source)
    assert isinstance(program, ProgramNode)
    assert program.stmts == []
    assert (program.line, program.column) == (1, 1)


# ==============================================================================
# 4. Violações Gramaticais em Expressões e Parênteses
# ==============================================================================


@pytest.mark.parametrize(
    ("source", "expected_line", "expected_col"),
    [
        ("(1 + 2", 1, 7),
        ("((1 + 2) * 3", 1, 13),
        ("()", 1, 2),
        ("1 + ()", 1, 6),
        ("1 + 2)", 1, 6),
    ],
)
def test_malformed_parentheses_raise_parser_error_with_position(
    source: str, expected_line: int, expected_col: int
) -> None:
    """Valida lançamento de ParserError em parênteses não fechados, vazios ou sobrando."""
    with pytest.raises(ParserError) as exc_info:
        parse_program(source)

    assert exc_info.value.line == expected_line
    assert exc_info.value.column == expected_col


@pytest.mark.parametrize(
    ("source", "expected_line", "expected_col"),
    [
        ("* 10", 1, 1),
        ("/ 2", 1, 1),
        ("== 5", 1, 1),
        ("!= 0", 1, 1),
        ("10 +", 1, 5),
        ("10 -", 1, 5),
        ("10 *", 1, 5),
        ("10 /", 1, 5),
        ("10 + * 5", 1, 6),
        ("a == != b", 1, 6),
        ("-", 1, 2),
        ("+", 1, 2),
    ],
)
def test_operators_without_operands_raise_parser_error(
    source: str, expected_line: int, expected_col: int
) -> None:
    """Valida que operadores unários ou binários sem operandos lançam ParserError."""
    with pytest.raises(ParserError) as exc_info:
        parse_program(source)

    assert exc_info.value.line == expected_line
    assert exc_info.value.column == expected_col


# ==============================================================================
# 5. Violações em Atribuições e Instruções Simples
# ==============================================================================


@pytest.mark.parametrize(
    ("source", "expected_line", "expected_col"),
    [
        ("x =", 1, 4),
        ("x +=", 1, 5),
        ("x -=", 1, 5),
        ("10 = x", 1, 4),
        ('"texto" = 1', 1, 9),
        ("(a + b) = 10", 1, 9),
        ("x = 1 y = 2", 1, 7),
        ("return 1 2", 1, 10),
    ],
)
def test_malformed_simple_statements_raise_parser_error(
    source: str, expected_line: int, expected_col: int
) -> None:
    """Valida lançamento de ParserError em atribuições inválidas ou instruções coladas."""
    with pytest.raises(ParserError) as exc_info:
        parse_program(source)

    assert exc_info.value.line == expected_line
    assert exc_info.value.column == expected_col


# ==============================================================================
# 6. Violações em Estruturas de Controle e Blocos Indentados
# ==============================================================================


@pytest.mark.parametrize(
    ("source", "expected_line", "expected_col"),
    [
        # Falta de ':' no if, elif, else e while
        ("if x > 0\n    y = 1\n", 1, 9),
        ("if x > 0:\n    y = 1\nelif x < 0\n    y = 2\n", 3, 11),
        ("if x > 0:\n    y = 1\nelse\n    y = 2\n", 3, 5),
        ("while x < 10\n    x += 1\n", 1, 13),
        # Falta de condição em if, elif e while
        ("if :\n    x = 1\n", 1, 4),
        ("if True:\n    x = 1\nelif :\n    x = 2\n", 3, 6),
        ("while :\n    x = 1\n", 1, 7),
        # Instrução na mesma linha após ':' (sem NEWLINE)
        ("if True: x = 1\n", 1, 10),
        ("while True: x = 1\n", 1, 13),
        # Falta de bloco indentado (INDENT) após ':'
        ("if True:\nx = 1\n", 2, 1),
        ("while True:\nx = 1\n", 2, 1),
        ("if True:\n    x = 1\nelse:\ny = 2\n", 4, 1),
    ],
)
def test_malformed_control_flow_and_blocks_raise_parser_error(
    source: str, expected_line: int, expected_col: int
) -> None:
    """Valida lançamento de ParserError em falta de ':', condição ou indentação em blocos."""
    with pytest.raises(ParserError) as exc_info:
        parse_program(source)

    assert exc_info.value.line == expected_line
    assert exc_info.value.column == expected_col


@pytest.mark.parametrize(
    ("source", "expected_keyword", "expected_line"),
    [
        ("elif x > 0:\n    y = 1\n", "elif", 1),
        ("else:\n    y = 1\n", "else", 1),
        ("x = 1\nelse:\n    y = 2\n", "else", 2),
    ],
)
def test_orphan_elif_and_else_raise_parser_error(
    source: str, expected_keyword: str, expected_line: int
) -> None:
    """Verifica que cláusulas elif/else isoladas sem if correspondente lançam ParserError."""
    with pytest.raises(ParserError, match=f"Cláusula '{expected_keyword}' sem 'if'") as exc_info:
        parse_program(source)

    assert exc_info.value.line == expected_line


def test_unexpected_indentation_in_global_scope() -> None:
    """Verifica que recuo inesperado no nível global dispara ParserError."""
    with pytest.raises(ParserError, match="Indentação inesperada") as exc_info:
        parse_program("x = 1\n    y = 2\n")

    assert exc_info.value.line == 2


def test_misaligned_dedent_propagates_as_parser_error() -> None:
    """Verifica que um recuo desalinhado (TokenType.ERROR) dentro de um bloco lança ParserError."""
    source = (
        "if True:\n"
        "    x = 1\n"
        "  y = 2\n"
    )
    with pytest.raises(ParserError, match="Indentação desalinhada") as exc_info:
        parse_program(source)

    assert exc_info.value.line == 3


def test_unclosed_block_reaching_eof_without_dedent_raises_parser_error() -> None:
    """Verifica que um bloco aberto cuja lista de tokens termina em EOF sem DEDENT lança ParserError."""
    tokens = [
        Token(TokenType.KW_IF, "if", None, line=1, column=1),
        Token(TokenType.KW_TRUE, "True", True, line=1, column=4),
        Token(TokenType.COLON, ":", None, line=1, column=8),
        Token(TokenType.NEWLINE, "\n", None, line=1, column=9),
        Token(TokenType.INDENT, "", None, line=2, column=1),
        Token(TokenType.IDENTIFIER, "x", None, line=2, column=5),
        Token(TokenType.OP_ASSIGN, "=", None, line=2, column=7),
        Token(TokenType.INT_LITERAL, "1", 1, line=2, column=9),
        Token(TokenType.EOF, "", None, line=2, column=10),
    ]
    with pytest.raises(ParserError, match="Bloco indentado não finalizado") as exc_info:
        Parser(tokens).parse()

    assert exc_info.value.line == 2
    assert exc_info.value.column == 10
