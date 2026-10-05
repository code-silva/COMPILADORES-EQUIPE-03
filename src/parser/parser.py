"""Parser descendente recursivo para a gramática sintática inicial."""

from src.lexer.scanner import Scanner
from src.lexer.token import Token
from src.lexer.token_type import TokenType

from .errors import ParserError


class Parser:
    """Reconhece atribuições e expressões do subconjunto inicial de Python.

    Este primeiro incremento valida apenas a estrutura sintática. A construção
    da AST e os comandos compostos serão adicionados nas próximas etapas.
    """

    _ASSIGNMENT_OPERATORS = {
        TokenType.OP_ASSIGN,
        TokenType.OP_ADD_ASSIGN,
        TokenType.OP_SUB_ASSIGN,
    }
    _COMPARISON_OPERATORS = {
        TokenType.OP_EQ,
        TokenType.OP_NEQ,
        TokenType.OP_LT,
        TokenType.OP_LTE,
        TokenType.OP_GT,
        TokenType.OP_GTE,
    }
    _ADDITIVE_OPERATORS = {TokenType.OP_PLUS, TokenType.OP_MINUS}
    _MULTIPLICATIVE_OPERATORS = {TokenType.OP_MULT, TokenType.OP_DIV}
    _LITERALS = {
        TokenType.INT_LITERAL,
        TokenType.FLOAT_LITERAL,
        TokenType.STRING_LITERAL,
        TokenType.KW_TRUE,
        TokenType.KW_FALSE,
        TokenType.KW_NONE,
    }

    def __init__(self, source_code: str):
        self._tokens = self._scan(source_code)
        self._current = 0

    @staticmethod
    def _scan(source_code: str) -> list[Token]:
        scanner = Scanner(source_code)
        tokens: list[Token] = []
        while True:
            token = scanner.next_token()
            tokens.append(token)
            if token.type == TokenType.EOF:
                return tokens

    def parse(self) -> None:
        """Valida o programa e lança ``ParserError`` ao encontrar erro."""
        while not self._is_at_end():
            if self._match(TokenType.NEWLINE):
                continue

            self._statement()
            if not self._is_at_end():
                self._consume(
                    TokenType.NEWLINE,
                    "esperado fim de linha após a instrução",
                )

    def _statement(self) -> None:
        if (
            self._check(TokenType.IDENTIFIER)
            and self._peek_next().type in self._ASSIGNMENT_OPERATORS
        ):
            self._advance()
            self._advance()
            self._expression()
            return

        self._expression()

    def _expression(self) -> None:
        self._comparison()

    def _comparison(self) -> None:
        self._addition()
        while self._peek().type in self._COMPARISON_OPERATORS:
            self._advance()
            self._addition()

    def _addition(self) -> None:
        self._multiplication()
        while self._peek().type in self._ADDITIVE_OPERATORS:
            self._advance()
            self._multiplication()

    def _multiplication(self) -> None:
        self._unary()
        while self._peek().type in self._MULTIPLICATIVE_OPERATORS:
            self._advance()
            self._unary()

    def _unary(self) -> None:
        if self._peek().type in self._ADDITIVE_OPERATORS:
            self._advance()
            self._unary()
            return
        self._primary()

    def _primary(self) -> None:
        if self._peek().type in self._LITERALS or self._check(TokenType.IDENTIFIER):
            self._advance()
            return

        if self._match(TokenType.LPAREN):
            self._expression()
            self._consume(TokenType.RPAREN, "esperado ')' após a expressão")
            return

        raise ParserError("esperada uma expressão", self._peek())

    def _match(self, token_type: TokenType) -> bool:
        if not self._check(token_type):
            return False
        self._advance()
        return True

    def _consume(self, token_type: TokenType, message: str) -> Token:
        if self._check(token_type):
            return self._advance()
        raise ParserError(message, self._peek())

    def _check(self, token_type: TokenType) -> bool:
        return self._peek().type == token_type

    def _advance(self) -> Token:
        token = self._peek()
        if not self._is_at_end():
            self._current += 1
        return token

    def _is_at_end(self) -> bool:
        return self._peek().type == TokenType.EOF

    def _peek(self) -> Token:
        return self._tokens[self._current]

    def _peek_next(self) -> Token:
        next_index = min(self._current + 1, len(self._tokens) - 1)
        return self._tokens[next_index]
