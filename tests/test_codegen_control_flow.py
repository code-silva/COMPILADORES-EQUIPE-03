"""Testes unitários da geração de código Java para estruturas de controle (Issue #37).

Valida a tradução de ``IfNode`` (incluindo ``ElifClauseNode`` e ``ElseClauseNode``)
e ``WhileNode`` para blocos Java equivalentes (``if (...) { ... } else if (...) { ... } else { ... }``
e ``while (...) { ... }``), verificando a indentação de 4 espaços, o alinhamento de
chaves ``{}`` e o gerenciamento de escopos de variáveis declaradas em cada bloco.
"""

import pytest

from src.codegen import CodeGenerator
from src.parser import (
    AssignNode,
    BoolLiteralNode,
    ElifClauseNode,
    ElseClauseNode,
    IfNode,
    IntLiteralNode,
    Parser,
    WhileNode,
)
from src.semantic import SemanticError


def compile_to_java(source: str) -> str:
    """Compila código-fonte Python em código Java completo via Parser + CodeGenerator."""
    program = Parser(source).parse()
    return CodeGenerator().generate(program)


def main_body_lines(source: str) -> list[str]:
    """Retorna as linhas internas ao método main (mantendo indentação relativa à main)."""
    full_code = compile_to_java(source)
    lines = full_code.splitlines()
    # Remove as 2 primeiras linhas (class Main e main) e as 2 últimas (fechamentos)
    # e remove os 8 espaços base do nível do corpo da main.
    return [line[8:] if line.startswith("        ") else line for line in lines[2:-2]]


# ==============================================================================
# 1. Estruturas Condicionais (if / elif / else)
# ==============================================================================


def test_simple_if_statement_generates_java_if_block() -> None:
    """Verifica tradução de um bloco 'if' simples sem elif/else."""
    source = (
        "x = 10\n"
        "if x > 5:\n"
        "    x = 20\n"
    )
    assert main_body_lines(source) == [
        "int x = 10;",
        "if ((x > 5)) {",
        "    x = 20;",
        "}",
    ]


def test_if_else_statement_generates_java_if_else() -> None:
    """Verifica tradução de 'if / else' com alinhamento de chaves '} else {'."""
    source = (
        "ativo = True\n"
        "resultado = 0\n"
        "if ativo:\n"
        "    resultado = 1\n"
        "else:\n"
        "    resultado = 2\n"
    )
    assert main_body_lines(source) == [
        "boolean ativo = true;",
        "int resultado = 0;",
        "if (ativo) {",
        "    resultado = 1;",
        "} else {",
        "    resultado = 2;",
        "}",
    ]


def test_if_elif_else_chain_generates_else_if_blocks() -> None:
    """Verifica encadeamento de múltiplos 'elif' seguidos de 'else'."""
    source = (
        "nota = 8\n"
        'conceito = ""\n'
        "if nota >= 9:\n"
        '    conceito = "A"\n'
        "elif nota >= 7:\n"
        '    conceito = "B"\n'
        "elif nota >= 5:\n"
        '    conceito = "C"\n'
        "else:\n"
        '    conceito = "D"\n'
    )
    assert main_body_lines(source) == [
        "int nota = 8;",
        'String conceito = "";',
        "if ((nota >= 9)) {",
        '    conceito = "A";',
        "} else if ((nota >= 7)) {",
        '    conceito = "B";',
        "} else if ((nota >= 5)) {",
        '    conceito = "C";',
        "} else {",
        '    conceito = "D";',
        "}",
    ]


def test_if_node_with_explicit_else_clause_node() -> None:
    """Verifica suporte direto a ElseClauseNode quando instanciado na AST."""
    gen = CodeGenerator()
    if_node = IfNode(
        condition=BoolLiteralNode(value=True),
        then_body=[AssignNode(target="a", op="=", value=IntLiteralNode(value=1))],
        elif_clauses=[],
        else_body=[
            ElseClauseNode(
                body=[AssignNode(target="b", op="=", value=IntLiteralNode(value=2))]
            )
        ],
    )
    gen.visit(if_node)
    assert gen.code_lines == [
        "if (true) {",
        "    int a = 1;",
        "} else {",
        "    int b = 2;",
        "}",
    ]


