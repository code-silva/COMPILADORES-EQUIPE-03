"""Testes unitários do Analisador Semântico base e navegação Visitor (#31).

Cobrem:
- Exceção ``SemanticError`` (atributos e formatação padronizada);
- Inicialização do ``SemanticAnalyzer`` e gerenciamento de escopos (``enter_scope``,
  ``exit_scope`` e restauração em caso de exceção);
- Travessia completa da AST via padrão Visitor (``ProgramNode``, ``AssignNode``,
  ``ReturnNode``, ``IfNode``, ``ElifClauseNode``, ``ElseClauseNode``, ``WhileNode``,
  ``BinOpNode``, ``IdentifierNode`` e literais);
- Isolamento de escopos ao entrar e sair de blocos condicionais e laços.
"""

from dataclasses import dataclass

import pytest

from src.parser import (
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
    Parser,
    ProgramNode,
    ReturnNode,
    StringLiteralNode,
    WhileNode,
)
from src.semantic import SemanticAnalyzer, SemanticError, Symbol, SymbolTable


class RecordingSemanticAnalyzer(SemanticAnalyzer):
    """Subclasse instrumentada que registra cada nó visitado e a profundidade do escopo."""

    def __init__(self) -> None:
        super().__init__()
        self.visited_nodes: list[str] = []
        self.visited_depths: list[tuple[str, int]] = []

    def visit(self, node: Node | None):
        if node is not None:
            name = type(node).__name__
            self.visited_nodes.append(name)
            self.visited_depths.append((name, self.current_scope.depth))
        return super().visit(node)


# ==============================================================================
# 1. Testes de SemanticError
# ==============================================================================


def test_semantic_error_stores_attributes_and_formats_message() -> None:
    """Verifica que SemanticError armazena message, line, column e formata __str__."""
    err = SemanticError("Variável 'x' não declarada", line=4, column=10)

    assert isinstance(err, Exception)
    assert err.message == "Variável 'x' não declarada"
    assert err.line == 4
    assert err.column == 10
    assert str(err) == "Erro Semântico [Linha 4, Coluna 10]: Variável 'x' não declarada"


def test_semantic_error_default_coordinates() -> None:
    """Verifica coordenadas padrão (line=0, column=0) em SemanticError."""
    err = SemanticError("Erro semântico genérico")
    assert err.line == 0
    assert err.column == 0
    assert "Linha 0, Coluna 0" in str(err)


# ==============================================================================
# 2. Inicialização e Gerenciamento de Escopos
# ==============================================================================


def test_analyzer_initializes_with_global_scope() -> None:
    """Garante que o analisador inicia no escopo global vazio (depth 0)."""
    analyzer = SemanticAnalyzer()
    assert isinstance(analyzer.current_scope, SymbolTable)
    assert analyzer.current_scope is analyzer.global_scope
    assert analyzer.current_scope.parent is None
    assert analyzer.current_scope.depth == 0


def test_enter_and_exit_scope_chain() -> None:
    """Verifica encadeamento correto ao entrar e sair de múltiplos escopos."""
    analyzer = SemanticAnalyzer()
    global_scope = analyzer.current_scope

    scope_1 = analyzer.enter_scope()
    assert analyzer.current_scope is scope_1
    assert scope_1.parent is global_scope
    assert scope_1.depth == 1

    scope_2 = analyzer.enter_scope()
    assert analyzer.current_scope is scope_2
    assert scope_2.parent is scope_1
    assert scope_2.depth == 2

    returned_1 = analyzer.exit_scope()
    assert returned_1 is scope_1
    assert analyzer.current_scope is scope_1

    returned_global = analyzer.exit_scope()
    assert returned_global is global_scope
    assert analyzer.current_scope is global_scope


def test_exit_global_scope_raises_semantic_error() -> None:
    """Garante que tentar sair do escopo global lança SemanticError."""
    analyzer = SemanticAnalyzer()
    with pytest.raises(SemanticError, match="Não é possível sair do escopo global"):
        analyzer.exit_scope()


# ==============================================================================
# 3. Travessia de ProgramNode e Nós da AST (Visitor)
# ==============================================================================


