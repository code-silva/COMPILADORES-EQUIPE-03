"""
src/lexer/lexer.py

Analisador lexico do PyToJava.

Converte codigo-fonte de um subconjunto de Python em uma sequencia de
tokens, incluindo tratamento de indentacao (INDENT / DEDENT), a parte
mais delicada de lexar uma linguagem sensivel a espacos.

Subconjunto coberto (ajustem conforme a definicao da equipe):
    - atribuicao:            x = 10
    - tipos literais:        int, float, str, bool (True/False), None
    - operadores:            + - * / % == != < > <= >= = and or not
    - estruturas de controle: if / elif / else, while, for x in range(...)
    - funcoes:                def nome(params): ... return expr
    - print(...)
    - comentarios com #
"""

from dataclasses import dataclass
import re


KEYWORDS = {
    "def", "return", "if", "elif", "else", "while", "for", "in",
    "print", "True", "False", "None", "and", "or", "not",
    "break", "continue",
}

# Ordem importa: padroes mais especificos primeiro.
TOKEN_SPEC = [
    ("NUMBER",   r"\d+\.\d+|\d+"),
    ("STRING",   r'"[^"\n]*"|\'[^\'\n]*\''),
    ("NAME",     r"[A-Za-z_][A-Za-z0-9_]*"),
    ("OP",       r"==|!=|<=|>=|\*\*|[+\-*/%=<>(),:]"),
    ("COMMENT",  r"\#.*"),
    ("WS",       r"[ \t]+"),
    ("MISMATCH", r"."),
]

MASTER_PATTERN = re.compile(
    "|".join(f"(?P<{name}>{pattern})" for name, pattern in TOKEN_SPEC)
)


@dataclass
class Token:
    type: str
    value: str
    line: int
    column: int

    def __repr__(self):
        return f"Token({self.type!r}, {self.value!r}, line={self.line}, col={self.column})"


class LexerError(Exception):
    def __init__(self, message, line, column):
        super().__init__(f"[Lexer] linha {line}, coluna {column}: {message}")
        self.line = line
        self.column = column


def tokenize(source: str):
    """
    Gera a lista de tokens de `source`.

    Emite NEWLINE ao final de cada linha logica nao vazia, INDENT/DEDENT
    quando o nivel de indentacao muda, e ENDMARKER no final do arquivo.
    """
    tokens = []
    indent_stack = [0]

    lines = source.split("\n")

    for line_no, raw_line in enumerate(lines, start=1):
        # Calcula indentacao (assume espacos; adaptem se usarem tabs)
        stripped = raw_line.lstrip(" ")
        indent = len(raw_line) - len(stripped)

        # Ignora linhas totalmente em branco ou so com comentario
        content = stripped.split("#", 1)[0].rstrip()
        if content == "":
            continue

        # Ajusta pilha de indentacao -> emite INDENT/DEDENT
        if indent > indent_stack[-1]:
            indent_stack.append(indent)
            tokens.append(Token("INDENT", "", line_no, 0))
        while indent < indent_stack[-1]:
            indent_stack.pop()
            tokens.append(Token("DEDENT", "", line_no, 0))
        if indent != indent_stack[-1]:
            raise LexerError("indentacao inconsistente", line_no, indent)

        # Tokeniza o conteudo da linha (sem a indentacao)
        pos = indent
        while pos < len(raw_line):
            match = MASTER_PATTERN.match(raw_line, pos)
            if match is None:
                raise LexerError(f"caractere inesperado {raw_line[pos]!r}", line_no, pos)

            kind = match.lastgroup
            value = match.group()
            pos = match.end()

            if kind == "WS":
                continue
            if kind == "COMMENT":
                break
            if kind == "MISMATCH":
                raise LexerError(f"token invalido {value!r}", line_no, pos)
            if kind == "NAME" and value in KEYWORDS:
                kind = value.upper()

            tokens.append(Token(kind, value, line_no, pos))

        tokens.append(Token("NEWLINE", "", line_no, len(raw_line)))

    # Fecha indentacoes pendentes no fim do arquivo
    while len(indent_stack) > 1:
        indent_stack.pop()
        tokens.append(Token("DEDENT", "", len(lines) + 1, 0))

    tokens.append(Token("ENDMARKER", "", len(lines) + 1, 0))
    return tokens


if __name__ == "__main__":
    # Uso rapido: python lexer.py caminho/para/arquivo.py
    import sys

    if len(sys.argv) != 2:
        print("Uso: python lexer.py <arquivo.py>")
        sys.exit(1)

    with open(sys.argv[1], encoding="utf-8") as f:
        source_code = f.read()

    for tok in tokenize(source_code):
        print(tok)