# ==============================================================================
# 2. Laços de Repetição (while)
# ==============================================================================


def test_while_loop_with_internal_statements() -> None:
    """Verifica tradução de laço 'while' com múltiplas instruções internas."""
    source = (
        "n = 5\n"
        "fatorial = 1\n"
        "while n > 1:\n"
        "    fatorial = fatorial * n\n"
        "    n -= 1\n"
    )
    assert main_body_lines(source) == [
        "int n = 5;",
        "int fatorial = 1;",
        "while ((n > 1)) {",
        "    fatorial = (fatorial * n);",
        "    n -= 1;",
        "}",
    ]


# ==============================================================================
# 3. Estruturas Aninhadas, Formatação de Chaves e Escopos de Bloco
# ==============================================================================


def test_nested_while_and_if_else_indentation_and_braces() -> None:
    """Verifica indentação de múltiplos níveis e balanceamento de chaves em blocos aninhados."""
    source = (
        "i = 0\n"
        "menores = 0\n"
        "while i < 10:\n"
        "    if i < 5:\n"
        "        menores += 1\n"
        "    else:\n"
        "        if i == 7:\n"
        "            return\n"
        "    i += 1\n"
    )
    java_code = compile_to_java(source)

    expected_java = (
        "public class Main {\n"
        "    public static void main(String[] args) {\n"
        "        int i = 0;\n"
        "        int menores = 0;\n"
        "        while ((i < 10)) {\n"
        "            if ((i < 5)) {\n"
        "                menores += 1;\n"
        "            } else {\n"
        "                if ((i == 7)) {\n"
        "                    return;\n"
        "                }\n"
        "            }\n"
        "            i += 1;\n"
        "        }\n"
        "    }\n"
        "}\n"
    )
    assert java_code == expected_java
    assert java_code.count("{") == java_code.count("}")


def test_sibling_blocks_declare_independent_local_variables_in_java() -> None:
    """Garante que variáveis locais criadas em blocos irmãos recebem declaração tipada em cada bloco."""
    source = (
        "x = 10\n"
        "if x > 0:\n"
        "    temp = 1\n"
        "else:\n"
        "    temp = 2\n"
    )
    assert main_body_lines(source) == [
        "int x = 10;",
        "if ((x > 0)) {",
        "    int temp = 1;",
        "} else {",
        "    int temp = 2;",
        "}",
    ]


# ==============================================================================
# 4. Validações Defensivas e Semânticas
# ==============================================================================


def test_non_boolean_condition_in_if_or_while_raises_semantic_error() -> None:
    """Garante que condições não booleanas em if/while disparam SemanticError na geração."""
    with pytest.raises(SemanticError, match="Condição inválida em 'if'"):
        compile_to_java("if 10:\n    x = 1\n")

    with pytest.raises(SemanticError, match="Condição inválida em 'while'"):
        compile_to_java("while 10:\n    x = 1\n")


def test_missing_condition_in_control_flow_nodes_raises_value_error() -> None:
    """Garante ValueError se IfNode, ElifClauseNode ou WhileNode estiverem sem condição."""
    gen = CodeGenerator()

    with pytest.raises(ValueError, match="IfNode requer uma condição"):
        gen.visit(IfNode(condition=None, then_body=[]))

    with pytest.raises(ValueError, match="ElifClauseNode requer uma condição"):
        gen.visit(ElifClauseNode(condition=None, body=[]))

    with pytest.raises(ValueError, match="WhileNode requer uma condição"):
        gen.visit(WhileNode(condition=None, body=[]))
