"""Módulo responsável pela leitura e rastreamento de caracteres do código-fonte."""


class CharStream:
    """Leitor de fluxo de caracteres que percorre o código-fonte caractere a caractere.

    Rastreia com precisão o cursor, a linha e a coluna atuais, permitindo
    mensagens de erro léxico exatas e suporte a lookahead pelo scanner.
    """

    def __init__(self, source_code: str) -> None:
        """Inicializa o leitor de caracteres com o código-fonte fornecido.

        Args:
            source_code: String contendo todo o código-fonte de entrada.
        """
        self.source_code: str = source_code
        self.cursor: int = 0
        self.line: int = 1
        self.column: int = 1

    def is_at_end(self) -> bool:
        """Verifica se o cursor atingiu ou ultrapassou o fim do código-fonte.

        Returns:
            True se estiver no fim do arquivo, False caso contrário.
        """
        return self.cursor >= len(self.source_code)

    def peek(self) -> str:
        """Inspeciona o caractere atual sem avançar o cursor.

        Returns:
            O caractere na posição atual ou o sentinela '\\0' caso esteja no fim.
        """
        if self.is_at_end():
            return "\0"
        return self.source_code[self.cursor]

    def peek_next(self) -> str:
        """Inspeciona o caractere subsequente (lookahead de 1) sem avançar o cursor.

        Returns:
            O próximo caractere ou o sentinela '\\0' caso esteja além do fim.
        """
        if self.cursor + 1 >= len(self.source_code):
            return "\0"
        return self.source_code[self.cursor + 1]

    def advance(self) -> str:
        """Consome e retorna o caractere atual, atualizando cursor, linha e coluna.

        Se o caractere consumido for quebra de linha ('\\n'), a linha é
        incrementada e a coluna é redefinida para 1. Para os demais caracteres,
        apenas a coluna é incrementada.

        Returns:
            O caractere consumido ou '\\0' caso já esteja no fim.
        """
        if self.is_at_end():
            return "\0"

        char = self.source_code[self.cursor]
        self.cursor += 1

        if char == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1

        return char

    def current_position(self) -> tuple[int, int]:
        """Retorna as coordenadas atuais no código-fonte.

        Returns:
            Tupla contendo (linha, coluna).
        """
        return self.line, self.column

    def __repr__(self) -> str:
        return (
            f"CharStream(cursor={self.cursor}, line={self.line}, column={self.column})"
        )
