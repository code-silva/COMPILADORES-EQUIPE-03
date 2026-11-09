"""Suíte de Testes de Integração: Pipeline Completo de Compilação e CLI (Issue #38).

Valida o driver do compilador em ``src/cli.py`` (e ``src/main.py``), cobrindo:
1. Execução sequencial das fases: ``Scanner -> Parser -> SemanticAnalyzer -> CodeGenerator``.
2. Geração de código Java completo a partir de programas Python procedurais válidos.
3. Interrupção imediata do pipeline em erros léxicos, sintáticos e semânticos com linha e coluna.
4. Interface de Linha de Comando (``argparse``, leitura de ``.py``, escrita de ``.java`` e códigos de saída).
"""

from pathlib import Path

import pytest

from src.cli import build_arg_parser, compile_file, compile_source, main
from src.lexer import LexicalError, Scanner, TokenType
from src.parser import ParserError
from src.semantic import SemanticError


# ==============================================================================
# 1. Pipeline Ponta a Ponta (compile_source) — Caminhos Felizes
# ==============================================================================


def test_scanner_scan_returns_full_token_list_ending_with_eof() -> None:
    """Verifica que Scanner.scan() retorna todos os tokens até EOF."""
    tokens = Scanner("x = 10\n").scan()
    assert [t.type for t in tokens] == [
        TokenType.IDENTIFIER,
        TokenType.OP_ASSIGN,
        TokenType.INT_LITERAL,
        TokenType.NEWLINE,
        TokenType.EOF,
    ]


def test_compile_source_empty_program_generates_java_boilerplate() -> None:
    """Verifica que código vazio ou só com comentários gera a estrutura base da classe Main."""
    java_code = compile_source("# programa vazio\n\n")
    expected = (
        "public class Main {\n"
        "    public static void main(String[] args) {\n"
        "    }\n"
        "}\n"
    )
    assert java_code == expected


def test_compile_source_declarations_and_arithmetic_expressions() -> None:
    """Testa compilação de variáveis tipadas, expressões aritméticas e reatribuições."""
    source = (
        "a = 10\n"
        "b = 20\n"
        "soma = a + b * 2\n"
        "soma += 5\n"
        "taxa = 1.5\n"
        'mensagem = "ok"\n'
        "ativo = True\n"
        "return\n"
    )
    java_code = compile_source(source)
    expected = (
        "public class Main {\n"
        "    public static void main(String[] args) {\n"
        "        int a = 10;\n"
        "        int b = 20;\n"
        "        int soma = (a + (b * 2));\n"
        "        soma += 5;\n"
        "        double taxa = 1.5;\n"
        '        String mensagem = "ok";\n'
        "        boolean ativo = true;\n"
        "        return;\n"
        "    }\n"
        "}\n"
    )
    assert java_code == expected


def test_compile_source_control_flow_if_elif_else_and_while() -> None:
    """Testa compilação completa com estruturas condicionais if/elif/else e laço while."""
    source = (
        "contador = 0\n"
        "limite = 5\n"
        "while contador < limite:\n"
        "    if contador == 0:\n"
        "        passo = 1\n"
        "        contador += passo\n"
        "    elif contador == 3:\n"
        "        contador += 2\n"
        "    else:\n"
        "        contador += 1\n"
    )
    java_code = compile_source(source)
    expected = (
        "public class Main {\n"
        "    public static void main(String[] args) {\n"
        "        int contador = 0;\n"
        "        int limite = 5;\n"
        "        while ((contador < limite)) {\n"
        "            if ((contador == 0)) {\n"
        "                int passo = 1;\n"
        "                contador += passo;\n"
        "            } else if ((contador == 3)) {\n"
        "                contador += 2;\n"
        "            } else {\n"
        "                contador += 1;\n"
        "            }\n"
        "        }\n"
        "    }\n"
        "}\n"
    )
    assert java_code == expected


# ==============================================================================
# 2. Interrupção do Pipeline em Erros Léxicos, Sintáticos e Semânticos
# ==============================================================================


@pytest.mark.parametrize(
    ("source", "expected_line", "expected_col"),
    [
        ("x = 10 @ 2\n", 1, 8),
        ('msg = "string sem fechar\n', 1, 7),
        ("a = $100\n", 1, 5),
    ],
)
def test_pipeline_stops_on_lexical_error(
    source: str, expected_line: int, expected_col: int
) -> None:
    """Garante que erros léxicos interrompem o pipeline antes do Parser."""
    with pytest.raises(LexicalError) as exc_info:
        compile_source(source)

    assert exc_info.value.line == expected_line
    assert exc_info.value.column == expected_col


