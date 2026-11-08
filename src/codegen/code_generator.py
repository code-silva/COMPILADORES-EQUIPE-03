from __future__ import annotations

from src.parser.nodes import ProgramNode

class CodeGenerator:
    """esse metodo é uma constante, cuja a utilidade é definir quantos espaços tem cada nível de indentação, no caso em Java é 4"""
    INDENT_SIZE: int = 4

    def __init__(self) -> None:
        self.indent_level: int = 0 #guarda o nível da indentação
        self.code_lines: list[str] = [] #lista de linhas de código na ordem já geradas

    """calcula os espaços e colaca a linha de código com sua indentação na lista"""
    def emit(self, code: str) -> None:
        prefix = " " * (self.indent_level * self.INDENT_SIZE)
        self.code_lines.append(f"{prefix}{code}")

    """soma +1 nível cada vez que abrir uma chave"""
    def indent(self) -> None:
        self.indent_level += 1

    """remove -1 nível cada vez que fechar uma chave"""
    def dedent(self) -> None: 
        if self.indent_level > 0:
            self.indent_level -= 1
        else:
            raise ValueError("A indentação não pode ter nível menor que 0.")

    """junta as linhas da lista em uma única string"""
    def get_code(self) -> str:
        return "\n".join(self.code_lines) + "\n"

    """gera o corpo da main vazio e devolve tudo com uma única string"""
    def generate(self, node: ProgramNode) -> str:
        self.indent_level = 0
        self.code_lines = []

        self.emit("public class Main {")
        self.indent()

        self.emit("public static void main(String[] args) {")
        self.indent()

        self.dedent()
        self.emit("}")

        self.dedent()
        self.emit("}")

        return self.get_code()