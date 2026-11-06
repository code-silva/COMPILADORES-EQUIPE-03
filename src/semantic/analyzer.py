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
from .symbol_table import SymbolTable


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
        """Infere o tipo semântico de ``node``.

        Literais são mapeados para os nomes de tipo usados na etapa de geração
        de código; identificadores são resolvidos na tabela de símbolos ativa.

        Raises:
            SemanticError: Se o identificador não estiver declarado ou se o nó
                não produzir um tipo textual.
        """
        if isinstance(node, IntLiteralNode):
            return "int"
        if isinstance(node, FloatLiteralNode):
            return "float"
        if isinstance(node, StringLiteralNode):
            return "String"
        if isinstance(node, BoolLiteralNode):
            return "boolean"
        if isinstance(node, NoneLiteralNode):
            return "None"

        if isinstance(node, IdentifierNode):
            symbol = self.current_scope.lookup(node.name)
            if symbol is None:
                raise SemanticError(
                    f"Variável '{node.name}' não declarada",
                    line=node.line,
                    column=node.column,
                )
            return symbol.type

        raise SemanticError(
            f"Não foi possível inferir o tipo do nó {type(node).__name__}",
            line=node.line,
            column=node.column,
        )

    # ==========================================================================
    # Métodos de Visita da AST (Visitors)
    # ==========================================================================

    def visit_ProgramNode(self, node: ProgramNode) -> SymbolTable:
        """Percorre todas as instruções de nível superior do programa."""
        for stmt in node.stmts:
            self.visit(stmt)
        return self.current_scope

    def visit_AssignNode(self, node: AssignNode) -> str | None:
        """Visita a expressão atribuída em uma instrução de atribuição."""
        if node.value is not None:
            return self.visit(node.value)
        return None

    def visit_ReturnNode(self, node: ReturnNode) -> str:
        """Visita a expressão de retorno (se presente) e devolve seu tipo."""
        if node.value is not None:
            result = self.visit(node.value)
            return result if isinstance(result, str) else "None"
        return "None"

    def visit_IfNode(self, node: IfNode) -> None:
        """Visita a condição, o bloco ``then``, as cláusulas ``elif`` e o ``else``."""
        if node.condition is not None:
            self.visit(node.condition)

        self._visit_block(node.then_body, new_scope=True)

        for elif_clause in node.elif_clauses:
            self.visit(elif_clause)

        if node.else_body:
            self._visit_block(node.else_body, new_scope=True)

    def visit_ElifClauseNode(self, node: ElifClauseNode) -> None:
        """Visita a condição da cláusula ``elif`` e seu corpo em escopo próprio."""
        if node.condition is not None:
            self.visit(node.condition)
        self._visit_block(node.body, new_scope=True)

    def visit_ElseClauseNode(self, node: ElseClauseNode) -> None:
        """Visita o corpo de uma cláusula ``else`` em escopo próprio."""
        self._visit_block(node.body, new_scope=True)

    def visit_WhileNode(self, node: WhileNode) -> None:
        """Visita a condição de repetição e o corpo do laço ``while`` em escopo próprio."""
        if node.condition is not None:
            self.visit(node.condition)
        self._visit_block(node.body, new_scope=True)

    def visit_BinOpNode(self, node: BinOpNode) -> str | None:
        """Visita recursivamente os operandos esquerdo e direito da operação binária."""
        if node.left is not None:
            self.visit(node.left)
        if node.right is not None:
            self.visit(node.right)
        return None

    def visit_IdentifierNode(self, node: IdentifierNode) -> str:
        """Infere o tipo do identificador consultando a tabela de símbolos ativa."""
        return self.infer_type(node)

    def visit_IntLiteralNode(self, node: IntLiteralNode) -> str:
        """Infere o tipo ``'int'`` para literais inteiros."""
        return self.infer_type(node)

    def visit_FloatLiteralNode(self, node: FloatLiteralNode) -> str:
        """Infere o tipo ``'float'`` para literais de ponto flutuante."""
        return self.infer_type(node)

    def visit_StringLiteralNode(self, node: StringLiteralNode) -> str:
        """Infere o tipo ``'String'`` para literais de texto."""
        return self.infer_type(node)

    def visit_BoolLiteralNode(self, node: BoolLiteralNode) -> str:
        """Infere o tipo ``'boolean'`` para literais booleanos."""
        return self.infer_type(node)

    def visit_NoneLiteralNode(self, node: NoneLiteralNode) -> str:
        """Infere o tipo ``'None'`` para o literal nulo."""
        return self.infer_type(node)
