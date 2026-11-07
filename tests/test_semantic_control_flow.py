"""Suíte de Testes Unitários: Verificação Semântica de Controle de Fluxo e Escopos de Bloco (Issue #33).

Valida no ``SemanticAnalyzer``:
1. Exigência de condições do tipo ``'boolean'`` em ``IfNode``, ``ElifClauseNode`` e ``WhileNode``.
2. Rejeição com ``SemanticError`` (incluindo linha e coluna) para condições numéricas, textuais ou nulas.
3. Criação e destruição de escopos locais em blocos ``if``, ``elif``, ``else`` e ``while``, impedindo vazamento de variáveis locais para o escopo externo ou blocos irmãos.
4. Acesso e reatribuição de variáveis do escopo externo dentro de blocos aninhados.
"""

import pytest

from src.parser import (
    ElifClauseNode,
    IfNode,
    IntLiteralNode,
    Parser,
    ProgramNode,
    WhileNode,
)
from src.semantic import SemanticAnalyzer, SemanticError, SymbolTable


def analyze_source(source_code: str) -> SymbolTable:
    """Auxiliar que executa Parser + SemanticAnalyzer sobre um código Python."""
    program: ProgramNode = Parser(source_code).parse()
    analyzer = SemanticAnalyzer()
    return analyzer.analyze(program)


# ==============================================================================
# 1. Condições Booleanas Válidas em if, elif e while
# ==============================================================================


@pytest.mark.parametrize(
    "source",
    [
        "if True:\n    x = 1\n",
        "if False:\n    x = 1\nelse:\n    x = 2\n",
        "ativo = True\nif ativo:\n    x = 10\n",
        "a = 10\nb = 20\nif a < b:\n    menor = a\nelif a == b:\n    menor = 0\nelse:\n    menor = b\n",
        "contador = 0\nwhile contador < 5:\n    contador += 1\n",
        "continuar = True\nwhile continuar:\n    continuar = False\n",
    ],
)
def test_valid_boolean_conditions_in_if_elif_and_while(source: str) -> None:
    """Verifica que condições booleanas (literais, variáveis e comparações) são aceitas."""
    scope = analyze_source(source)
    assert isinstance(scope, SymbolTable)


# ==============================================================================
# 2. Rejeição de Condições Não-Booleanas (if, elif, while)
# ==============================================================================


@pytest.mark.parametrize(
    ("condition_expr", "expected_type"),
    [
        ("1", "int"),
        ("0", "int"),
        ("42", "int"),
        ("3.14", "float"),
        ('"texto"', "String"),
        ("None", "None"),
        ("10 + 5", "int"),
        ("10 / 2", "float"),
    ],
)
def test_if_non_boolean_condition_raises_semantic_error(
    condition_expr: str, expected_type: str
) -> None:
    """Garante que passar condição não booleana no 'if' lança SemanticError com o tipo inferido."""
    source = f"if {condition_expr}:\n    x = 1\n"
    with pytest.raises(
        SemanticError,
        match=f"Condição inválida em 'if': esperado tipo 'boolean', mas recebeu '{expected_type}'",
    ) as exc_info:
        analyze_source(source)

    assert exc_info.value.line == 1


@pytest.mark.parametrize(
    ("condition_expr", "expected_type"),
    [
        ("100", "int"),
        ("2.5", "float"),
        ('"invalido"', "String"),
        ("None", "None"),
    ],
)
def test_elif_non_boolean_condition_raises_semantic_error(
    condition_expr: str, expected_type: str
) -> None:
    """Garante que passar condição não booleana no 'elif' lança SemanticError na linha correta."""
    source = (
        "x = 10\n"
        "if x > 0:\n"
        "    y = 1\n"
        f"elif {condition_expr}:\n"
        "    y = 2\n"
    )
    with pytest.raises(
        SemanticError,
        match=f"Condição inválida em 'elif': esperado tipo 'boolean', mas recebeu '{expected_type}'",
    ) as exc_info:
        analyze_source(source)

    assert exc_info.value.line == 4


@pytest.mark.parametrize(
    ("condition_expr", "expected_type"),
    [
        ("10", "int"),
        ("0.0", "float"),
        ('"loop"', "String"),
        ("None", "None"),
        ("x + 1", "int"),
    ],
)
def test_while_non_boolean_condition_raises_semantic_error(
    condition_expr: str, expected_type: str
) -> None:
    """Garante que passar condição não booleana no 'while' lança SemanticError."""
    source = f"x = 1\nwhile {condition_expr}:\n    x += 1\n"
    with pytest.raises(
        SemanticError,
        match=f"Condição inválida em 'while': esperado tipo 'boolean', mas recebeu '{expected_type}'",
    ) as exc_info:
        analyze_source(source)

    assert exc_info.value.line == 2


def test_non_boolean_variable_in_condition_raises_semantic_error() -> None:
    """Verifica que usar uma variável numérica ou String diretamente como condição falha."""
    source = (
        "quantidade = 5\n"
        "if quantidade:\n"
        "    x = 1\n"
    )
    with pytest.raises(
        SemanticError,
        match="Condição inválida em 'if': esperado tipo 'boolean', mas recebeu 'int'",
    ) as exc_info:
        analyze_source(source)

    assert exc_info.value.line == 2
    assert exc_info.value.column == 4


def test_undeclared_variable_in_condition_raises_semantic_error() -> None:
    """Verifica que usar variável não declarada na condição do if/while lança SemanticError."""
    with pytest.raises(SemanticError, match="Variável 'inexistente' não declarada") as exc_info:
        analyze_source("if inexistente > 0:\n    x = 1\n")

    assert exc_info.value.line == 1


