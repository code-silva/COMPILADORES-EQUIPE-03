"""Testes do gerenciador de indentação (estado global, reinicialização e transições)."""

from src.lexer import indent_manager
from src.lexer.token import Token
from src.lexer.token_type import TokenType


def test_initial_state() -> None:
    """Verifica que o nível de recuo ativo inicia em 0 ao importar o módulo."""
    assert indent_manager.get_current_indent_level() == 0


def test_reset_indent_manager() -> None:
    """Verifica que reset_indent_manager restaura a pilha e esvazia os pendentes."""
    indent_manager.INDENT_STACK.append(4)
    indent_manager.PENDING_TOKENS.append(
        Token(type=TokenType.IDENTIFIER, lexeme="x", line=1, column=1)
    )

    indent_manager.reset_indent_manager()

    assert indent_manager.get_current_indent_level() == 0
    assert len(indent_manager.INDENT_STACK) == 1
    assert len(indent_manager.PENDING_TOKENS) == 0


def test_process_indentation_increase() -> None:
    """Verifica que o aumento de recuo emite INDENT e empilha o novo nível."""
    indent_manager.reset_indent_manager()

    result = indent_manager.process_indentation(4, 1, 1)
    assert [t.type for t in result] == [TokenType.INDENT]
    assert indent_manager.INDENT_STACK == [0, 4]

    result = indent_manager.process_indentation(8, 2, 1)
    assert [t.type for t in result] == [TokenType.INDENT]
    assert indent_manager.INDENT_STACK == [0, 4, 8]


def test_process_indentation_single_and_multiple_dedent() -> None:
    """Verifica transições de redução de recuo (um único ou múltiplos DEDENT)."""
    indent_manager.reset_indent_manager()
    indent_manager.process_indentation(4, 1, 1)
    indent_manager.process_indentation(8, 2, 1)

    result = indent_manager.process_indentation(4, 3, 1)
    assert [t.type for t in result] == [TokenType.DEDENT]
    assert indent_manager.INDENT_STACK == [0, 4]

    indent_manager.process_indentation(8, 4, 1)
    assert indent_manager.INDENT_STACK == [0, 4, 8]

    result = indent_manager.process_indentation(0, 5, 1)
    assert [t.type for t in result] == [TokenType.DEDENT, TokenType.DEDENT]
    assert indent_manager.INDENT_STACK == [0]


def test_process_indentation_misaligned_error() -> None:
    """Verifica que recuo desalinhado gera token de erro com mensagem exata e desempilha a pilha."""
    indent_manager.reset_indent_manager()
    indent_manager.process_indentation(4, 1, 1)
    indent_manager.process_indentation(8, 2, 1)

    result = indent_manager.process_indentation(3, 3, 1)

    assert len(result) == 1
    assert result[0].type == TokenType.ERROR
    assert result[0].lexeme == "Erro Léxico [Linha 3, Coluna 1]: Indentação desalinhada"
    assert indent_manager.INDENT_STACK == [0]


def test_process_indentation_same_level() -> None:
    """Verifica que recuo inalterado não emite tokens nem modifica a pilha."""
    indent_manager.reset_indent_manager()
    indent_manager.process_indentation(4, 1, 1)

    result = indent_manager.process_indentation(4, 2, 1)

    assert result == []
    assert indent_manager.INDENT_STACK == [0, 4]