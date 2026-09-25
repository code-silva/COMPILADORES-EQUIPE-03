from src.lexer.char_stream import CharStream
from src.lexer.token import Token
from src.lexer.token_type import TokenType
from collections import deque
from src.lexer.indent_manager import (finalize_indentation, process_indentation, reset_indent_manager)

class Scanner:

    #dicionário de palavras reservadas do python para consultas
    KEYWORDS = {
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

    #construtor com a instância do CharStream
    def __init__(self, source_code: str):
        self.stream = CharStream(source_code)
        self.pending_tokens = deque()
        self.at_line_start = True
        reset_indent_manager()

    #verifica se é int ou float 
    def _scan_number(self, line: int, column: int) -> Token:    
        lexeme = ""
    
        #aqui ele roda enquanto não chega no final do código. EX: x = 45 ou enquanto é um digito (aqui ele lê só a parte inteira)
        while not self.stream.is_at_end() and self.stream.peek().isdigit():
            lexeme += self.stream.peek()
            self.stream.advance()

        #aqui ele checa se não tá no final e se o caractere é um ponto (.)    
        if not self.stream.is_at_end() and self.stream.peek() == ".":
            if self.stream.peek_next().isdigit():
                lexeme += self.stream.peek()
                self.stream.advance()
                while not self.stream.is_at_end() and self.stream.peek().isdigit():
                    lexeme += self.stream.peek()
                    self.stream.advance()
        if '.' in lexeme:
            return Token(TokenType.FLOAT_LITERAL, lexeme, float(lexeme), line, column)
        return Token(TokenType.INT_LITERAL, lexeme, int(lexeme), line, column)
        
    #verifica se é um id ou uma palavra reservada    
    def _scan_identifier(self, line: int, column: int) -> Token:
        lexeme = ""
        while not self.stream.is_at_end() and (self.stream.peek().isalnum() or self.stream.peek() == "_"):
             lexeme += self.stream.peek()
             self.stream.advance()
        tokenType = self.KEYWORDS.get(lexeme, TokenType.IDENTIFIER)
        return Token(tokenType, lexeme, None, line, column)

        
    #verifica abertura e fechamento de " e ' até mesmo em caso de uso da \
    #bem como deve emitir ERROR se não estiver fechada(verifica a existencia de uma string)
    def _scan_string(self, start_line: int, start_col: int) -> Token:
        quote_type = self.stream.peek() 
        self.stream.advance() 
        value = ""

        #aqui roda encquanto o caractere encontrado não é " ou '
        while not self.stream.is_at_end() and self.stream.peek() != quote_type:
            character = self.stream.peek()
            if character == '\\':
                self.stream.advance()
                if self.stream.is_at_end():
                    break
                next_char = self.stream.peek()
                escapes = {'n': '\n', '\\': '\\', '"': '"', "'": "'"}
                value += escapes.get(next_char, next_char)
            else:
                value += character
            self.stream.advance()

        #aqui só executa se chegar ao fim sem ter fechado as aspas    
        if self.stream.is_at_end():    
            return Token(TokenType.ERROR, value, "String não fechada", start_line, start_col)
        self.stream.advance()
        return Token(TokenType.STRING_LITERAL, value, value, start_line, start_col) 
   
    #verifica ':', '(' e ')'
    def _scan_demiliter(self, line: int, column: int):
        character = self.stream.peek()
        self.stream.advance()
        if character == ':':
                return Token(TokenType.COLON, ":", None,  line, column )
        elif character == '(':
                return Token(TokenType.LPAREN, "(", None,  line, column)
        elif character == ')':
                 return Token(TokenType.RPAREN, ")", None, line, column)

    #verifica '+', '+=', '-=', '*' e '/'
    def _scan_operator(self, line: int, column: int):
            character = self.stream.peek()
            if character == '+':
                character = self.stream.peek_next()
                if character == '=':
                     self.stream.advance()
                     self.stream.advance()
                     return Token(TokenType.OP_ADD_ASSIGN, "+=", None, line, column)
                self.stream.advance()
                return Token(TokenType.OP_PLUS, "+", None, line, column)
                
            elif character == '-':
                character = self.stream.peek_next()
                if character == '=':
                    self.stream.advance()
                    self.stream.advance()
                    return Token(TokenType.OP_SUB_ASSIGN, "-=", None, line, column)
                self.stream.advance()
                return Token(TokenType.OP_MINUS, "-", None, line, column)
            
            elif character == '*':
                 self.stream.advance()
                 return Token(TokenType.OP_MULT, "*", None, line, column)
            
            elif character == '/':
                self.stream.advance()
                return Token(TokenType.OP_DIV, "/", None, line, column)

    #verifica '=', '==', '!=', '<', '<=', '>' e '>='
    def _scan_RelationalOperator(self, line: int, column: int):
       character = self.stream.peek()
       if character == "=":
            character = self.stream.peek_next()
            if character == "=":
                 self.stream.advance()
                 self.stream.advance()
                 return Token(TokenType.OP_EQ, "==", None, line, column)
            self.stream.advance()
            return Token(TokenType.OP_ASSIGN, "=", None, line, column) 
       
       elif character == "!":
            character = self.stream.peek_next()
            if character == "=":
                    self.stream.advance()
                    self.stream.advance()
                    return Token(TokenType.OP_NEQ, "!=", None, line, column)
            self.stream.advance()
            return Token(TokenType.ERROR, "!", f"Caractere inválido: '{character}'", line, column) 
       
       elif character == "<":
            character = self.stream.peek_next()
            if character == "=":
                self.stream.advance()
                self.stream.advance()
                return Token(TokenType.OP_LTE , "<=", None, line, column)
            self.stream.advance()
            return Token(TokenType.OP_LT, "<", None, line, column)
       
       elif character == ">":
            character = self.stream.peek_next()
            if character == "=":
                self.stream.advance()
                self.stream.advance()
                return Token(TokenType.OP_GTE , ">=", None, line, column)
            self.stream.advance()
            return Token(TokenType.OP_GT, ">", None, line, column)
       
    #aqui ignora espaços em branco
    def _skip_whitespace(self) -> None:
        while not self.stream.is_at_end() and self.stream.peek() in (" ", "\t"):
            self.stream.advance()

    #aqui ignora comentário
    def _skip_comment(self) -> None:
        while not self.stream.is_at_end() and self.stream.peek() not in ("\n", "\r",):
            self.stream.advance()

    #aqui scanea nova linha e indica que vai inicializar uma nova 
    def _scan_newline(self) -> Token:
        line = self.stream.line
        column = self.stream.column

        char = self.stream.advance()
        if char == "\r" and self.stream.peek() == "\n":
            self.stream.advance()
        self.at_line_start = True 
        return Token(TokenType.NEWLINE, "\n", None, line, column)   

    #esse metodo processa a indentação
    def _process_line_indentation(self) -> None:
        self.at_line_start = False
        start_line = self.stream.line
        start_col = self.stream.column

        #aqui é onde o recuo é contado
        indent_level = 0
        while self.stream.peek() in (" ", "\t"):
            if self.stream.peek() == "\t":
                indent_level += 4
            else:
                indent_level += 1
            self.stream.advance()

        #envia para o IndentManager e processa a indentação
        if self.stream.peek() not in ("\r", "\n", "#", ""):
            tokens = process_indentation(indent_level, start_line, start_col)
            if tokens:
                self.pending_tokens.extend(tokens) 

    #envia DEDENT pedentes e retorna o token EOF
    def _finalize_and_get_eof(self) -> Token:
        line = self.stream.line
        column = self.stream.column
        dedent_tokens = finalize_indentation(line, column)
        if dedent_tokens:
            self.pending_tokens.extend(dedent_tokens)
            return self.pending_tokens.popleft()
        return Token(TokenType.EOF, "", None, line, column)

    #esse metodo é o coração do scanner ele roda todos os outros scanners 
    def next_token(self) -> Token:
        #aqui é onde guarda  tokens de identação na fila 
        while True:
            if self.pending_tokens:
                return self.pending_tokens.popleft()

            #roda toda vez que inicializa uma linha
            if self.at_line_start:
                self._process_line_indentation()
                if self.pending_tokens:
                    return self.pending_tokens.popleft() 
                
            if self.stream.is_at_end():
                return self._finalize_and_get_eof()

            self._skip_whitespace()

            if self.stream.peek() == "#":
                self._skip_comment()
                continue

            if self.stream.peek() in ("\r", "\n"):
                return self._scan_newline()
            break
            
        character = self.stream.peek()
        line = self.stream.line
        column = self.stream.column

        if character.isdigit():
            token = self._scan_number(line, column)
            return token
        elif character.isalpha() or character == '_':
            return self._scan_identifier(line, column)
        elif character in ('"', "'"):
            return self._scan_string(line, column)    
        elif character in ['+', '-', '*', '/']:
            token = self._scan_operator(line, column)
            return token
        elif character in [':', '(', ')']:
            token = self._scan_demiliter(line, column)
            return token
        elif character in ['=', '!', '<', '>']:
            token = self._scan_RelationalOperator(line, column)
            return token
        
        self.stream.advance()
        return Token(TokenType.ERROR, "", f"Caractere inválido: '{character}'", self.stream.line, self.stream.column)