def test_missing_condition_in_ast_nodes_raises_semantic_error() -> None:
    """Garante que nós IfNode, ElifClauseNode e WhileNode sem condição lançam SemanticError."""
    analyzer = SemanticAnalyzer()

    with pytest.raises(SemanticError, match="Condição ausente na estrutura 'if'"):
        analyzer.visit(IfNode(condition=None, then_body=[IntLiteralNode(value=1)], line=2, column=1))

    with pytest.raises(SemanticError, match="Condição ausente na estrutura 'elif'"):
        analyzer.visit(ElifClauseNode(condition=None, body=[IntLiteralNode(value=1)], line=3, column=1))

    with pytest.raises(SemanticError, match="Condição ausente na estrutura 'while'"):
        analyzer.visit(WhileNode(condition=None, body=[IntLiteralNode(value=1)], line=5, column=1))


# ==============================================================================
# 3. Isolamento de Escopos de Bloco (Não-Vazamento de Variáveis Locais)
# ==============================================================================


def test_variable_declared_inside_if_then_is_not_visible_outside() -> None:
    """Garante que variável criada dentro do bloco 'if' não vaza para o escopo externo."""
    source = (
        "if True:\n"
        "    interna = 42\n"
        "resultado = interna + 1\n"
    )
    with pytest.raises(SemanticError, match="Variável 'interna' não declarada") as exc_info:
        analyze_source(source)

    assert exc_info.value.line == 3


def test_variable_declared_inside_elif_is_not_visible_outside() -> None:
    """Garante que variável criada dentro do bloco 'elif' não vaza para o escopo externo."""
    source = (
        "x = 10\n"
        "if x < 0:\n"
        "    a = 1\n"
        "elif x > 5:\n"
        "    local_elif = 99\n"
        "return local_elif\n"
    )
    with pytest.raises(SemanticError, match="Variável 'local_elif' não declarada") as exc_info:
        analyze_source(source)

    assert exc_info.value.line == 6


def test_variable_declared_inside_else_is_not_visible_outside() -> None:
    """Garante que variável criada dentro do bloco 'else' não vaza para o escopo externo."""
    source = (
        "if False:\n"
        "    a = 1\n"
        "else:\n"
        "    local_else = 2\n"
        "return local_else\n"
    )
    with pytest.raises(SemanticError, match="Variável 'local_else' não declarada") as exc_info:
        analyze_source(source)

    assert exc_info.value.line == 5


def test_variable_declared_inside_while_is_not_visible_outside() -> None:
    """Garante que variável criada dentro do laço 'while' não vaza para o escopo externo."""
    source = (
        "i = 0\n"
        "while i < 3:\n"
        "    temp_loop = i * 2\n"
        "    i += 1\n"
        "return temp_loop\n"
    )
    with pytest.raises(SemanticError, match="Variável 'temp_loop' não declarada") as exc_info:
        analyze_source(source)

    assert exc_info.value.line == 5


def test_sibling_blocks_if_elif_else_do_not_share_local_variables() -> None:
    """Garante que variáveis definidas no bloco 'if' não existem nos blocos irmãos 'elif' e 'else'."""
    source_elif = (
        "x = 5\n"
        "if x == 1:\n"
        "    so_no_if = 10\n"
        "elif x == 5:\n"
        "    y = so_no_if + 1\n"
    )
    with pytest.raises(SemanticError, match="Variável 'so_no_if' não declarada") as exc_elif:
        analyze_source(source_elif)
    assert exc_elif.value.line == 5

    source_else = (
        "x = 5\n"
        "if x == 1:\n"
        "    so_no_if = 10\n"
        "else:\n"
        "    y = so_no_if + 1\n"
    )
    with pytest.raises(SemanticError, match="Variável 'so_no_if' não declarada") as exc_else:
        analyze_source(source_else)
    assert exc_else.value.line == 5


def test_sibling_blocks_can_declare_same_variable_name_with_different_types() -> None:
    """Como cada bloco possui seu próprio escopo, blocos irmãos podem declarar o mesmo nome independentemente."""
    source = (
        "x = 10\n"
        "if x > 0:\n"
        "    temp = 100\n"
        "else:\n"
        '    temp = " cem "\n'
    )
    global_scope = analyze_source(source)
    assert global_scope.lookup("temp") is None
    assert global_scope.lookup("x") is not None


# ==============================================================================
# 4. Herança de Escopo Pai e Blocos Aninhados
# ==============================================================================


def test_outer_variables_are_visible_and_checked_inside_nested_blocks() -> None:
    """Verifica que variáveis externas são acessíveis em blocos aninhados e mantêm checagem de tipos."""
    source = (
        "soma = 0\n"
        "i = 1\n"
        "while i <= 10:\n"
        "    if i > 5:\n"
        "        soma += i\n"
        "    i += 1\n"
        "return soma\n"
    )
    global_scope = analyze_source(source)
    assert global_scope.lookup("soma") is not None
    assert global_scope.lookup("soma").type == "int"
    assert global_scope.lookup("i") is not None
    assert global_scope.lookup("i").type == "int"


def test_incompatible_reassignment_of_outer_variable_inside_block_raises_error() -> None:
    """Garante que atribuir tipo incompatível a uma variável externa dentro de um bloco lança SemanticError."""
    source = (
        "contador = 0\n"
        "if contador == 0:\n"
        '    contador = "invalido"\n'
    )
    with pytest.raises(
        SemanticError,
        match="Tipo incompatível na atribuição: variável 'contador' é 'int', mas recebeu 'String'",
    ) as exc_info:
        analyze_source(source)

    assert exc_info.value.line == 3
