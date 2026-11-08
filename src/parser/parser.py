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
    ElifClauseNode,
    FloatLiteralNode,
    IdentifierNode,
    IfNode,
    IntLiteralNode,
    Node,
    NoneLiteralNode,
    ProgramNode,
    ReturnNode,
    StringLiteralNode,
    WhileNode,
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
        """Verifica se o token atual pertence a ``token_types`` e o consome em caso positivo.

        Raises:
            TypeError: se algum argumento não for uma instância de ``TokenType``.
            ParserError: se o token atual for ``TokenType.ERROR``.
        """
        for expected_type in token_types:
            if not isinstance(expected_type, TokenType):
                raise TypeError(
                    f"Esperado TokenType em match(), mas recebido {type(expected_type).__name__}"
                )

        token = self.peek()
        if token.type == TokenType.ERROR and TokenType.ERROR not in token_types:
            raise ParserError(
                token.lexeme or "Token de erro léxico encontrado",
                token.line,
                token.column,
            )

        if token.type in token_types:
            self.advance()
            return True
        return False

    def expect(self, token_type: TokenType, message: str | None = None) -> Token:
        """Exige que o token atual seja do tipo ``token_type``, lançando ``ParserError`` caso contrário.

        Raises:
            TypeError: se ``token_type`` não for uma instância de ``TokenType``.
            ParserError: se o token atual não corresponder ao esperado.
        """
        if not isinstance(token_type, TokenType):
            raise TypeError(
                f"Esperado TokenType em expect(), mas recebido {type(token_type).__name__}"
            )

        token = self.peek()
        if token.type == token_type:
            return self.advance()

        if token.type == TokenType.ERROR:
            raise ParserError(
                token.lexeme or "Token de erro léxico encontrado",
                token.line,
                token.column,
            )

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
    # Ponto de Entrada
    # ==========================================================================

    def parse(self) -> ProgramNode:
        """Analisa o programa inteiro e devolve o nó raiz ``ProgramNode``.

        Consome tokens até encontrar ``EOF``, ignorando quebras de linha
        (``NEWLINE``) extras no escopo global e delegando cada instrução a
        ``parse_statement()``.

        Raises:
            ParserError: se houver indentação inesperada no escopo global ou
                qualquer violação gramatical nas instruções.
        """
        program = ProgramNode(line=1, column=1)

        while True:
            while self.match(TokenType.NEWLINE):
                pass

            token = self.peek()
            if token.type == TokenType.EOF:
                return program

            if token.type in (TokenType.INDENT, TokenType.DEDENT):
                raise ParserError(
                    "Indentação inesperada no escopo global",
                    token.line,
                    token.column,
                )

            program.stmts.append(self.parse_statement())

    # ==========================================================================
    # Parsing de Estruturas de Controle de Fluxo
    # ==========================================================================

    def parse_block(self) -> list[Node]:
        """Analisa um bloco indentado delimitado por ``COLON`` e ``INDENT``/``DEDENT``.

        Consome obrigatoriamente ``COLON`` e ``NEWLINE``, valida e consome a
        abertura de escopo (``INDENT``), analisa as instruções internas via
        ``parse_statement()`` até encontrar o ``DEDENT`` correspondente e o
        consome ao encerrar o bloco.

        Returns:
            Lista de nós que compõem o corpo do bloco.

        Raises:
            ParserError: se ``COLON``/``NEWLINE``/``INDENT`` estiverem ausentes
                ou se o bloco terminar em ``EOF`` antes do ``DEDENT``.
        """
        self.expect(TokenType.COLON, "Esperado ':' ao iniciar o bloco")
        self.expect(TokenType.NEWLINE, "Esperado fim de linha após ':'")
        self.expect(TokenType.INDENT, "Esperado bloco indentado após ':'")

        statements: list[Node] = []
        while self.peek().type != TokenType.DEDENT:
            if self.peek().type == TokenType.EOF:
                token = self.peek()
                raise ParserError(
                    "Bloco indentado não finalizado: esperado DEDENT",
                    token.line,
                    token.column,
                )
            if self.match(TokenType.NEWLINE):
                continue
            statements.append(self.parse_statement())

        self.expect(TokenType.DEDENT, "Esperado DEDENT ao encerrar o bloco")
        return statements

    def parse_if_statement(self) -> IfNode:
        """Analisa ``if``/``elif``/``else`` e devolve um ``IfNode``.

        A condição do ``if`` é analisada por ``parse_expression()`` e o corpo
        principal por ``parse_block()``. Em seguida, são processadas zero ou
        mais cláusulas ``elif`` (cada uma como ``ElifClauseNode``) e o bloco
        opcional ``else`` (armazenado em ``else_body``).
        """
        keyword = self.expect(TokenType.KW_IF, "Esperado 'if'")

        condition = self.parse_expression()
        then_body = self.parse_block()

        elif_clauses: list[ElifClauseNode] = []
        while self.peek().type == TokenType.KW_ELIF:
            elif_keyword = self.advance()
            elif_condition = self.parse_expression()
            elif_body = self.parse_block()
            elif_clauses.append(
                ElifClauseNode(
                    condition=elif_condition,
                    body=elif_body,
                    line=elif_keyword.line,
                    column=elif_keyword.column,
                )
            )

        else_body: list[Node] = []
        if self.match(TokenType.KW_ELSE):
            else_body = self.parse_block()

        return IfNode(
            condition=condition,
            then_body=then_body,
            elif_clauses=elif_clauses,
            else_body=else_body,
            line=keyword.line,
            column=keyword.column,
        )

    def parse_while_statement(self) -> WhileNode:
        """Analisa ``while`` e devolve um ``WhileNode``.

        A condição é analisada por ``parse_expression()`` e o corpo do laço
        por ``parse_block()``.
        """
        keyword = self.expect(TokenType.KW_WHILE, "Esperado 'while'")

        condition = self.parse_expression()
        body = self.parse_block()

        return WhileNode(
            condition=condition,
            body=body,
            line=keyword.line,
            column=keyword.column,
        )

    # ==========================================================================
    # Parsing de Instruções Simples
    # ==========================================================================

    def parse_statement(self) -> Node:
        """Identifica o tipo de instrução no token atual e delega o parsing.

        - ``if`` → ``parse_if_statement()``;
        - ``while`` → ``parse_while_statement()``;
        - ``return`` → ``parse_return_statement()``;
        - ``IDENTIFIER`` seguido de ``=``, ``+=`` ou ``-=`` → ``parse_assignment()``;
        - qualquer outra construção é analisada como expressão.

        Instruções compostas já consomem seu próprio ``NEWLINE`` e ``DEDENT``.
        Para instruções simples, exige que terminem em ``NEWLINE`` (consumido),
        ``DEDENT`` ou ``EOF`` (não consumidos).
        """
        token = self.peek()

        if token.type in (TokenType.KW_ELIF, TokenType.KW_ELSE):
            raise ParserError(
                f"Cláusula '{token.lexeme}' sem 'if' correspondente",
                token.line,
                token.column,
            )

        if token.type == TokenType.KW_IF:
            return self.parse_if_statement()
        if token.type == TokenType.KW_WHILE:
            return self.parse_while_statement()

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
