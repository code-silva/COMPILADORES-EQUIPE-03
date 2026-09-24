from src.lexer.char_stream import CharStream
from src.lexer.token import Token
from src.lexer.token_type import TokenType

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

    #verifica se é int ou float 
    def _scan_number(self, line: int, column: int) -> Token:    
        lexeme = ""
    
        #aqui ele roda enquanto não chega no final do código. EX: x = 45 ou enquanto é um digito (aqui ele lê só a parte inteira)
        while not self.stream.is_at_end() and self.stream.peek().isdigit():
            lexeme += self.stream.peek
            self.stream.advance

        #aqui ele checa se não tá no final e se o caractere é um ponto (.)    
        if not self.stream.is_at_end() and self.stream.peek() == ".":
            if self.stream.peek_next().isdigit():
                lexeme += self.stream.peek()
                self.stream.advance()
                while not self.stream.is_at_end and self.stream.peek().isdigit():
                    lexeme += self.stream.peek()
                    self.stream.advance()
        if '.' in lexeme:
            return Token(TokenType.FLOAT_LITERAL, lexeme, float(lexeme), line, column)
        return Token(TokenType.FLOAT_LITERAL, lexeme, float(lexeme), line, column)
        
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
        pass    
   
    #verifica ':', '(' e ')'
    def _scan_demiliter(self, line: int, column: int):
        character = self.stream.peek()
        self.stream.advance()
        if character == ':':
                return Token(TokenType.COLON, ":", None,  line, column )
        elif character == '(':
                return Token(TokenType.LPAREN, "(", None,  line, column)
        elif character == ')':
                 return Token(TokenType.LPAREN, ")", None, line, column)

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
            return Token(TokenType.ERROR, "!", None, line, column) 
       
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

    def next_token(self) -> Token:
        #o loop é executado enquanto não for o fim do código
        while not self.stream.is_at_end():

            character = self.stream.peek()

            if character == ' ' or character == '\n':
                self.stream.advance()
                continue

            line = self.stream.line
            column = self.stream.column
            
            if character in ['+', '-', '*', '/']:
                token = self._scan_operator(line, column)
                return token
            elif character in [':', '(', ')']:
                token = self._scan_demiliter(line, column)
                return token
            elif character in ['=', '!', '<', '>']:
                token = self._scan_RelationalOperator(line, column)
            self.stream.advance()
        return Token(TokenType.EOF, "", None, self.stream.line, self.stream.column)