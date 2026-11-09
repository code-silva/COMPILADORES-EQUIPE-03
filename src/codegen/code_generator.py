from __future__ import annotations

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
    PrintNode,
    ProgramNode,
    ReturnNode,
    StringLiteralNode,
    WhileNode,
)
from src.semantic.analyzer import SemanticAnalyzer


class CodeGenerator:
    """esse metodo é uma constante, cuja a utilidade é definir quantos espaços tem cada nível de indentação, no caso em Java é 4"""
    INDENT_SIZE: int = 4

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

    def __init__(self) -> None:
        self.indent_level: int = 0 #guarda o nível da indentação
        self.code_lines: list[str] = [] #lista de linhas de código na ordem já geradas
        self.declared_vars: set[str] = set() #variáveis que já receberam declaração Java
        self._scope_stack: list[set[str]] = [self.declared_vars]
        self._analyzer: SemanticAnalyzer = SemanticAnalyzer() #fornece o tipo das variáveis

    def _is_declared(self, name: str) -> bool:
        """Verifica se ``name`` já foi declarada no escopo atual ou em escopos pais."""
        return any(name in scope for scope in reversed(self._scope_stack))

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
            for stmt in statements:
                self.visit(stmt)
        finally:
            self._exit_block_scope()
            self.dedent()

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
        self.declared_vars = set()
        self._scope_stack = [self.declared_vars]
        self._analyzer = SemanticAnalyzer()

        self.emit("public class Main {")
        self.indent()

        self.emit("public static void main(String[] args) {")
        self.indent()

        for stmt in node.stmts:
            self.visit(stmt)

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

    # ==========================================================================
    # Instruções (Issues #36 e #37)
    # ==========================================================================

    def visit(self, node: Node) -> None:
        """Despacha a geração de uma instrução para ``visit_<TipoDoNo>``.

        Raises:
            ValueError: Se o tipo de nó não possuir gerador de instrução.
        """
        visitor = getattr(self, f"visit_{type(node).__name__}", None)
        if visitor is None:
            raise ValueError(
                f"Instrução não suportada na geração de código: {type(node).__name__}"
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

    def visit_PrintNode(self, node: PrintNode) -> None:
        """Gera ``System.out.println(expr);`` (ou ``println()`` sem argumento)."""
        if node.value is None:
            self.emit("System.out.println();")
        else:
            self.emit(f"System.out.println({self.gen_expression(node.value)});")
