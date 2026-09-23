from char_stream import CharStream
from token import Token
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
    def _scan_number(self, start_line: int, start_col: int) -> Token:    
        pass

    #verifica se é um id ou uma palavra reservada    
    def _scan_identifier(self, start_line: int, start_col: int) -> Token:
        pass

    #verifica abertura e fechamento de " e ' até mesmo em caso de uso da \
    #bem como deve emitir ERROR se não estiver fechada
    def _scan_string(self, delimiter: str, start_line: int, start_col: int) -> Token:
        pass

    #verifica simbolos como =, +=, < 
    def next_token(self) -> Token:
        pass