def test_visit_empty_program_node() -> None:
    """Verifica travessia de um ProgramNode vazio."""
    analyzer = RecordingSemanticAnalyzer()
    program = ProgramNode(stmts=[], line=1, column=1)

    result_scope = analyzer.analyze(program)

    assert result_scope is analyzer.global_scope
    assert analyzer.visited_nodes == ["ProgramNode"]


def test_visit_simple_program_visits_all_children() -> None:
    """Testa a travessia de um ProgramNode simples verificando se todos os nós filhos são visitados."""
    source = (
        "x = 10\n"
        "y = x + 2.5\n"
        "ativo = True\n"
        "msg = 'ok'\n"
        "nulo = None\n"
        "return y\n"
    )
    program = Parser(source).parse()
    analyzer = RecordingSemanticAnalyzer()
    analyzer.global_scope.define(Symbol(name="x", type="int", line=1))
    analyzer.global_scope.define(Symbol(name="y", type="float", line=2))

    analyzer.analyze(program)

    expected_sequence = [
        "ProgramNode",
        "AssignNode",
        "IntLiteralNode",
        "AssignNode",
        "BinOpNode",
        "IdentifierNode",
        "FloatLiteralNode",
        "AssignNode",
        "BoolLiteralNode",
        "AssignNode",
        "StringLiteralNode",
        "AssignNode",
        "NoneLiteralNode",
        "ReturnNode",
        "IdentifierNode",
    ]
    assert analyzer.visited_nodes == expected_sequence
    assert analyzer.current_scope is analyzer.global_scope


def test_visit_literals_returns_primitive_type_names() -> None:
    """Verifica que os visitors de literais retornam seus respectivos tipos primitivos."""
    analyzer = SemanticAnalyzer()

    assert analyzer.visit(IntLiteralNode(value=1)) == "int"
    assert analyzer.visit(FloatLiteralNode(value=1.5)) == "float"
    assert analyzer.visit(StringLiteralNode(value="abc")) == "String"
    assert analyzer.visit(BoolLiteralNode(value=True)) == "boolean"
    assert analyzer.visit(NoneLiteralNode()) == "None"
    assert analyzer.visit(None) is None


def test_visit_return_node_with_and_without_value() -> None:
    """Verifica visita de ReturnNode vazio e com expressão."""
    analyzer = SemanticAnalyzer()

    assert analyzer.visit(ReturnNode(value=None)) == "None"
    assert analyzer.visit(ReturnNode(value=IntLiteralNode(value=42))) == "int"


def test_visit_identifier_resolves_symbol_in_current_scope() -> None:
    """Verifica que visit_IdentifierNode consulta current_scope.lookup()."""
    analyzer = SemanticAnalyzer()
    analyzer.current_scope.define(Symbol(name="contador", type="int", line=1))

    assert analyzer.visit(IdentifierNode(name="contador")) == "int"
    with pytest.raises(
        SemanticError, match="Variável 'inexistente' não declarada"
    ) as exc_info:
        analyzer.visit(IdentifierNode(name="inexistente", line=3, column=7))

    assert exc_info.value.line == 3
    assert exc_info.value.column == 7


def test_infer_type_resolves_literals_and_symbols() -> None:
    """Verifica a inferência de tipos de literais e de identificadores declarados."""
    analyzer = SemanticAnalyzer()
    analyzer.current_scope.define(
        Symbol(name="total", type="float", line=1, column=1)
    )

    assert analyzer.infer_type(IntLiteralNode(value=1)) == "int"
    assert analyzer.infer_type(FloatLiteralNode(value=1.5)) == "float"
    assert analyzer.infer_type(StringLiteralNode(value="ok")) == "String"
    assert analyzer.infer_type(BoolLiteralNode(value=False)) == "boolean"
    assert analyzer.infer_type(NoneLiteralNode()) == "None"
    assert analyzer.infer_type(IdentifierNode(name="total")) == "float"


