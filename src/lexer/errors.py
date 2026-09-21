"""Exceções utilizadas durante a análise léxica do PyToJava."""


class LexicalError(Exception):
    """Representa um erro léxico associado a uma posição do código-fonte."""

    def __init__(self, message: str, line: int, column: int) -> None:
        super().__init__(message)
        self.message = message
        self.line = line
        self.column = column

    def __str__(self) -> str:
        """Retorna o erro no formato padronizado definido pela issue #8."""
        return f"LexicalError[{self.line}:{self.column}]: {self.message}"
