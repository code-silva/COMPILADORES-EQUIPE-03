"""Suíte de Testes Unitários: Casos Limite e Indentação do Lexer (Issue #10).

Valida cenários de fronteira, resiliência a falhas, fechamento automático
de blocos no fim de arquivo (EOF), indentação desalinhada, strings não terminadas,
caracteres ilegais e tratamento de entradas vazias ou compostas apenas por comentários.
"""

import pytest

from src.lexer.errors import LexicalError
from src.lexer.scanner import Scanner
from src.lexer.token import Token
from src.lexer.token_type import TokenType


def scan_all(source_code: str) -> list[Token]:
    """Utilitário para coletar todos os tokens até EOF (inclusive)."""
    scanner = Scanner(source_code)
    tokens: list[Token] = []
    while True:
        token = scanner.next_token()
        tokens.append(token)
        if token.type == TokenType.EOF:
            break
    return tokens


def get_token_types(source_code: str) -> list[TokenType]:
    """Utilitário para extrair apenas a sequência de tipos dos tokens."""
    return [token.type for token in scan_all(source_code)]


# ==============================================================================
# 1. Indentação Aninhada e Múltiplos DEDENTs
# ==============================================================================

def test_multiple_dedents_returning_to_global_scope() -> None:
    """Verifica se desempilhar múltiplos níveis emite a quantidade exata de DEDENTs.
    
    Níveis de recuo:
    - Linha 1: 0 (if)
    - Linha 2: 4 (if)
    - Linha 3: 8 (if)
    - Linha 4: 12 (x = 1)
    - Linha 5: 0 (retorno abrupto ao nível global -> deve emitir 3 DEDENTs)
    """
    source = (
        "if True:\n"
        "    if True:\n"
        "        if True:\n"
        "            x = 1\n"
        "y = 2\n"
    )
    tokens = scan_all(source)
    types = [t.type for t in tokens]

    # Contagem total de INDENT e DEDENT
    assert types.count(TokenType.INDENT) == 3
    assert types.count(TokenType.DEDENT) == 3

    # Localizar o identificador 'y' e conferir se foi precedido imediatamente por 3 DEDENTs
    y_idx = next(i for i, t in enumerate(tokens) if t.lexeme == "y")
    assert types[y_idx - 3 : y_idx] == [
        TokenType.DEDENT,
        TokenType.DEDENT,
        TokenType.DEDENT,
    ]


def test_partial_dedent_to_intermediate_level() -> None:
    """Verifica desempilhamento parcial de níveis (ex: 8 -> 4, mantendo nível 4 ativo)."""
    source = (
        "if True:\n"
        "    if True:\n"
        "        x = 1\n"
        "    y = 2\n"
    )
    tokens = scan_all(source)
    types = [t.type for t in tokens]

    y_idx = next(i for i, t in enumerate(tokens) if t.lexeme == "y")
    # Antes do 'y', deve haver exatamente 1 DEDENT desempilhando o nível 8 de volta para 4
    assert types[y_idx - 1] == TokenType.DEDENT
    assert types[y_idx - 2] != TokenType.DEDENT


# ==============================================================================
# 2. Indentação Desalinhada
# ==============================================================================

def test_misaligned_indentation_emits_error_token() -> None:
    """Verifica se um recuo que não coincide com nenhum nível da pilha emite TokenType.ERROR."""
    # Níveis: 0 -> 4 -> 8. Depois tenta recuar para 6 (não existe na pilha [0, 4, 8])
    source = (
        "if True:\n"
        "    if True:\n"
        "        x = 1\n"
        "      y = 2\n"
    )
    tokens = scan_all(source)
    error_tokens = [t for t in tokens if t.type == TokenType.ERROR]

    assert len(error_tokens) == 1
    assert "Indentação desalinhada" in error_tokens[0].lexeme
    assert error_tokens[0].line == 4


def test_misaligned_indentation_with_two_spaces() -> None:
    """Verifica desalinhamento retornando a 2 espaços quando os níveis são 0 e 4."""
    source = (
        "if True:\n"
        "    x = 1\n"
        "  y = 2\n"
    )
    tokens = scan_all(source)
    error_tokens = [t for t in tokens if t.type == TokenType.ERROR]

    assert len(error_tokens) == 1
    assert error_tokens[0].line == 3
    assert "Indentação desalinhada" in error_tokens[0].lexeme


# ==============================================================================
# 3. Fechamento de Arquivo no Meio de Blocos (EOF Handling)
# ==============================================================================

def test_eof_with_single_open_block_emits_dedent_and_eof() -> None:
    """Garante que bloco aberto seja encerrado por DEDENT antes do EOF."""
    source = (
        "def main():\n"
        "    return 42"
    )
    types = get_token_types(source)
    assert types[-2:] == [TokenType.DEDENT, TokenType.EOF]


def test_eof_with_multiple_open_blocks_emits_all_dedents() -> None:
    """Garante que múltiplos blocos aninhados sem fechamento emitam todos os DEDENTs antes de EOF."""
    source = (
        "def calcular():\n"
        "    if True:\n"
        "        while True:\n"
        "            x = 1"
    )
    types = get_token_types(source)
    # 3 blocos abertos -> 3 DEDENTs antes do EOF
    assert types[-4:] == [
        TokenType.DEDENT,
        TokenType.DEDENT,
        TokenType.DEDENT,
        TokenType.EOF,
    ]


