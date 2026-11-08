"""Analisador semântico base e navegação na AST (padrão Visitor)."""

from __future__ import annotations

from typing import Any

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

from .errors import SemanticError
from .symbol_table import Symbol, SymbolTable


class SemanticAnalyzer:
    """Analisador semântico baseado no padrão Visitor para percorrer a AST.

    Gerencia o ciclo de vida dos escopos léxicos/semânticos através de uma
    cadeia de ``SymbolTable`` (``global_scope`` e ``current_scope``) e despacha
    dinamicamente a visita de cada nó da árvore para o método
    ``visit_<NomeDaClasse>(node)``.

    Atributos:
        global_scope: Tabela de símbolos raiz correspondente ao escopo global.
        current_scope: Tabela de símbolos ativa no ponto atual da travessia.
    """

    _ARITHMETIC_OPERATORS = frozenset({"+", "-", "*", "/", "%"})
    _COMPARISON_OPERATORS = frozenset({"==", "!=", "<", ">", "<=", ">="})
    _NUMERIC_TYPES = frozenset({"int", "float"})

    def __init__(self) -> None:
        self.global_scope: SymbolTable = SymbolTable()
        self.current_scope: SymbolTable = self.global_scope

    # ==========================================================================
    # Gerenciamento de Escopos
    # ==========================================================================

    def enter_scope(self) -> SymbolTable:
        """Cria um novo escopo aninhado tendo ``current_scope`` como pai."""
        self.current_scope = SymbolTable(parent=self.current_scope)
        return self.current_scope

    def exit_scope(self) -> SymbolTable:
        """Retorna ao escopo pai do escopo atual.

        Raises:
            SemanticError: Se houver tentativa de sair do escopo global.
        """
        if self.current_scope.parent is None:
            raise SemanticError("Não é possível sair do escopo global", 0, 0)
        self.current_scope = self.current_scope.parent
        return self.current_scope

    # ==========================================================================
    # Ponto de Entrada e Despacho Visitor
    # ==========================================================================

    def analyze(self, node: ProgramNode) -> SymbolTable:
        """Ponto de entrada de alto nível para analisar um ``ProgramNode``.

        Args:
            node: Nó raiz da AST gerada pelo ``Parser``.

        Returns:
            A ``SymbolTable`` correspondente ao escopo global após a análise.
        """
        self.visit(node)
        return self.global_scope

    def visit(self, node: Node | None) -> Any:
        """Despacha a visita do nó para o método ``visit_<TipoDoNo>`` específico."""
        if node is None:
            return None

        method_name = f"visit_{type(node).__name__}"
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node: Node) -> None:
        """Fallback acionado quando um tipo de nó não possui visitor dedicado."""
        raise SemanticError(
            f"Nó da AST não suportado pelo analisador semântico: {type(node).__name__}",
            node.line,
            node.column,
        )

    def _visit_block(self, statements: list[Node], *, new_scope: bool = True) -> None:
        """Visita uma sequência de instruções, opcionalmente em um novo escopo."""
        if new_scope:
            self.enter_scope()
        try:
            for stmt in statements:
                self.visit(stmt)
        finally:
            if new_scope:
                self.exit_scope()

    # ==========================================================================
    # Inferência de Tipos
    # ==========================================================================

    def infer_type(self, node: Node) -> str:
        """Infere o tipo semântico de ``node`` via visitor correspondente.

        A travessia é delegada a ``visit()`` para preservar o despacho dinâmico
        e os hooks de subclasses. O resultado deve ser um nome de tipo textual.

        Raises:
            SemanticError: Se o nó não produzir um tipo textual ou se contiver
                um identificador não declarado.
        """
        result = self.visit(node)
        if isinstance(result, str):
            return result

        raise SemanticError(
            f"Não foi possível inferir o tipo do nó {type(node).__name__}",
            line=node.line,
            column=node.column,
        )

    @classmethod
    def _numeric_result_type(cls, left_type: str, right_type: str) -> str | None:
        """Retorna o tipo numérico promovido ou ``None`` se forem incompatíveis."""
        if left_type not in cls._NUMERIC_TYPES or right_type not in cls._NUMERIC_TYPES:
            return None
        if "float" in (left_type, right_type):
            return "float"
        return "int"

    @staticmethod
    def _incompatible_binop_error(
        node: BinOpNode, left_type: str, right_type: str
    ) -> SemanticError:
        """Cria o erro padronizado para uma operação binária incompatível."""
        return SemanticError(
            f"Operação binária incompatível: {left_type} {node.op} {right_type}",
            line=node.line,
            column=node.column,
        )

    @staticmethod
    def _is_assignable(target_type: str, value_type: str) -> bool:
        """Retorna se ``value_type`` pode ser atribuído a ``target_type``."""
        if target_type == value_type:
            return True
        return target_type == "float" and value_type == "int"

    def _infer_arithmetic_type(
        self, node: BinOpNode, left_type: str, right_type: str
    ) -> str:
        """Valida e infere o tipo de uma operação aritmética."""
        if node.op == "+" and left_type == right_type == "String":
            return "String"

        numeric_type = self._numeric_result_type(left_type, right_type)
        if numeric_type is None:
            raise self._incompatible_binop_error(node, left_type, right_type)

        if node.op == "/":
            return "float"
        return numeric_type

    def _infer_comparison_type(
        self, node: BinOpNode, left_type: str, right_type: str
    ) -> str:
        """Valida e infere o tipo ``'boolean'`` de uma comparação."""
        if self._numeric_result_type(left_type, right_type) is not None:
            return "boolean"
        if left_type == right_type == "boolean":
            return "boolean"
        raise self._incompatible_binop_error(node, left_type, right_type)

    # ==========================================================================
    # Métodos de Visita da AST (Visitors)
    # ==========================================================================

    def visit_ProgramNode(self, node: ProgramNode) -> SymbolTable:
        """Percorre todas as instruções de nível superior do programa."""
        for stmt in node.stmts:
            self.visit(stmt)
        return self.current_scope

    def visit_AssignNode(self, node: AssignNode) -> str:
        """Infere o valor, registra o símbolo e valida o tipo da atribuição."""
        if node.value is None:
            raise SemanticError(
                "Atribuição sem expressão de valor",
                line=node.line,
                column=node.column,
            )

        value_type = self.infer_type(node.value)
        symbol = self.current_scope.lookup(node.target)

        if symbol is None:
            self.current_scope.define(
                Symbol(
                    name=node.target,
                    type=value_type,
                    line=node.line,
                    column=node.column,
                )
            )
            return value_type

        if not self._is_assignable(symbol.type, value_type):
            raise SemanticError(
                f"Tipo incompatível na atribuição: variável '{node.target}' "
                f"é '{symbol.type}', mas recebeu '{value_type}'",
                line=node.line,
                column=node.column,
            )
        return value_type

    def visit_ReturnNode(self, node: ReturnNode) -> str:
        """Visita a expressão de retorno (se presente) e devolve seu tipo."""
        if node.value is not None:
            result = self.visit(node.value)
            return result if isinstance(result, str) else "None"
        return "None"

    def _validate_condition(
        self, condition: Node | None, construct: str, owner_node: Node
    ) -> str:
        """Valida que a expressão condicional de ``if``, ``elif`` ou ``while`` é ``'boolean'``."""
        if condition is None:
            raise SemanticError(
                f"Condição ausente na estrutura '{construct}'",
                line=owner_node.line,
                column=owner_node.column,
            )

        cond_type = self.infer_type(condition)
        if cond_type != "boolean":
            err_line = condition.line if condition.line > 0 else owner_node.line
            err_col = condition.column if condition.column > 0 else owner_node.column
            raise SemanticError(
                f"Condição inválida em '{construct}': esperado tipo 'boolean', "
                f"mas recebeu '{cond_type}'",
                line=err_line,
                column=err_col,
            )
        return cond_type

    def visit_IfNode(self, node: IfNode) -> None:
        """Valida a condição booleana e visita ``then``, ``elif`` e ``else`` em escopos próprios."""
        self._validate_condition(node.condition, "if", node)

        self._visit_block(node.then_body, new_scope=True)

        for elif_clause in node.elif_clauses:
            self.visit(elif_clause)

        if node.else_body:
            self._visit_block(node.else_body, new_scope=True)

    def visit_ElifClauseNode(self, node: ElifClauseNode) -> None:
        """Valida a condição booleana da cláusula ``elif`` e visita seu corpo em escopo próprio."""
        self._validate_condition(node.condition, "elif", node)
        self._visit_block(node.body, new_scope=True)

    def visit_ElseClauseNode(self, node: ElseClauseNode) -> None:
        """Visita o corpo de uma cláusula ``else`` em escopo próprio."""
        self._visit_block(node.body, new_scope=True)

    def visit_WhileNode(self, node: WhileNode) -> None:
        """Valida a condição booleana de repetição e visita o corpo do ``while`` em escopo próprio."""
        self._validate_condition(node.condition, "while", node)
        self._visit_block(node.body, new_scope=True)

    def visit_BinOpNode(self, node: BinOpNode) -> str:
        """Valida os operandos e infere o tipo resultante da operação binária."""
        if node.left is None or node.right is None:
            raise SemanticError(
                "Expressão binária com operando ausente",
                line=node.line,
                column=node.column,
            )

        left_type = self.infer_type(node.left)
        right_type = self.infer_type(node.right)

        if node.op in self._ARITHMETIC_OPERATORS:
            return self._infer_arithmetic_type(node, left_type, right_type)
        if node.op in self._COMPARISON_OPERATORS:
            return self._infer_comparison_type(node, left_type, right_type)

        raise SemanticError(
            f"Operador binário não suportado: '{node.op}'",
            line=node.line,
            column=node.column,
        )

    def visit_IdentifierNode(self, node: IdentifierNode) -> str:
        """Infere o tipo do identificador consultando a tabela de símbolos ativa."""
        symbol = self.current_scope.lookup(node.name)
        if symbol is None:
            raise SemanticError(
                f"Variável '{node.name}' não declarada",
                line=node.line,
                column=node.column,
            )
        return symbol.type

    def visit_IntLiteralNode(self, node: IntLiteralNode) -> str:
        """Infere o tipo ``'int'`` para literais inteiros."""
        return "int"

    def visit_FloatLiteralNode(self, node: FloatLiteralNode) -> str:
        """Infere o tipo ``'float'`` para literais de ponto flutuante."""
        return "float"

    def visit_StringLiteralNode(self, node: StringLiteralNode) -> str:
        """Infere o tipo ``'String'`` para literais de texto."""
        return "String"

    def visit_BoolLiteralNode(self, node: BoolLiteralNode) -> str:
        """Infere o tipo ``'boolean'`` para literais booleanos."""
        return "boolean"

    def visit_NoneLiteralNode(self, node: NoneLiteralNode) -> str:
        """Infere o tipo ``'None'`` para o literal nulo."""
        return "None"
