"""Testes da primeira parte do gerenciador de indentação (estado global e reinicialização)."""

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