@pytest.mark.parametrize(
    ("source", "expected_line"),
    [
        ("x = (10 + 20\n", 1),
        ("if x > 0\n    y = 1\n", 1),
        ("x = 10 + * 5\n", 1),
        ("x = 1\nelse:\n    y = 2\n", 2),
    ],
)
def test_pipeline_stops_on_parser_error(source: str, expected_line: int) -> None:
    """Garante que erros sintáticos interrompem o pipeline antes da Análise Semântica."""
    with pytest.raises(ParserError) as exc_info:
        compile_source(source)

    assert exc_info.value.line == expected_line


@pytest.mark.parametrize(
    ("source", "expected_line", "expected_match"),
    [
        ("y = nao_declarada + 1\n", 1, "Variável 'nao_declarada' não declarada"),
        ('x = 10\nx = "texto"\n', 2, "Tipo incompatível na atribuição"),
        ("x = 10\nif x:\n    y = 1\n", 2, "Condição inválida em 'if'"),
        (
            "if True:\n    local_if = 10\ny = local_if + 1\n",
            3,
            "Variável 'local_if' não declarada",
        ),
    ],
)
def test_pipeline_stops_on_semantic_error(
    source: str, expected_line: int, expected_match: str
) -> None:
    """Garante que erros semânticos interrompem o pipeline antes da Geração de Código."""
    with pytest.raises(SemanticError, match=expected_match) as exc_info:
        compile_source(source)

    assert exc_info.value.line == expected_line


# ==============================================================================
# 3. Interface de Linha de Comando (CLI) e Arquivos de E/S
# ==============================================================================


def test_build_arg_parser_parses_input_and_output_flags() -> None:
    """Verifica que o ArgumentParser reconhece input_file e -o/--output."""
    parser = build_arg_parser()

    args_short = parser.parse_args(["programa.py", "-o", "Saida.java"])
    assert args_short.input_file == "programa.py"
    assert args_short.output == "Saida.java"

    args_long = parser.parse_args(["programa.py", "--output", "out/Main.java"])
    assert args_long.input_file == "programa.py"
    assert args_long.output == "out/Main.java"

    args_default = parser.parse_args(["programa.py"])
    assert args_default.input_file == "programa.py"
    assert args_default.output is None


def test_cli_main_compiles_file_with_explicit_output(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Verifica execução completa via CLI com argumento -o gerando arquivo .java."""
    input_py = tmp_path / "calc.py"
    output_java = tmp_path / "out" / "Main.java"
    input_py.write_text("x = 15\ny = x * 2\n", encoding="utf-8")

    exit_code = main([str(input_py), "-o", str(output_java)])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert output_java.exists()
    assert "Arquivo Java gerado com sucesso" in captured.out

    content = output_java.read_text(encoding="utf-8")
    assert "public class Main {" in content
    assert "int x = 15;" in content
    assert "int y = (x * 2);" in content


def test_compile_file_uses_default_output_directory_when_omitted(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verifica que compile_file salva em output/<nome>.java quando output_path é omitido."""
    monkeypatch.chdir(tmp_path)
    input_py = tmp_path / "meu_script.py"
    input_py.write_text("valor = 42\n", encoding="utf-8")

    generated_path = compile_file(input_py)

    assert generated_path == Path("output/meu_script.java")
    assert generated_path.exists()
    assert "int valor = 42;" in generated_path.read_text(encoding="utf-8")


def test_cli_main_returns_1_on_missing_input_file(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Verifica que arquivo de entrada inexistente retorna código 1 e exibe erro no stderr."""
    missing = tmp_path / "nao_existe.py"

    exit_code = main([str(missing)])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "Erro de Arquivo" in captured.err
    assert "nao_existe.py" in captured.err


@pytest.mark.parametrize(
    ("bad_source", "expected_error_prefix"),
    [
        ("x = 10 @ 2\n", "Erro Léxico [Linha 1, Coluna 8]"),
        ("if True\n    x = 1\n", "Erro Sintático [Linha 1, Coluna 8]"),
        ("x = y + 1\n", "Erro Semântico [Linha 1, Coluna 5]"),
    ],
)
def test_cli_main_reports_formatted_compilation_errors_to_stderr(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    bad_source: str,
    expected_error_prefix: str,
) -> None:
    """Verifica que erros léxicos, sintáticos e semânticos na CLI retornam 1 e informam linha e coluna."""
    input_py = tmp_path / "invalido.py"
    output_java = tmp_path / "Main.java"
    input_py.write_text(bad_source, encoding="utf-8")

    exit_code = main([str(input_py), "-o", str(output_java)])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert expected_error_prefix in captured.err
    assert not output_java.exists()
