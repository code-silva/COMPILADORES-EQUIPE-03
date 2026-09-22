"""Gerenciador de indentação do analisador léxico.

Mantém o estado global da pilha de níveis de recuo e o buffer de tokens
pendentes, seguindo as normas do projeto).
"""

from src.lexer.token import Token

# Pilha de níveis de recuo, iniciada com o nível base 0 (escopo global).
INDENT_STACK: list[int] = [0]

# Buffer auxiliar para tokens pendentes (INDENT/DEDENT em fila de emissão).
PENDING_TOKENS: list[Token] = []


def reset_indent_manager() -> None:
    """Reinicia o estado interno para garantir isolamento entre testes e execuções.

    Redefine a pilha para o nível base ``[0]`` e esvazia a lista de tokens
    pendentes.
    """
    global INDENT_STACK, PENDING_TOKENS
    INDENT_STACK = [0]
    PENDING_TOKENS = []


def get_current_indent_level() -> int:
    """Consulta o nível de recuo ativo no topo da pilha, sem modificá-la.

    Returns:
        O nível de recuo vigente (topo de ``INDENT_STACK``).
    """
    return INDENT_STACK[-1]