"""Gerenciador de indentação do analisador léxico.

(Mantém o estado global da pilha de níveis de recuo e o buffer de tokens
pendentes, seguindo as normas do projeto).
"""

from src.lexer.token import Token
from src.lexer.token_type import TokenType

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


def process_indentation(indent_level: int, line: int, col: int) -> list[Token]:
    """Processa o nível de recuo de uma linha e emite os tokens sintéticos devidos.

    Compara ``indent_level`` com o topo da pilha e executa a transição de estado:

    - Aumento de recuo: empilha o novo nível e emite um ``INDENT``.
    - Redução de recuo: desempilha os níveis superiores, emitindo um ``DEDENT``
      para cada, e valida o alinhamento do nível final.
    - Recuo inalterado: mantém a pilha e não emite token algum.

    Args:
        indent_level: Quantidade de espaços/tabulações do início da linha.
        line: Linha do código-fonte onde o recuo foi medido (iniciando em 1).
        col: Coluna do código-fonte onde o recuo foi medido (iniciando em 1).

    Returns:
        Lista de tokens ``INDENT``/``DEDENT`` gerados na transição, um token
        ``ERROR`` em caso de indentação desalinhada ou lista vazia quando o
        nível não muda.
    """
    if indent_level > INDENT_STACK[-1]:
        INDENT_STACK.append(indent_level)
        return [
            Token(
                type=TokenType.INDENT,
                lexeme="",
                literal=None,
                line=line,
                column=col,
            )
        ]

    if indent_level < INDENT_STACK[-1]:
        generated_tokens: list[Token] = []
        while indent_level < INDENT_STACK[-1]:
            INDENT_STACK.pop()
            generated_tokens.append(
                Token(
                    type=TokenType.DEDENT,
                    lexeme="",
                    literal=None,
                    line=line,
                    column=col,
                )
            )

        if indent_level != INDENT_STACK[-1]:
            return [
                Token(
                    type=TokenType.ERROR,
                    lexeme=(
                        f"Erro Léxico [Linha {line}, Coluna {col}]: "
                        "Indentação desalinhada"
                    ),
                    literal=None,
                    line=line,
                    column=col,
                )
            ]

        return generated_tokens

    return []


def finalize_indentation(line: int, col: int) -> list[Token]:
    """Fecha todos os blocos ainda abertos ao alcançar o fim do arquivo (EOF).

    Desempilha os níveis de recuo superiores ao nível base ``0``, emitindo um
    token ``DEDENT`` para cada escopo encerrado. Se a pilha já estiver no
    nível base, nenhum token é gerado.

    Args:
        line: Linha do código-fonte onde o fim de arquivo foi atingido.
        col: Coluna do código-fonte onde o fim de arquivo foi atingido.

    Returns:
        Lista de tokens ``DEDENT`` acumulados para fechar os blocos abertos,
        ou lista vazia quando não há blocos pendentes.
    """
    dedent_tokens: list[Token] = []
    while len(INDENT_STACK) > 1:
        INDENT_STACK.pop()
        dedent_tokens.append(
            Token(
                type=TokenType.DEDENT,
                lexeme="",
                literal=None,
                line=line,
                column=col,
            )
        )
    return dedent_tokens