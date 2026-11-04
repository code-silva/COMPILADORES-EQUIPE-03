"""Analisador sintático (Parser): expressões, instruções simples e programa."""

from __future__ import annotations

from src.lexer.scanner import Scanner
from src.lexer.token import Token
from src.lexer.token_type import TokenType

from .errors import ParserError
from .nodes import (
    AssignNode,
    BinOpNode,
    BoolLiteralNode,
    FloatLiteralNode,
    IdentifierNode,
    IntLiteralNode,
    Node,
    NoneLiteralNode,
    ReturnNode,
    StringLiteralNode,
)


class Parser:
    """Analisador sintático recursivo descendente com Precedence Climbing.

    Consome uma lista de tokens gerada pelo ``Scanner`` e constrói a
    Árvore Sintática Abstrata (AST) correspondente às expressões da linguagem,
    respeitando a precedência e a associatividade à esquerda dos operadores.
    """

    PRECEDENCE: dict[TokenType, int] = {
        TokenType.OP_EQ: 10,
        TokenType.OP_NEQ: 10,
        TokenType.OP_LT: 10,
        TokenType.OP_LTE: 10,
        TokenType.OP_GT: 10,
        TokenType.OP_GTE: 10,
        TokenType.OP_PLUS: 20,
        TokenType.OP_MINUS: 20,
        TokenType.OP_MULT: 30,
        TokenType.OP_DIV: 30,
    }

    UNARY_OPERATORS: set[TokenType] = {
        TokenType.OP_PLUS,
        TokenType.OP_MINUS,
    }

    ASSIGNMENT_OPERATORS: set[TokenType] = {
        TokenType.OP_ASSIGN,
        TokenType.OP_ADD_ASSIGN,
        TokenType.OP_SUB_ASSIGN,
    }

    # Tokens que encerram uma instrução simples. ``DEDENT`` e ``EOF`` não são
    # consumidos pela instrução: pertencem a quem fecha o bloco ou o programa.
    STATEMENT_TERMINATORS: set[TokenType] = {
        TokenType.NEWLINE,
        TokenType.DEDENT,
        TokenType.EOF,
    }

    def __init__(self, tokens: list[Token] | str) -> None:
        """Inicializa o parser com a sequência de tokens do Scanner.

        Args:
            tokens: Lista de objetos ``Token`` gerada pelo ``Scanner``
                (ou string de código-fonte para tokenização direta).
        """
        if isinstance(tokens, str):
            tokens = self._tokenize_source(tokens)

        self.tokens: list[Token] = list(tokens)
        if not self.tokens:
            self.tokens.append(Token(TokenType.EOF, "", None, 1, 1))
        elif self.tokens[-1].type != TokenType.EOF:
            last = self.tokens[-1]
            self.tokens.append(Token(TokenType.EOF, "", None, last.line, last.column))

        self.current: int = 0

    @staticmethod
    def _tokenize_source(source_code: str) -> list[Token]:
        """Converte código-fonte diretamente em lista de tokens via Scanner."""
        scanner = Scanner(source_code)
        result: list[Token] = []
        while True:
            tok = scanner.next_token()
            result.append(tok)
            if tok.type == TokenType.EOF:
                break
        return result

    # ==========================================================================
    # Métodos Auxiliares de Navegação
    # ==========================================================================

    def peek(self, offset: int = 0) -> Token:
        """Retorna o token atual (ou deslocado por ``offset``) sem consumi-lo."""
        index = self.current + offset
        if index < 0:
            return self.tokens[0]
        if index >= len(self.tokens):
            return self.tokens[-1]
        return self.tokens[index]

    def advance(self) -> Token:
        """Consome o token atual e avança o cursor de leitura."""
        token = self.peek()
        if token.type != TokenType.EOF and self.current < len(self.tokens) - 1:
            self.current += 1
        return token

    def match(self, *token_types: TokenType) -> bool:
        """Verifica se o token atual pertence a ``token_types`` e o consome em caso positivo."""
        if self.peek().type in token_types:
            self.advance()
            return True
        return False

    def expect(self, token_type: TokenType, message: str | None = None) -> Token:
        """Exige que o token atual seja do tipo ``token_type``, lançando ``ParserError`` caso contrário."""
        token = self.peek()
        if token.type == token_type:
            return self.advance()

        error_msg = message or (
            f"Esperado token {token_type.name}, mas encontrado "
            f"{token.type.name} ('{token.lexeme}')"
        )
        raise ParserError(error_msg, token.line, token.column)

    # ==========================================================================
    # Parsing de Expressões e Precedência de Operadores
    # ==========================================================================

    def parse_primary(self) -> Node:
        """Analisa expressões primárias: literais, identificadores, keywords e parênteses."""
        token = self.peek()

        if token.type == TokenType.INT_LITERAL:
            self.advance()
            val = token.literal if token.literal is not None else int(token.lexeme)
            return IntLiteralNode(value=int(val), line=token.line, column=token.column)

        if token.type == TokenType.FLOAT_LITERAL:
            self.advance()
            val = token.literal if token.literal is not None else float(token.lexeme)
            return FloatLiteralNode(value=float(val), line=token.line, column=token.column)

        if token.type == TokenType.STRING_LITERAL:
            self.advance()
            val = token.literal if token.literal is not None else token.lexeme
            return StringLiteralNode(value=str(val), line=token.line, column=token.column)

        if token.type == TokenType.KW_TRUE:
            self.advance()
            return BoolLiteralNode(value=True, line=token.line, column=token.column)

        if token.type == TokenType.KW_FALSE:
            self.advance()
            return BoolLiteralNode(value=False, line=token.line, column=token.column)

        if token.type == TokenType.KW_NONE:
            self.advance()
            return NoneLiteralNode(line=token.line, column=token.column)

        if token.type == TokenType.IDENTIFIER:
            self.advance()
            return IdentifierNode(name=token.lexeme, line=token.line, column=token.column)

        if token.type == TokenType.LPAREN:
            self.advance()
            expr = self.parse_expression()
            self.expect(TokenType.RPAREN, "Esperado ')' após a expressão agrupada")
            return expr

        raise ParserError(
            f"Token inesperado ao analisar expressão primária: '{token.lexeme}' ({token.type.name})",
            token.line,
            token.column,
        )

    def parse_unary(self) -> Node:
        """Analisa operadores unários prefixados (``+`` e ``-``) ou delega para ``parse_primary()``."""
        token = self.peek()
        if token.type in self.UNARY_OPERATORS:
            op_token = self.advance()
            operand = self.parse_unary()
            return BinOpNode(
                left=IntLiteralNode(value=0, line=op_token.line, column=op_token.column),
                op=op_token.lexeme,
                right=operand,
                line=op_token.line,
                column=op_token.column,
            )

        return self.parse_primary()

    def parse_expression(self, precedence: int = 0) -> Node:
        """Analisa expressões binárias e unárias via Precedence Climbing.

        Args:
            precedence: Nível mínimo de precedência exigido para continuar
                agrupando operadores binários na sub-árvore atual (padrão: 0).

        Returns:
            Nó da AST representando a expressão analisada.
        """
        left = self.parse_unary()

        while True:
            token = self.peek()
            op_precedence = self.PRECEDENCE.get(token.type)
            if op_precedence is None or op_precedence <= precedence:
                break

            op_token = self.advance()
            right = self.parse_expression(op_precedence)
            left = BinOpNode(
                left=left,
                op=op_token.lexeme,
                right=right,
                line=op_token.line,
                column=op_token.column,
            )

        return left

    # ==========================================================================
    # Parsing de Instruções Simples
    # ==========================================================================

    def parse_statement(self) -> Node:
        """Identifica o tipo de instrução no token atual e delega o parsing.

        - ``return`` → ``parse_return_statement()``;
        - ``IDENTIFIER`` seguido de ``=``, ``+=`` ou ``-=`` → ``parse_assignment()``;
        - qualquer outra construção é analisada como expressão.

        Ao final, exige que a instrução termine em ``NEWLINE`` (consumido),
        ``DEDENT`` ou ``EOF`` (não consumidos).
        """
        token = self.peek()

        if token.type == TokenType.KW_RETURN:
            node = self.parse_return_statement()
        elif (
            token.type == TokenType.IDENTIFIER
            and self.peek(1).type in self.ASSIGNMENT_OPERATORS
        ):
            node = self.parse_assignment()
        else:
            node = self.parse_expression()

        self._end_simple_statement()
        return node

    def parse_assignment(self) -> AssignNode:
        """Analisa ``IDENTIFIER ("=" | "+=" | "-=") expressao``.

        Returns:
            ``AssignNode`` com o nome do alvo, o operador e a expressão
            atribuída, posicionado no identificador de destino.
        """
        target = self.expect(
            TokenType.IDENTIFIER, "Esperado identificador no início da atribuição"
        )

        op_token = self.peek()
        if op_token.type not in self.ASSIGNMENT_OPERATORS:
            raise ParserError(
                f"Esperado operador de atribuição ('=', '+=' ou '-='), "
                f"mas encontrado '{op_token.lexeme}' ({op_token.type.name})",
                op_token.line,
                op_token.column,
            )
        self.advance()

        value = self.parse_expression()
        return AssignNode(
            target=target.lexeme,
            op=op_token.lexeme,
            value=value,
            line=target.line,
            column=target.column,
        )

    def parse_return_statement(self) -> ReturnNode:
        """Analisa ``"return" expressao?``.

        Se o token após ``return`` já encerrar a instrução, gera um retorno
        vazio (``value=None``); caso contrário, analisa a expressão retornada.
        """
        keyword = self.expect(TokenType.KW_RETURN, "Esperado 'return'")

        value = None
        if self.peek().type not in self.STATEMENT_TERMINATORS:
            value = self.parse_expression()

        return ReturnNode(value=value, line=keyword.line, column=keyword.column)

    def _end_simple_statement(self) -> None:
        """Garante que a instrução simples terminou no token atual."""
        token = self.peek()
        if token.type == TokenType.NEWLINE:
            self.advance()
            return
        if token.type in (TokenType.DEDENT, TokenType.EOF):
            return
        raise ParserError(
            f"Esperado fim de linha após a instrução, mas encontrado "
            f"'{token.lexeme}' ({token.type.name})",
            token.line,
            token.column,
        )
