from __future__ import annotations

from src.parser.nodes import (
    BinOpNode,
    BoolLiteralNode,
    FloatLiteralNode,
    IdentifierNode,
    IntLiteralNode,
    Node,
    NoneLiteralNode,
    ProgramNode,
    StringLiteralNode,
)


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

    def gen_expression(self, node: Node) -> str:
        """Converte um nó de expressão da AST para a sintaxe equivalente em Java.

        Args:
            node: Nó da AST representando um literal, identificador ou operação binária.

        Returns:
            String contendo a expressão formatada na sintaxe Java.

        Raises:
            ValueError: Se o nó de operação binária estiver incompleto ou se o tipo
                de nó não for suportado como expressão.
        """
        if isinstance(node, BoolLiteralNode):
            return "true" if node.value else "false"

        if isinstance(node, IntLiteralNode):
            return str(node.value)

        if isinstance(node, FloatLiteralNode):
            return str(node.value)

        if isinstance(node, StringLiteralNode):
            escaped = (
                node.value.replace("\\", "\\\\")
                .replace('"', '\\"')
                .replace("\n", "\\n")
                .replace("\t", "\\t")
                .replace("\r", "\\r")
            )
            return f'"{escaped}"'

        if isinstance(node, NoneLiteralNode):
            return "null"

        if isinstance(node, IdentifierNode):
            return node.name

        if isinstance(node, BinOpNode):
            if node.left is None or node.right is None:
                raise ValueError(
                    "BinOpNode requer ambos os operandos (left e right) para gerar código."
                )
            left_expr = self.gen_expression(node.left)
            right_expr = self.gen_expression(node.right)
            return f"({left_expr} {node.op} {right_expr})"

        raise ValueError(
            f"Nó de expressão não suportado na geração de código: {type(node).__name__}"
        )
