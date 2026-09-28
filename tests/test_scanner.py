"""Testes do Scanner — cobertura completa dos tokens, erros e blocos léxicos."""

import pytest

from src.lexer.errors import LexicalError
from src.lexer.scanner import Scanner
from src.lexer.token_type import TokenType

def scan_all(source: str) -> list:
    """Coleta todos os tokens até EOF (inclusive)."""
    scanner = Scanner(source)
    tokens = []
    while True:
        token = scanner.next_token()
        tokens.append(token)
        if token.type == TokenType.EOF:
            break
    return tokens

def types(source: str) -> list:
    """Retorna apenas os tipos dos tokens produzidos."""
    return [t.type for t in scan_all(source)]

def test_keywords_all() -> None:
    """Verifica que cada palavra reservada é reconhecida com seu tipo correto."""
    cases = [
        ("class", TokenType.KW_CLASS),
        ("def", TokenType.KW_DEF),
        ("self", TokenType.KW_SELF),
        ("if", TokenType.KW_IF),
        ("elif", TokenType.KW_ELIF),
        ("else", TokenType.KW_ELSE),
        ("while", TokenType.KW_WHILE),
        ("return", TokenType.KW_RETURN),
        ("True", TokenType.KW_TRUE),
        ("False", TokenType.KW_FALSE),
        ("None", TokenType.KW_NONE),
    ]
    for lexeme, expected_type in cases:
        tokens = scan_all(lexeme)
        assert tokens[0].type == expected_type, f"Falhou para '{lexeme}'"
        assert tokens[0].lexeme == lexeme

def test_keyword_not_matched_as_prefix() -> None:
    """Verifica que 'define' e 'ifx' são IDENTIFIER, não KW_DEF / KW_IF."""
    assert scan_all("define")[0].type == TokenType.IDENTIFIER
    assert scan_all("ifx")[0].type == TokenType.IDENTIFIER


def test_keywords_case_sensitive() -> None:
    """Verifica que 'DEF', 'Class' e 'true' são IDENTIFIER (maiúsculas não são keywords)."""
    assert scan_all("DEF")[0].type == TokenType.IDENTIFIER
    assert scan_all("Class")[0].type == TokenType.IDENTIFIER
    assert scan_all("true")[0].type == TokenType.IDENTIFIER

def test_identifier_with_underscore_and_digits() -> None:
    """Verifica identificadores com underscore e dígitos."""
    for name in ("_init", "total_1", "valor2", "__x__"):
        token = scan_all(name)[0]
        assert token.type == TokenType.IDENTIFIER, f"Falhou para '{name}'"
        assert token.lexeme == name

def test_int_literal() -> None:
    """Verifica tokenização de inteiros."""
    for src, expected in (("0", 0), ("42", 42), ("1000", 1000)):
        token = scan_all(src)[0]
        assert token.type == TokenType.INT_LITERAL
        assert token.lexeme == src
        assert token.literal == expected

def test_float_literal() -> None:
    """Verifica tokenização de floats."""
    for src, expected in (("0.5", 0.5), ("3.1415", 3.1415), ("10.0", 10.0)):
        token = scan_all(src)[0]
        assert token.type == TokenType.FLOAT_LITERAL
        assert token.lexeme == src
        assert token.literal == pytest.approx(expected)

def test_int_followed_by_dot_without_digit_is_not_float() -> None:
    """Verifica que '3.' lança LexicalError — '.' isolado não é token válido."""
    with pytest.raises(LexicalError):
        scan_all("3.")

def test_string_double_quotes() -> None:
    """Verifica string com aspas duplas."""
    token = scan_all('"olá"')[0]
    assert token.type == TokenType.STRING_LITERAL
    assert token.literal == "olá"

def test_string_single_quotes() -> None:
    """Verifica string com aspas simples."""
    token = scan_all("'texto'")[0]
    assert token.type == TokenType.STRING_LITERAL
    assert token.literal == "texto"