# ==============================================================================
# 4. Strings Não Terminadas (Unterminated Strings)
# ==============================================================================

def test_unterminated_string_with_newline_raises_lexical_error() -> None:
    """Verifica se string com aspas duplas sem fechamento antes de quebra de linha lança erro."""
    source = 'x = "string sem fechamento\ny = 1\n'
    with pytest.raises(LexicalError) as exc_info:
        scan_all(source)
    err = exc_info.value
    assert err.line == 1
    assert err.column == 5
    assert "literal de string não terminado" in str(err)


def test_unterminated_single_quote_string_with_newline_raises_lexical_error() -> None:
    """Verifica se string com aspas simples sem fechamento antes de quebra de linha lança erro."""
    source = "mensagem = 'abriu e nao fechou\n"
    with pytest.raises(LexicalError) as exc_info:
        scan_all(source)
    err = exc_info.value
    assert err.line == 1
    assert err.column == 12
    assert "literal de string não terminado" in str(err)


def test_unterminated_string_at_eof_raises_lexical_error() -> None:
    """Verifica se string aberta que atinge o EOF sem fechamento lança erro."""
    source = 'def run():\n    nome = "sem fechar'
    with pytest.raises(LexicalError) as exc_info:
        scan_all(source)
    err = exc_info.value
    assert err.line == 2
    assert err.column == 12
    assert "literal de string não terminado" in str(err)


def test_unterminated_string_with_trailing_escape() -> None:
    """Verifica string que termina com barra de escape sem caractere subsequente."""
    source = 'texto = "incompleto\\'
    with pytest.raises(LexicalError) as exc_info:
        scan_all(source)
    assert "literal de string não terminado" in str(exc_info.value)


# ==============================================================================
# 5. Caracteres Inválidos e Símbolos Fora da Especificação
# ==============================================================================

@pytest.mark.parametrize(
    "invalid_char",
    ["@", "$", "?", "~", "`", "^", "&", "|", ";"],
)
def test_unsupported_characters_raise_lexical_error(invalid_char: str) -> None:
    """Verifica se caracteres fora do subconjunto procedural disparam LexicalError."""
    source = f"x = 10 {invalid_char} 20"
    with pytest.raises(LexicalError) as exc_info:
        scan_all(source)
    err = exc_info.value
    assert f"caractere inválido '{invalid_char}'" in str(err)
    assert err.line == 1
    assert err.column == 8


def test_isolated_exclamation_mark_raises_lexical_error() -> None:
    """Verifica se '!' isolado (não formando '!=') lança LexicalError."""
    source = "if x ! 10:\n    pass\n"
    with pytest.raises(LexicalError) as exc_info:
        scan_all(source)
    err = exc_info.value
    assert "caractere inválido '!'" in str(err)
    assert err.line == 1
    assert err.column == 6


def test_malformed_float_with_trailing_dot_raises_lexical_error() -> None:
    """Verifica se número terminado com '.' sem dígitos subsequentes acusa erro léxico."""
    source = "taxa = 3.\n"
    with pytest.raises(LexicalError) as exc_info:
        scan_all(source)
    err = exc_info.value
    assert "caractere inválido '.'" in str(err)
    assert err.line == 1
    assert err.column == 9


# ==============================================================================
# 6. Arquivos Vazios ou Quase Vazios
# ==============================================================================

def test_completely_empty_source() -> None:
    """Verifica entrada vazia (0 caracteres): deve emitir apenas Token(EOF)."""
    tokens = scan_all("")
    assert len(tokens) == 1
    assert tokens[0].type == TokenType.EOF
    assert (tokens[0].line, tokens[0].column) == (1, 1)


def test_whitespace_and_tabs_only() -> None:
    """Verifica entrada contendo exclusivamente espaços e tabs."""
    tokens = scan_all("   \t  \t\t   ")
    assert len(tokens) == 1
    assert tokens[0].type == TokenType.EOF


def test_blank_lines_only() -> None:
    """Verifica entrada contendo apenas quebras de linha (\\n e \\r\\n)."""
    tokens = scan_all("\n\n\r\n\n")
    assert len(tokens) == 1
    assert tokens[0].type == TokenType.EOF


def test_comments_only() -> None:
    """Verifica entrada contendo apenas linhas de comentários."""
    source = (
        "# Comentário inicial\n"
        "# Outro comentário na linha 2\n"
        "# Último comentário\n"
    )
    tokens = scan_all(source)
    assert len(tokens) == 1
    assert tokens[0].type == TokenType.EOF


def test_interleaved_comments_blank_lines_and_spaces() -> None:
    """Verifica entrada com mistura de comentários, espaços e linhas em branco."""
    source = (
        "\n"
        "   # Comentário com espaços antes\n"
        "\n"
        "    \t    \n"
        "# Fim dos comentários\n"
    )
    tokens = scan_all(source)
    assert len(tokens) == 1
    assert tokens[0].type == TokenType.EOF
