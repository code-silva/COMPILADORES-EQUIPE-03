"""Analisador léxico (Scanner) do compilador PyToJava."""

from __future__ import annotations

from collections import deque

from src.lexer.char_stream import CharStream
from src.lexer.errors import LexicalError
from src.lexer.indent_manager import (
    finalize_indentation,
    process_indentation,
    reset_indent_manager,
)
from src.lexer.token import Token
from src.lexer.token_type import TokenType


class Scanner:
    """Analisador léxico determinístico com controle de pilha de indentação.

    Converte o código-fonte Python em uma sequência de objetos ``Token``,
    aplicando a regra do maior casamento (*maximal munch*), descartando
    comentários e linhas em branco e emitindo tokens sintéticos ``INDENT``,
    ``DEDENT`` e ``NEWLINE``.
    """

    KEYWORDS: dict[str, TokenType] = {
        "class": TokenType.KW_CLASS,
        "def": TokenType.KW_DEF,
        "self": TokenType.KW_SELF,
        "if": TokenType.KW_IF,
        "elif": TokenType.KW_ELIF,
        "else": TokenType.KW_ELSE,
        "while": TokenType.KW_WHILE,
        "return": TokenType.KW_RETURN,
        "True": TokenType.KW_TRUE,
        "False": TokenType.KW_FALSE,
        "None": TokenType.KW_NONE,
    }

    _DELIMITERS: dict[str, TokenType] = {
        ":": TokenType.COLON,
        "(": TokenType.LPAREN,
        ")": TokenType.RPAREN,
    }

    _ARITH_OPERATORS: frozenset[str] = frozenset({"+", "-", "*", "/"})
    _REL_OPERATORS: frozenset[str] = frozenset({"=", "!", "<", ">"})
    _QUOTES: frozenset[str] = frozenset({'"', "'"})
    _INLINE_WHITESPACE: frozenset[str] = frozenset({" ", "\t"})
    _LINE_BREAKS: frozenset[str] = frozenset({"\r", "\n"})
    _NON_INDENT_LINE_STARTS: frozenset[str] = frozenset({"\r", "\n", "#", "\0"})
    _STRING_ESCAPES: dict[str, str] = {
        "n": "\n",
        "\\": "\\",
        '"': '"',
        "'": "'",
    }

    def __init__(self, source_code: str) -> None:
        """Inicializa o scanner com o código-fonte e reinicia a pilha de indentação."""
        self.stream: CharStream = CharStream(source_code)
        self.pending_tokens: deque[Token] = deque()
        self.at_line_start: bool = True
        self.line_has_tokens: bool = False
        reset_indent_manager()

    def _scan_number(self, line: int, column: int) -> Token:
        """Reconhece literais numéricos inteiros (``INT_LITERAL``) ou decimais (``FLOAT_LITERAL``)."""
        stream = self.stream
        start = stream.cursor
        is_float = False

        while not stream.is_at_end() and stream.peek().isdigit():
            stream.advance()

        if not stream.is_at_end() and stream.peek() == "." and stream.peek_next().isdigit():
            is_float = True
            stream.advance()
            while not stream.is_at_end() and stream.peek().isdigit():
                stream.advance()

        lexeme = stream.source_code[start : stream.cursor]
        if is_float:
            return Token(TokenType.FLOAT_LITERAL, lexeme, float(lexeme), line, column)
        return Token(TokenType.INT_LITERAL, lexeme, int(lexeme), line, column)

    def _scan_identifier(self, line: int, column: int) -> Token:
        """Reconhece identificadores ou palavras reservadas da linguagem."""
        stream = self.stream
        start = stream.cursor

        while not stream.is_at_end():
            ch = stream.peek()
            if ch.isalnum() or ch == "_":
                stream.advance()
            else:
                break

        lexeme = stream.source_code[start : stream.cursor]
        token_type = self.KEYWORDS.get(lexeme, TokenType.IDENTIFIER)
        return Token(token_type, lexeme, None, line, column)

    def _scan_string(self, start_line: int, start_col: int) -> Token:
        """Reconhece literais de string delimitados por aspas simples ou duplas."""
        stream = self.stream
        quote_type = stream.advance()
        chars: list[str] = []
        escapes = self._STRING_ESCAPES

        while not stream.is_at_end():
            character = stream.peek()
            if character == quote_type or character in self._LINE_BREAKS:
                break
            if character == "\\":
                stream.advance()
                if stream.is_at_end() or stream.peek() in self._LINE_BREAKS:
                    raise LexicalError("literal de string não terminado", start_line, start_col)
                next_char = stream.advance()
                chars.append(escapes.get(next_char, next_char))
            else:
                chars.append(stream.advance())

        if stream.is_at_end() or stream.peek() in self._LINE_BREAKS:
            raise LexicalError("literal de string não terminado", start_line, start_col)

        stream.advance()
        value = "".join(chars)
        return Token(TokenType.STRING_LITERAL, value, value, start_line, start_col)

    def _scan_delimiter(self, line: int, column: int) -> Token:
        """Reconhece delimitadores pontuais ``:``, ``(`` e ``)``."""
        character = self.stream.advance()
        return Token(self._DELIMITERS[character], character, None, line, column)

    def _scan_operator(self, line: int, column: int) -> Token:
        """Reconhece operadores aritméticos e de atribuição composta (``+``, ``+=``, ``-``, ``-=``, ``*``, ``/``)."""
        stream = self.stream
        character = stream.advance()
        if character == "+":
            if stream.peek() == "=":
                stream.advance()
                return Token(TokenType.OP_ADD_ASSIGN, "+=", None, line, column)
            return Token(TokenType.OP_PLUS, "+", None, line, column)

        if character == "-":
            if stream.peek() == "=":
                stream.advance()
                return Token(TokenType.OP_SUB_ASSIGN, "-=", None, line, column)
            return Token(TokenType.OP_MINUS, "-", None, line, column)

        if character == "*":
            return Token(TokenType.OP_MULT, "*", None, line, column)

        return Token(TokenType.OP_DIV, "/", None, line, column)

    def _scan_relational_operator(self, line: int, column: int) -> Token:
        """Reconhece operadores de atribuição simples e relacionais (``=``, ``==``, ``!=``, ``<``, ``<=``, ``>``, ``>=``)."""
        stream = self.stream
        character = stream.advance()
        if character == "=":
            if stream.peek() == "=":
                stream.advance()
                return Token(TokenType.OP_EQ, "==", None, line, column)
            return Token(TokenType.OP_ASSIGN, "=", None, line, column)

        if character == "!":
            if stream.peek() == "=":
                stream.advance()
                return Token(TokenType.OP_NEQ, "!=", None, line, column)
            raise LexicalError("caractere inválido '!'", line, column)

        if character == "<":
            if stream.peek() == "=":
                stream.advance()
                return Token(TokenType.OP_LTE, "<=", None, line, column)
            return Token(TokenType.OP_LT, "<", None, line, column)

        if stream.peek() == "=":
            stream.advance()
            return Token(TokenType.OP_GTE, ">=", None, line, column)
        return Token(TokenType.OP_GT, ">", None, line, column)

    def _skip_whitespace(self) -> None:
        """Consome espaços e tabulações horizontais no meio da linha."""
        stream = self.stream
        while not stream.is_at_end() and stream.peek() in self._INLINE_WHITESPACE:
            stream.advance()

    def _skip_comment(self) -> None:
        """Descarta comentários iniciados por ``#`` até o final da linha física."""
        stream = self.stream
        while not stream.is_at_end() and stream.peek() not in self._LINE_BREAKS:
            stream.advance()

    def _scan_newline(self) -> Token | None:
        """Consome quebra de linha (``\\n`` ou ``\\r\\n``) e emite ``NEWLINE`` se a linha continha tokens."""
        stream = self.stream
        line = stream.line
        column = stream.column

        char = stream.advance()
        if char == "\r" and stream.peek() == "\n":
            stream.advance()
        had_tokens = self.line_has_tokens
        self.at_line_start = True
        self.line_has_tokens = False
        if not had_tokens:
            return None
        return Token(TokenType.NEWLINE, "\n", None, line, column)

    def _process_line_indentation(self) -> None:
        """Mede o recuo inicial de uma linha lógica e enfileira tokens ``INDENT``/``DEDENT``."""
        stream = self.stream
        self.at_line_start = False
        start_line = stream.line
        start_col = stream.column

        indent_level = 0
        while not stream.is_at_end() and stream.peek() in self._INLINE_WHITESPACE:
            if stream.advance() == "\t":
                indent_level += 4
            else:
                indent_level += 1

        if not stream.is_at_end() and stream.peek() not in self._NON_INDENT_LINE_STARTS:
            tokens = process_indentation(indent_level, start_line, start_col)
            if tokens:
                self.pending_tokens.extend(tokens)

    def _finalize_and_get_eof(self) -> Token:
        """Desempilha os níveis de indentação pendentes no fim do arquivo e emite ``EOF``."""
        line = self.stream.line
        column = self.stream.column
        dedent_tokens = finalize_indentation(line, column)
        if dedent_tokens:
            if self.line_has_tokens:
                self.pending_tokens.append(Token(TokenType.NEWLINE, "\n", None, line, column))
            self.pending_tokens.extend(dedent_tokens)
            return self.pending_tokens.popleft()
        return Token(TokenType.EOF, "", None, line, column)

    def next_token(self) -> Token:
        """Retorna o próximo token válido do código-fonte ou lança ``LexicalError``."""
        stream = self.stream
        pending = self.pending_tokens

        while True:
            if pending:
                return pending.popleft()

            if self.at_line_start:
                self._process_line_indentation()
                if pending:
                    return pending.popleft()

            self._skip_whitespace()

            if stream.is_at_end():
                return self._finalize_and_get_eof()

            ch = stream.peek()
            if ch in self._LINE_BREAKS:
                newline_token = self._scan_newline()
                if newline_token is not None:
                    return newline_token
                continue

            if ch == "#":
                self._skip_comment()
                continue
            break

        character = stream.peek()
        line = stream.line
        column = stream.column

        if character.isdigit():
            token = self._scan_number(line, column)
        elif character.isalpha() or character == "_":
            token = self._scan_identifier(line, column)
        elif character in self._QUOTES:
            token = self._scan_string(line, column)
        elif character in self._ARITH_OPERATORS:
            token = self._scan_operator(line, column)
        elif character in self._DELIMITERS:
            token = self._scan_delimiter(line, column)
        elif character in self._REL_OPERATORS:
            token = self._scan_relational_operator(line, column)
        else:
            stream.advance()
            raise LexicalError(f"caractere inválido '{character}'", line, column)

        self.line_has_tokens = True
        return token

    def scan(self) -> list[Token]:
        """Percorre todo o código-fonte e retorna a lista de tokens até ``EOF``."""
        tokens: list[Token] = []
        append = tokens.append
        next_tok = self.next_token
        eof_type = TokenType.EOF
        while True:
            token = next_tok()
            append(token)
            if token.type == eof_type:
                return tokens