def test_string_with_escape_sequences() -> None:
    """Verifica tratamento de sequências de escape dentro de strings."""
    token = scan_all(r'"com \"escape\""')[0]
    assert token.type == TokenType.STRING_LITERAL
    assert '"' in token.literal

def test_string_with_newline_escape() -> None:
    """Verifica que \\n dentro da string vira caractere de nova linha."""
    token = scan_all(r'"linha1\nlinha2"')[0]
    assert token.type == TokenType.STRING_LITERAL
    assert token.literal == "linha1\nlinha2"

def test_unterminated_string_raises_lexical_error() -> None:
    """Verifica que string não terminada lança LexicalError com posição correta."""
    with pytest.raises(LexicalError) as exc_info:
        scan_all('"olá\n')
    err = exc_info.value
    assert err.line == 1
    assert err.column == 1
    assert "literal de string não terminado" in str(err)


def test_unterminated_string_at_eof_raises_lexical_error() -> None:
    """Verifica que string aberta sem fechamento até EOF lança LexicalError."""
    with pytest.raises(LexicalError) as exc_info:
        scan_all('"sem fechar')
    assert "literal de string não terminado" in str(exc_info.value)

def test_compound_assignment_operators() -> None:
    """Verifica operadores compostos += e -= (maior casamento)."""
    token = scan_all("+=")[0]
    assert token.type == TokenType.OP_ADD_ASSIGN
    assert token.lexeme == "+="

    token = scan_all("-=")[0]
    assert token.type == TokenType.OP_SUB_ASSIGN
    assert token.lexeme == "-="


def test_assign_operator() -> None:
    """Verifica operador de atribuição simples."""
    token = scan_all("=")[0]
    assert token.type == TokenType.OP_ASSIGN
    assert token.lexeme == "="

def test_relational_operators() -> None:
    """Verifica todos os operadores relacionais."""
    cases = [
        ("==", TokenType.OP_EQ),
        ("!=", TokenType.OP_NEQ),
        ("<",  TokenType.OP_LT),
        ("<=", TokenType.OP_LTE),
        (">",  TokenType.OP_GT),
        (">=", TokenType.OP_GTE),
    ]
    for src, expected in cases:
        token = scan_all(src)[0]
        assert token.type == expected, f"Falhou para '{src}'"
        assert token.lexeme == src

def test_delimiters() -> None:
    """Verifica tokenização dos delimitadores : ( )."""
    cases = [
        (":", TokenType.COLON),
        ("(", TokenType.LPAREN),
        (")", TokenType.RPAREN),
    ]
    for src, expected in cases:
        token = scan_all(src)[0]
        assert token.type == expected
        assert token.lexeme == src

def test_invalid_character_raises_lexical_error() -> None:
    """Verifica que caractere inválido '@' lança LexicalError com posição."""
    with pytest.raises(LexicalError) as exc_info:
        scan_all("@")
    err = exc_info.value
    assert "caractere inválido '@'" in str(err)
    assert err.line == 1
    assert err.column == 1

def test_inline_comment_is_discarded() -> None:
    """Verifica que comentário ao final de linha é descartado."""
    result = types("x = 1  # comentário inline\n")
    assert TokenType.NEWLINE in result
    assert TokenType.EOF in result
    assert all(t not in result for t in [TokenType.ERROR])


def test_comment_does_not_generate_newline() -> None:
    """Verifica que linha apenas com comentário não gera NEWLINE."""
    result = types("# apenas comentário\n")
    assert TokenType.NEWLINE not in result


def test_newline_token_emitted() -> None:
    """Verifica que quebra de linha gera token NEWLINE."""
    result = types("x\n")
    assert TokenType.NEWLINE in result


def test_crlf_produces_single_newline() -> None:
    """Verifica que \\r\\n produz apenas um token NEWLINE."""
    result = types("x\r\ny")
    assert result.count(TokenType.NEWLINE) == 1