def test_generic_visit_raises_semantic_error_for_unknown_node() -> None:
    """Garante que um nó desconhecido aciona generic_visit e lança SemanticError."""

    @dataclass
    class UnknownCustomNode(Node):
        pass

    analyzer = SemanticAnalyzer()
    with pytest.raises(SemanticError, match="UnknownCustomNode") as exc_info:
        analyzer.visit(UnknownCustomNode(line=7, column=3))

    assert exc_info.value.line == 7
    assert exc_info.value.column == 3


# ==============================================================================
# 4. Isolamento de Escopos em Estruturas de Controle de Fluxo
# ==============================================================================


def test_scope_depth_during_control_flow_traversal() -> None:
    """Verifica que blocos if/elif/else e while são visitados em escopos aninhados (depth > 0)."""
    source = (
        "x = 0\n"
        "if x == 0:\n"
        "    y = 1\n"
        "elif x == 1:\n"
        "    y = 2\n"
        "else:\n"
        "    while x < 5:\n"
        "        x += 1\n"
        "return x\n"
    )
    program = Parser(source).parse()
    analyzer = RecordingSemanticAnalyzer()
    analyzer.global_scope.define(Symbol(name="x", type="int", line=1))

    analyzer.analyze(program)

    # Ao final da análise, o escopo ativo deve voltar ao global (depth 0)
    assert analyzer.current_scope is analyzer.global_scope
    assert analyzer.current_scope.depth == 0

    # Verifica profundidades registradas para os AssignNodes:
    # 1º AssignNode (x = 0) -> depth 0
    # 2º AssignNode (y = 1 no then) -> depth 1
    # 3º AssignNode (y = 2 no elif) -> depth 1
    # 4º AssignNode (x += 1 dentro do while que está dentro do else) -> depth 2
    assign_depths = [
        depth for node_name, depth in analyzer.visited_depths if node_name == "AssignNode"
    ]
    assert assign_depths == [0, 1, 1, 2]


def test_scope_isolation_between_blocks_and_parent() -> None:
    """Garante que símbolos definidos dentro de um bloco não vazam para o escopo pai ou blocos irmãos."""

    class ScopeTrackingAnalyzer(SemanticAnalyzer):
        """Registra símbolos no escopo corrente ao visitar AssignNode para testar isolamento."""

        def __init__(self) -> None:
            super().__init__()
            self.else_saw_then_var: Symbol | None = None

        def visit_AssignNode(self, node: AssignNode) -> str | None:
            inferred = super().visit_AssignNode(node) or "int"
            if self.current_scope.lookup_current_scope(node.target) is None:
                self.current_scope.define(
                    Symbol(
                        name=node.target,
                        type=inferred,
                        line=node.line,
                        column=node.column,
                    )
                )
            return inferred

        def visit_ReturnNode(self, node: ReturnNode) -> str:
            # Chamado dentro do bloco else: verifica se 'interna_then' vazou do bloco then
            self.else_saw_then_var = self.current_scope.lookup("interna_then")
            return super().visit_ReturnNode(node)

    source = (
        "global_var = 10\n"
        "if global_var > 0:\n"
        "    interna_then = 20\n"
        "else:\n"
        "    interna_else = 30\n"
        "    return global_var\n"
    )
    program = Parser(source).parse()
    analyzer = ScopeTrackingAnalyzer()
    analyzer.analyze(program)

    # 'global_var' permanece no escopo global
    assert analyzer.global_scope.lookup("global_var") is not None
    # Variáveis criadas dentro de then e else não existem no escopo global
    assert analyzer.global_scope.lookup("interna_then") is None
    assert analyzer.global_scope.lookup("interna_else") is None
    # O bloco else não enxergou a variável local criada no bloco irmão then
    assert analyzer.else_saw_then_var is None


def test_visit_else_clause_node_directly_creates_isolated_scope() -> None:
    """Verifica visita direta de ElseClauseNode gerenciando seu próprio escopo."""
    analyzer = RecordingSemanticAnalyzer()
    else_node = ElseClauseNode(
        body=[AssignNode(target="a", op="=", value=IntLiteralNode(value=1))],
        line=3,
        column=1,
    )

    analyzer.visit(else_node)

    assert analyzer.current_scope is analyzer.global_scope
    assert ("ElseClauseNode", 0) in analyzer.visited_depths
    assert ("AssignNode", 1) in analyzer.visited_depths
