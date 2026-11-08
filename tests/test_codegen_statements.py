"""Testes unitários da geração de código Java para instruções (Issue #36).

Valida o mapeamento de ``AssignNode`` (declaração tipada na primeira
atribuição, reatribuição e atribuições acumulativas ``+=``/``-=``) e de
``ReturnNode`` (``return expr;`` e ``return;``) no ``CodeGenerator``.
"""

import pytest

from src.codegen import CodeGenerator
from src.parser import (
    AssignNode,
    BinOpNode,
    BoolLiteralNode,
    FloatLiteralNode,
    IdentifierNode,
    IntLiteralNode,
    NoneLiteralNode,
    Parser,
    ProgramNode,
    ReturnNode,
    StringLiteralNode,
)
from src.semantic import SemanticError


def gen_lines(*stmts) -> list[str]:
    """Gera as instruções com um CodeGenerator novo e devolve as linhas emitidas."""
    gen = CodeGenerator()
    for stmt in stmts:
        gen.visit(stmt)
    return gen.code_lines


def main_body(source: str) -> list[str]:
    """Compila ``source`` e devolve as linhas do corpo da main, sem indentação."""
    code = CodeGenerator().generate(Parser(source).parse())
    lines = code.splitlines()
    return [line.strip() for line in lines[2:-2]]


# ==============================================================================
# 1. Primeira atribuição: declaração tipada
# ==============================================================================


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (IntLiteralNode(value=10), "int x = 10;"),
        (FloatLiteralNode(value=2.5), "double x = 2.5;"),
        (StringLiteralNode(value="oi"), 'String x = "oi";'),
        (BoolLiteralNode(value=True), "boolean x = true;"),
        (NoneLiteralNode(), "Object x = null;"),
    ],
)
def test_primeira_atribuicao_declara_tipo_java(value, expected) -> None:
    """A primeira atribuição emite a declaração com o tipo Java do valor."""
    assert gen_lines(AssignNode(target="x", op="=", value=value)) == [expected]


def test_declaracao_com_expressao_infere_tipo() -> None:
    """O tipo da declaração vem da expressão inteira (int * float -> double)."""
    lines = gen_lines(
        AssignNode(target="a", op="=", value=IntLiteralNode(value=2)),
        AssignNode(
            target="b",
            op="=",
            value=BinOpNode(
                left=IdentifierNode(name="a"),
                op="*",
                right=FloatLiteralNode(value=1.5),
            ),
        ),
    )
    assert lines == ["int a = 2;", "double b = (a * 1.5);"]


def test_declaracao_de_comparacao_gera_boolean() -> None:
    """Comparações geram variáveis ``boolean``."""
    assert main_body("n = 7\naprovado = n >= 5\n") == [
        "int n = 7;",
        "boolean aprovado = (n >= 5);",
    ]


def test_declaracao_de_concatenacao_gera_string() -> None:
    """Concatenação de Strings gera variável ``String``."""
    assert main_body('a = "x"\nb = a + "y"\n') == ['String a = "x";', 'String b = (a + "y");']


def test_variavel_e_registrada_em_declared_vars() -> None:
    """Após a declaração o nome passa a constar em ``declared_vars``."""
    gen = CodeGenerator()
    assert gen.declared_vars == set()
    gen.visit(AssignNode(target="x", op="=", value=IntLiteralNode(value=1)))
    assert gen.declared_vars == {"x"}


# ==============================================================================
# 2. Reatribuições e atribuições acumulativas
# ==============================================================================


def test_reatribuicao_nao_repete_declaracao() -> None:
    """A segunda atribuição da mesma variável não repete o tipo."""
    assert main_body("x = 10\nx = 20\n") == ["int x = 10;", "x = 20;"]


@pytest.mark.parametrize("op", ["+=", "-="])
def test_atribuicao_acumulativa(op: str) -> None:
    """``+=`` e ``-=`` são emitidos como em Java depois da declaração."""
    assert main_body(f"x = 10\nx {op} 5\n") == ["int x = 10;", f"x {op} 5;"]