def test_blank_lines_do_not_produce_newline() -> None:
    """Verifica que linhas em branco entre instruções não geram tokens extras."""
    result = types("x\n\ny")
    assert result.count(TokenType.NEWLINE) == 1

def test_indent_and_dedent_single_block() -> None:
    """Verifica emissão de INDENT e DEDENT para um bloco simples."""
    src = "if True:\n    x = 1\n"
    result = types(src)
    assert TokenType.INDENT in result
    assert TokenType.DEDENT in result

def test_nested_blocks_emit_multiple_indent_dedent() -> None:
    """Verifica emissão de múltiplos INDENT/DEDENT para blocos aninhados."""
    src = "if True:\n    if True:\n        x = 1\n"
    result = types(src)
    assert result.count(TokenType.INDENT) == 2
    assert result.count(TokenType.DEDENT) == 2


def test_eof_closes_open_blocks_with_dedents() -> None:
    """Verifica que EOF fecha blocos abertos emitindo DEDENTs (spec item 5)."""
    src = "def foo():\n    x = 1"  # sem \n no final
    result = types(src)
    assert TokenType.DEDENT in result
    assert result[-1] == TokenType.EOF

def test_spec_example_comment_discarded() -> None:
    """Exemplo 1 da spec: comentários descartados em def dobro."""
    src = "# calcula o dobro de um número\ndef dobro(x):\n    return x * 2  # ignora este comentário\n"
    result = types(src)
    expected = [
        TokenType.KW_DEF, TokenType.IDENTIFIER, TokenType.LPAREN,
        TokenType.IDENTIFIER, TokenType.RPAREN, TokenType.COLON, TokenType.NEWLINE,
        TokenType.INDENT, TokenType.KW_RETURN, TokenType.IDENTIFIER,
        TokenType.OP_MULT, TokenType.INT_LITERAL, TokenType.NEWLINE,
        TokenType.DEDENT, TokenType.EOF,
    ]
    assert result == expected

def test_spec_example_compound_operators() -> None:
    """Exemplo 2 da spec: operadores compostos <= e +=."""
    src = "while total <= 100:\n    total += 1\n"
    result = types(src)
    expected = [
        TokenType.KW_WHILE, TokenType.IDENTIFIER, TokenType.OP_LTE,
        TokenType.INT_LITERAL, TokenType.COLON, TokenType.NEWLINE,
        TokenType.INDENT, TokenType.IDENTIFIER, TokenType.OP_ADD_ASSIGN,
        TokenType.INT_LITERAL, TokenType.NEWLINE,
        TokenType.DEDENT, TokenType.EOF,
    ]
    assert result == expected

def test_spec_example_invalid_char_at() -> None:
    """Exemplo de erro da spec: '@' na coluna 11 da linha 3."""
    src = "def main():\n    a = 10\n    b = a @ 2\n    return b\n"
    with pytest.raises(LexicalError) as exc_info:
        scan_all(src)
    err = exc_info.value
    assert err.line == 3
    assert err.column == 11
    assert "caractere inválido '@'" in str(err)

def test_spec_example_unterminated_string_position() -> None:
    """Exemplo de erro da spec: string não terminada na linha 2, coluna 13."""
    src = 'def mensagem():\n    texto = "olá\n    return texto\n'
    with pytest.raises(LexicalError) as exc_info:
        scan_all(src)
    err = exc_info.value
    assert err.line == 2
    assert err.column == 13
    assert "literal de string não terminado" in str(err)

def test_many_blank_lines_do_not_cause_recursion_error() -> None:
    """Verifica que muitas linhas vazias consecutivas não estouram a pilha de recursão."""
    src = "\n" * 1500 + "x = 1\n"
    tokens = scan_all(src)
    assert any(t.type == TokenType.IDENTIFIER and t.lexeme == "x" for t in tokens)