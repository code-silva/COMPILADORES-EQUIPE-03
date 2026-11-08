"""Testes unitários do Gerador de Código base (Issue #34)."""

import pytest

from src.codegen import CodeGenerator
from src.parser.nodes import ProgramNode


def test_codegen_importable_from_package() -> None:
    """Verifica que CodeGenerator é exportado corretamente pelo pacote src.codegen."""
    from src.codegen import CodeGenerator as CG  # noqa: PLC0415

    assert CG is CodeGenerator


def test_codegen_initial_state() -> None:
    """Verifica o estado inicial do CodeGenerator após instanciação."""
    gen = CodeGenerator()

    assert gen.indent_level == 0
    assert gen.code_lines == []


def test_generate_empty_program_returns_string() -> None:
    """Verifica que generate() retorna uma string para um ProgramNode vazio."""
    gen = CodeGenerator()
    result = gen.generate(ProgramNode())

    assert isinstance(result, str)
    assert len(result) > 0


def test_generate_empty_program_contains_class_main() -> None:
    """Verifica que o código gerado contém 'public class Main'."""
    gen = CodeGenerator()
    result = gen.generate(ProgramNode())

    assert "public class Main" in result


def test_generate_empty_program_contains_main_method() -> None:
    """Verifica que o código gerado contém a assinatura do método main."""
    gen = CodeGenerator()
    result = gen.generate(ProgramNode())

    assert "public static void main(String[] args)" in result


def test_generate_empty_program_has_opening_braces() -> None:
    """Verifica que o código gerado possui chaves de abertura para classe e método."""
    gen = CodeGenerator()
    result = gen.generate(ProgramNode())

    # Deve haver pelo menos duas chaves abertas: uma para a classe, outra para o método
    assert result.count("{") >= 2


def test_generate_empty_program_has_closing_braces() -> None:
    """Verifica que o código gerado possui chaves de fechamento para classe e método."""
    gen = CodeGenerator()
    result = gen.generate(ProgramNode())

    # Deve haver pelo menos duas chaves fechadas: uma para o método, outra para a classe
    assert result.count("}") >= 2


def test_generate_empty_program_balanced_braces() -> None:
    """Verifica que as chaves abertas e fechadas estão balanceadas."""
    gen = CodeGenerator()
    result = gen.generate(ProgramNode())

    assert result.count("{") == result.count("}")


def test_generate_empty_program_ends_with_newline() -> None:
    """Verifica que o código gerado termina com uma quebra de linha."""
    gen = CodeGenerator()
    result = gen.generate(ProgramNode())

    assert result.endswith("\n")


def test_generate_class_declaration_at_zero_indent() -> None:
    """Verifica que 'public class Main {' está sem indentação (nível 0)."""
    gen = CodeGenerator()
    lines = gen.generate(ProgramNode()).splitlines()

    assert lines[0] == "public class Main {"


def test_generate_main_method_at_one_indent() -> None:
    """Verifica que a assinatura do método main está indentada com 4 espaços."""
    gen = CodeGenerator()
    lines = gen.generate(ProgramNode()).splitlines()

    assert lines[1] == "    public static void main(String[] args) {"


def test_generate_method_closing_brace_at_one_indent() -> None:
    """Verifica que a chave de fechamento do método main está indentada com 4 espaços."""
    gen = CodeGenerator()
    lines = gen.generate(ProgramNode()).splitlines()

    # Penúltima linha não vazia deve ser '    }'
    non_empty = [line for line in lines if line.strip()]
    assert non_empty[-2] == "    }"


def test_generate_class_closing_brace_at_zero_indent() -> None:
    """Verifica que a chave de fechamento da classe está sem indentação."""
    gen = CodeGenerator()
    lines = gen.generate(ProgramNode()).splitlines()

    non_empty = [line for line in lines if line.strip()]
    assert non_empty[-1] == "}"


def test_generate_indent_size_is_four_spaces() -> None:
    """Verifica que o INDENT_SIZE padrão do CodeGenerator é 4."""
    assert CodeGenerator.INDENT_SIZE == 4

def test_generate_resets_state_on_each_call() -> None:
    """Verifica que chamadas consecutivas a generate() não acumulam linhas."""
    gen = CodeGenerator()
    result1 = gen.generate(ProgramNode())
    result2 = gen.generate(ProgramNode())

    assert result1 == result2


def test_generate_indent_level_returns_to_zero_after_generation() -> None:
    """Verifica que indent_level volta a 0 após a geração completa."""
    gen = CodeGenerator()
    gen.generate(ProgramNode())

    assert gen.indent_level == 0

def test_emit_adds_line_with_current_indent() -> None:
    """Verifica que emit() prefixa a linha com a indentação correta."""
    gen = CodeGenerator()
    gen.emit("int x = 0;")

    assert gen.code_lines == ["int x = 0;"]


def test_emit_with_indent_level_one() -> None:
    """Verifica que emit() usa 4 espaços com indent_level=1."""
    gen = CodeGenerator()
    gen.indent()
    gen.emit("int x = 0;")

    assert gen.code_lines == ["    int x = 0;"]


def test_emit_with_indent_level_two() -> None:
    """Verifica que emit() usa 8 espaços com indent_level=2."""
    gen = CodeGenerator()
    gen.indent()
    gen.indent()
    gen.emit("x++;")

    assert gen.code_lines == ["        x++;"]


def test_indent_increments_level() -> None:
    """Verifica que indent() incrementa indent_level."""
    gen = CodeGenerator()
    gen.indent()

    assert gen.indent_level == 1


def test_dedent_decrements_level() -> None:
    """Verifica que dedent() decrementa indent_level."""
    gen = CodeGenerator()
    gen.indent()
    gen.dedent()

    assert gen.indent_level == 0


def test_dedent_at_zero_raises_value_error() -> None:
    """Verifica que dedent() levanta ValueError quando indent_level já é 0."""
    gen = CodeGenerator()

    with pytest.raises(ValueError):
        gen.dedent()


def test_get_code_joins_lines_with_newline() -> None:
    """Verifica que get_code() une as linhas com \\n e adiciona newline final."""
    gen = CodeGenerator()
    gen.code_lines = ["linha 1", "linha 2", "linha 3"]

    result = gen.get_code()

    assert result == "linha 1\nlinha 2\nlinha 3\n"


def test_get_code_empty_lines_returns_newline() -> None:
    """Verifica que get_code() com lista vazia retorna apenas \\n."""
    gen = CodeGenerator()

    assert gen.get_code() == "\n"