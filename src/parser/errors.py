"""Exceções utilizadas durante a análise sintática do PyToJava."""


class ParserError(Exception):
    """Representa um erro sintático associado a uma posição do código-fonte.

    Atributos:
        message: Descrição amigável da violação gramatical.
        line: Linha no código-fonte onde o erro foi detectado (1-based).
        column: Coluna no código-fonte onde o erro foi detectado (1-based).
    """

    def __init__(self, message: str, line: int = 0, column: int = 0) -> None:
        super().__init__(message)
        self.message = message
        self.line = line
        self.column = column

    def __str__(self) -> str:
        """Retorna o erro sintático no formato padronizado do compilador."""
        return (
            f"Erro Sintático [Linha {self.line}, Coluna {self.column}]: "
            f"{self.message}"
        )