def test_sequencia_de_atribuicoes() -> None:
    """Declarações e atribuições se misturam na ordem do programa."""
    source = "total = 0\ncont = 1\ntotal += cont\ncont = cont + 1\ntotal -= 2\n"
    assert main_body(source) == [
        "int total = 0;",
        "int cont = 1;",
        "total += cont;",
        "cont = (cont + 1);",
        "total -= 2;",
    ]


def test_float_aceita_reatribuicao_com_int() -> None:
    """Variável ``double`` aceita receber um ``int`` (promoção válida em Java)."""
    assert main_body("media = 1.5\nmedia = 2\n") == ["double media = 1.5;", "media = 2;"]


def test_acumulativa_em_variavel_nao_declarada_falha() -> None:
    """``x += 1`` sem declaração prévia não tem tradução válida em Java."""
    with pytest.raises(ValueError, match="não declarada"):
        gen_lines(AssignNode(target="x", op="+=", value=IntLiteralNode(value=1)))


def test_reatribuicao_com_tipo_incompativel_falha() -> None:
    """Trocar o tipo de uma variável já declarada é erro semântico."""
    with pytest.raises(SemanticError):
        main_body('x = 1\nx = "texto"\n')


def test_uso_de_variavel_indefinida_falha() -> None:
    """O valor não pode usar identificador ainda não declarado."""
    with pytest.raises(SemanticError):
        main_body("x = y + 1\n")


@pytest.mark.parametrize(
    "node",
    [
        AssignNode(target="", op="=", value=IntLiteralNode(value=1)),
        AssignNode(target="x", op="=", value=None),
        AssignNode(target="x", op="*=", value=IntLiteralNode(value=1)),
    ],
)
def test_assign_invalido_levanta_erro(node: AssignNode) -> None:
    """Nós de atribuição incompletos ou com operador inválido são rejeitados."""
    with pytest.raises(ValueError):
        gen_lines(node)


def test_generate_reinicia_variaveis_declaradas() -> None:
    """Chamadas consecutivas de ``generate`` declaram as variáveis de novo."""
    gen = CodeGenerator()
    program = Parser("x = 1\n").parse()
    first = gen.generate(program)
    second = gen.generate(program)
    assert first == second
    assert "int x = 1;" in second


# ==============================================================================
# 3. Retorno
# ==============================================================================


def test_return_com_expressao() -> None:
    """``ReturnNode`` com valor gera ``return expr;``."""
    node = ReturnNode(
        value=BinOpNode(left=IntLiteralNode(value=1), op="+", right=IntLiteralNode(value=2))
    )
    assert gen_lines(node) == ["return (1 + 2);"]


def test_return_sem_expressao() -> None:
    """``ReturnNode`` sem valor gera ``return;``."""
    assert gen_lines(ReturnNode()) == ["return;"]


def test_return_de_variavel_do_programa() -> None:
    """O retorno usa variáveis declaradas antes."""
    assert main_body("x = 3\nreturn x\n") == ["int x = 3;", "return x;"]


# ==============================================================================
# 4. Programa completo
# ==============================================================================


def test_programa_completo_indentado() -> None:
    """As instruções ficam dentro da main, com 8 espaços de indentação."""
    code = CodeGenerator().generate(Parser("x = 10\nx += 5\n").parse())
    assert code == (
        "public class Main {\n"
        "    public static void main(String[] args) {\n"
        "        int x = 10;\n"
        "        x += 5;\n"
        "    }\n"
        "}\n"
    )


def test_programa_vazio_continua_igual() -> None:
    """Sem instruções o boilerplate não muda."""
    code = CodeGenerator().generate(ProgramNode())
    assert code == (
        "public class Main {\n"
        "    public static void main(String[] args) {\n"
        "    }\n"
        "}\n"
    )


def test_instrucao_nao_suportada_levanta_erro() -> None:
    """Nós sem gerador de instrução são rejeitados com ValueError."""
    with pytest.raises(ValueError, match="não suportada"):
        gen_lines(IntLiteralNode(value=1))
