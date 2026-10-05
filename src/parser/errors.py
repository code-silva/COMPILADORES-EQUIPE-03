"""Erros produzidos durante a análise sintática."""

from src.lexer.token import Token
from src.lexer.token_type import TokenType


class ParserError(Exception):
    """Erro sintático associado ao token em que a análise falhou."""

    def __init__(self, message: str, token: Token):
        self.message = message
        self.token = token
        self.line = token.line
        self.column = token.column
        super().__init__(self.__str__())

    def __str__(self) -> str:
        found = "fim do arquivo" if self.token.type == TokenType.EOF else repr(self.token.lexeme)
        return (
            f"Erro sintático em {self.line}:{self.column}: "
            f"{self.message}; encontrado {found}"
        )
