"""Gerador de código Java a partir da Árvore Sintática Abstrata (AST)."""

from __future__ import annotations

from typing import Any, Callable

from src.parser.nodes import (
    AssignNode,
    BinOpNode,
    BoolLiteralNode,
    ElifClauseNode,
    ElseClauseNode,
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
from src.semantic.analyzer import SemanticAnalyzer


class CodeGenerator:
    """Traduz a AST validada de Python procedural para código-fonte Java formatado."""

    INDENT_SIZE: int = 4

    # Cache pré-alocado de prefixos de indentação (4 espaços por nível).
    _INDENT_PREFIXES: tuple[str, ...] = tuple(" " * (level * 4) for level in range(32))

    # Tipos semânticos do analisador -> tipos Java usados nas declarações.
    JAVA_TYPES: dict[str, str] = {
        "int": "int",
        "float": "double",
        "String": "String",
        "boolean": "boolean",
        "None": "Object",
    }

    # Operadores de atribuição aceitos pelo gerador.
    ASSIGN_OPERATORS: frozenset[str] = frozenset({"=", "+=", "-="})

    _VISITOR_DISPATCH: dict[type[Node], Callable[[CodeGenerator, Any], None]] = {}

    def __init__(self) -> None:
        self.indent_level: int = 0
        self.code_lines: list[str] = []
        self.declared_vars: set[str] = set()
        self._scope_stack: list[set[str]] = [self.declared_vars]
        self._analyzer: SemanticAnalyzer = SemanticAnalyzer()

    def _is_declared(self, name: str) -> bool:
        """Verifica se ``name`` já foi declarada no escopo atual ou em escopos pais."""
        for scope in reversed(self._scope_stack):
            if name in scope:
                return True
        return False

    def _enter_block_scope(self) -> None:
        """Abre um novo escopo léxico de bloco no analisador e na pilha de declarações."""
        self._analyzer.enter_scope()
        new_scope: set[str] = set()
        self._scope_stack.append(new_scope)
        self.declared_vars = new_scope

    def _exit_block_scope(self) -> None:
        """Fecha o escopo de bloco atual e restaura o escopo pai."""
        self._scope_stack.pop()
        self.declared_vars = self._scope_stack[-1]
        self._analyzer.exit_scope()

    def _emit_block_body(self, statements: list[Node]) -> None:
        """Emite uma lista de instruções dentro de um bloco indentado com escopo próprio."""
        self.indent()
        self._enter_block_scope()
        try:
            visit = self.visit
            for stmt in statements:
                visit(stmt)
        finally:
            self._exit_block_scope()
            self.dedent()

    def emit(self, code: str) -> None:
        """Adiciona uma linha de código Java precedida pela indentação atual."""
        level = self.indent_level
        if self.INDENT_SIZE == 4 and level < len(self._INDENT_PREFIXES):
            prefix = self._INDENT_PREFIXES[level]
        else:
            prefix = " " * (level * self.INDENT_SIZE)
        self.code_lines.append(f"{prefix}{code}" if prefix else code)

    def indent(self) -> None:
        """Incrementa o nível de indentação atual em 1."""
        self.indent_level += 1

    def dedent(self) -> None:
        """Decrementa o nível de indentação atual em 1.

        Raises:
            ValueError: Se o nível de indentação já estiver em 0.
        """
        if self.indent_level > 0:
            self.indent_level -= 1
        else:
            raise ValueError("A indentação não pode ter nível menor que 0.")

    def get_code(self) -> str:
        """Une as linhas emitidas em uma única string terminada por quebra de linha."""
        return "\n".join(self.code_lines) + "\n"

    def generate(self, node: ProgramNode) -> str:
        """Gera a classe ``Main`` completa em Java a partir de um ``ProgramNode``."""
        self.indent_level = 0
        self.code_lines = []
        self.declared_vars = set()
        self._scope_stack = [self.declared_vars]
        self._analyzer = SemanticAnalyzer()

        self.emit("public class Main {")
        self.indent()

        self.emit("public static void main(String[] args) {")
        self.indent()

        visit = self.visit
        for stmt in node.stmts:
            visit(stmt)

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
        node_type = type(node)

        if node_type is IdentifierNode or isinstance(node, IdentifierNode):
            return node.name

        if node_type is IntLiteralNode or isinstance(node, IntLiteralNode):
            return str(node.value)

        if node_type is BinOpNode or isinstance(node, BinOpNode):
            if node.left is None or node.right is None:
                raise ValueError(
                    "BinOpNode requer ambos os operandos (left e right) para gerar código."
                )
            left_expr = self.gen_expression(node.left)
            right_expr = self.gen_expression(node.right)
            return f"({left_expr} {node.op} {right_expr})"

        if node_type is FloatLiteralNode or isinstance(node, FloatLiteralNode):
            return str(node.value)

        if node_type is StringLiteralNode or isinstance(node, StringLiteralNode):
            escaped = (
                node.value.replace("\\", "\\\\")
                .replace('"', '\\"')
                .replace("\n", "\\n")
                .replace("\t", "\\t")
                .replace("\r", "\\r")
            )
            return f'"{escaped}"'

        if node_type is BoolLiteralNode or isinstance(node, BoolLiteralNode):
            return "true" if node.value else "false"

        if node_type is NoneLiteralNode or isinstance(node, NoneLiteralNode):
            return "null"

        raise ValueError(
            f"Nó de expressão não suportado na geração de código: {node_type.__name__}"
        )

    # ==========================================================================
    # Instruções (Issues #36 e #37)
    # ==========================================================================

    def visit(self, node: Node) -> None:
        """Despacha a geração de uma instrução para ``visit_<TipoDoNo>``.

        Raises:
            ValueError: Se o tipo de nó não possuir gerador de instrução.
        """
        node_type = type(node)
        if type(self) is CodeGenerator:
            handler = self._VISITOR_DISPATCH.get(node_type)
            if handler is not None:
                handler(self, node)
                return
        visitor = getattr(self, f"visit_{node_type.__name__}", None)
        if visitor is None:
            raise ValueError(
                f"Instrução não suportada na geração de código: {node_type.__name__}"
            )
        visitor(node)

    def java_type(self, semantic_type: str) -> str:
        """Converte um tipo do analisador semântico para o tipo Java equivalente.

        Raises:
            ValueError: Se o tipo não tiver correspondente em Java.
        """
        try:
            return self.JAVA_TYPES[semantic_type]
        except KeyError:
            raise ValueError(
                f"Tipo sem correspondente em Java: {semantic_type}"
            ) from None

    def visit_AssignNode(self, node: AssignNode) -> None:
        """Gera a declaração tipada ou a atribuição Java de um ``AssignNode``.

        Na primeira atribuição de uma variável emite ``tipo alvo = expr;``,
        com o tipo obtido do analisador semântico. Nas seguintes emite
        ``alvo op expr;`` (``=``, ``+=`` ou ``-=``).

        Raises:
            ValueError: Se faltar alvo ou valor, se o operador não for suportado
                ou se uma atribuição acumulativa usar variável não declarada.
        """
        if not node.target:
            raise ValueError("AssignNode requer um alvo (target) para gerar código.")
        if node.value is None:
            raise ValueError("AssignNode requer um valor (value) para gerar código.")
        if node.op not in self.ASSIGN_OPERATORS:
            raise ValueError(f"Operador de atribuição não suportado: {node.op!r}")

        is_first = not self._is_declared(node.target)
        if is_first and node.op != "=":
            raise ValueError(
                f"Atribuição acumulativa '{node.op}' em variável não declarada: "
                f"{node.target}"
            )

        value_expr = self.gen_expression(node.value)
        # O analisador registra a variável na primeira vez e valida as seguintes.
        value_type = self._analyzer.visit(node)

        if is_first:
            java_type = self.java_type(value_type)
            self.emit(f"{java_type} {node.target} = {value_expr};")
            self.declared_vars.add(node.target)
        else:
            self.emit(f"{node.target} {node.op} {value_expr};")

    def visit_ReturnNode(self, node: ReturnNode) -> None:
        """Gera ``return expr;`` ou ``return;`` para um ``ReturnNode``."""
        if node.value is None:
            self.emit("return;")
        else:
            self.emit(f"return {self.gen_expression(node.value)};")

    def visit_IfNode(self, node: IfNode) -> None:
        """Traduz ``IfNode`` (com ``elif_clauses`` e ``else_body``) para ``if / else if / else`` em Java."""
        if node.condition is None:
            raise ValueError("IfNode requer uma condição (condition) para gerar código.")

        self._analyzer._validate_condition(node.condition, "if", node)
        cond_expr = self.gen_expression(node.condition)
        self.emit(f"if ({cond_expr}) {{")
        self._emit_block_body(node.then_body)

        for elif_clause in node.elif_clauses:
            self.visit_ElifClauseNode(elif_clause)

        if node.else_body:
            if len(node.else_body) == 1 and isinstance(node.else_body[0], ElseClauseNode):
                self.visit_ElseClauseNode(node.else_body[0])
            else:
                self.emit("} else {")
                self._emit_block_body(node.else_body)

        self.emit("}")

    def visit_ElifClauseNode(self, node: ElifClauseNode) -> None:
        """Traduz ``ElifClauseNode`` encadeando ``} else if (condição) {`` em Java."""
        if node.condition is None:
            raise ValueError(
                "ElifClauseNode requer uma condição (condition) para gerar código."
            )

        self._analyzer._validate_condition(node.condition, "elif", node)
        elif_cond_expr = self.gen_expression(node.condition)
        self.emit(f"}} else if ({elif_cond_expr}) {{")
        self._emit_block_body(node.body)

    def visit_ElseClauseNode(self, node: ElseClauseNode) -> None:
        """Traduz ``ElseClauseNode`` encadeando ``} else {`` em Java."""
        self.emit("} else {")
        self._emit_block_body(node.body)

    def visit_WhileNode(self, node: WhileNode) -> None:
        """Traduz ``WhileNode`` para ``while (condição) { ... }`` em Java."""
        if node.condition is None:
            raise ValueError(
                "WhileNode requer uma condição (condition) para gerar código."
            )

        self._analyzer._validate_condition(node.condition, "while", node)
        cond_expr = self.gen_expression(node.condition)
        self.emit(f"while ({cond_expr}) {{")
        self._emit_block_body(node.body)
        self.emit("}")


CodeGenerator._VISITOR_DISPATCH = {
    AssignNode: CodeGenerator.visit_AssignNode,
    ReturnNode: CodeGenerator.visit_ReturnNode,
    IfNode: CodeGenerator.visit_IfNode,
    ElifClauseNode: CodeGenerator.visit_ElifClauseNode,
    ElseClauseNode: CodeGenerator.visit_ElseClauseNode,
    WhileNode: CodeGenerator.visit_WhileNode,
}
