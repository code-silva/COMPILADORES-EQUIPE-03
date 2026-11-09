"""Testes de integração End-to-End (E2E), casos de borda, exemplos e validação real com javac (Issue #39)."""

from __future__ import annotations

from pathlib import Path
import re
import shutil
import subprocess

import pytest

from src.cli import compile_file, compile_source, main
from src.lexer import LexicalError
from src.parser import ParserError
from src.semantic import SemanticError

PROJECT_ROOT = Path(__file__).resolve().parent.parent
EXAMPLES_DIR = PROJECT_ROOT / "examples"
DOCS_DIR = PROJECT_ROOT / "docs"
MKDOCS_CONFIG = PROJECT_ROOT / "mkdocs.yml"

REQUIRED_EXAMPLES = (
    "hello.py",
    "factorial.py",
    "calculator.py",
    "basic_math.py",
    "control_flow.py",
)


# ==============================================================================
# Fixtures e Helpers de Compilação Java (javac / java)
# ==============================================================================


@pytest.fixture(scope="module")
def javac_bin() -> str:
    """Retorna o caminho do executável ``javac`` ou pula o teste se indisponível."""
    executable = shutil.which("javac")
    if executable is None:
        pytest.skip("Executável 'javac' não encontrado no PATH do ambiente de execução.")
    try:
        probe = subprocess.run(
            [executable, "-version"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        pytest.skip("Executável 'javac' inacessível ou bloqueado pelo ambiente atual.")
    if probe.returncode != 0:
        pytest.skip("Executável 'javac' retornou código de erro ao verificar versão.")
    return executable


@pytest.fixture(scope="module")
def java_bin() -> str:
    """Retorna o caminho do executável ``java`` ou pula o teste se indisponível."""
    executable = shutil.which("java")
    if executable is None:
        pytest.skip("Executável 'java' não encontrado no PATH do ambiente de execução.")
    return executable


def compile_with_javac(java_code: str, work_dir: Path, javac_executable: str) -> Path:
    """Salva o código Java em ``Main.java``, invoca ``javac`` e valida código de retorno 0."""
    work_dir.mkdir(parents=True, exist_ok=True)
    java_file = work_dir / "Main.java"
    java_file.write_text(java_code, encoding="utf-8")

    result = subprocess.run(
        [javac_executable, str(java_file)],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    assert result.returncode == 0, (
        f"Falha ao compilar Main.java com javac (returncode={result.returncode}):\n"
        f"STDERR:\n{result.stderr}\n"
        f"CÓDIGO JAVA:\n{java_code}"
    )

    class_file = work_dir / "Main.class"
    assert class_file.is_file(), "O arquivo bytecode Main.class não foi gerado pelo javac."
    return class_file


# ==============================================================================
# 1. Validação Real com javac (End-to-End)
# ==============================================================================


def test_e2e_javac_complex_procedural_program(
    tmp_path: Path, javac_bin: str, java_bin: str
) -> None:
    """Compila um script Python complexo e valida sintaxe/tipagem com ``javac`` e execução na JVM."""
    source_code = (
        "# Programa procedural completo: variaveis, expressoes, if/elif/else, while e return\n"
        "limite = 8\n"
        "contador = 1\n"
        "acumulador = 0\n"
        "fator = 1.5\n"
        "media_ponderada = 0.0\n"
        'rotulo = "Calculo: "\n'
        "ativo = True\n"
        "nulo = None\n"
        "\n"
        "while contador <= limite:\n"
        "    if contador == 1:\n"
        "        passo_inicial = 10\n"
        "        acumulador += passo_inicial\n"
        "    elif contador <= 4:\n"
        "        acumulador = acumulador + contador * 2\n"
        "    else:\n"
        "        acumulador -= 1\n"
        "    contador += 1\n"
        "\n"
        "media_ponderada = (acumulador * fator) / 2.0\n"
        "\n"
        "if media_ponderada >= 10.0:\n"
        '    status = rotulo + "APROVADO"\n'
        "elif media_ponderada >= 5.0:\n"
        '    status = rotulo + "RECUPERACAO"\n'
        "else:\n"
        '    status = rotulo + "REPROVADO"\n'
        "    return\n"
    )

    java_code = compile_source(source_code)
    compile_with_javac(java_code, tmp_path, javac_bin)

    run_result = subprocess.run(
        [java_bin, "-cp", str(tmp_path), "Main"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert run_result.returncode == 0, f"Erro ao executar Main.class: {run_result.stderr}"


@pytest.mark.parametrize("example_name", REQUIRED_EXAMPLES)
def test_e2e_javac_compiles_all_example_scripts(
    example_name: str, tmp_path: Path, javac_bin: str
) -> None:
    """Todos os scripts em ``examples/`` devem compilar via CLI e gerar bytecode válido no ``javac``."""
    example_path = EXAMPLES_DIR / example_name
    assert example_path.is_file(), f"Arquivo de exemplo ausente: {example_path}"

    target_dir = tmp_path / example_path.stem
    target_dir.mkdir(parents=True, exist_ok=True)
    java_output = target_dir / "Main.java"

    exit_code = main([str(example_path), "-o", str(java_output)])
    assert exit_code == 0
    assert java_output.is_file()

    result = subprocess.run(
        [javac_bin, str(java_output)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, (
        f"O exemplo {example_name} gerou Java inválido para o javac:\n{result.stderr}"
    )
    assert (target_dir / "Main.class").is_file()


def test_e2e_javac_edge_cases_escapes_and_scoping(
    tmp_path: Path, javac_bin: str
) -> None:
    """Valida casos de borda no ``javac``: escapes em strings, coerção int->double e escopos irmãos."""
    source_code = (
        'texto = "Linha 1\\nLinha 2 com \\"aspas\\" e \\\\barra\\\\"\n'
        "taxa = 2.5\n"
        "taxa = 10\n"
        "flag = True\n"
        "if flag == True:\n"
        "    temporaria = 42\n"
        "else:\n"
        '    temporaria = "mesmo nome em outro bloco com outro tipo"\n'
    )

    java_code = compile_source(source_code)
    compile_with_javac(java_code, tmp_path, javac_bin)


def test_e2e_javac_empty_and_comment_only_program(
    tmp_path: Path, javac_bin: str
) -> None:
    """Programa contendo apenas comentários e linhas em branco gera classe ``Main`` compilável."""
    source_code = "# Apenas comentario\n\n   # Outro comentario\n"
    java_code = compile_source(source_code)
    compile_with_javac(java_code, tmp_path, javac_bin)


# ==============================================================================
# 2. Testes E2E dos Scripts em examples/ e Casos de Borda do Pipeline
# ==============================================================================


@pytest.mark.parametrize("example_name", REQUIRED_EXAMPLES)
def test_examples_directory_scripts_compile_and_have_balanced_structure(
    example_name: str, tmp_path: Path
) -> None:
    """Verifica que cada script de ``examples/`` é compilado sem erros e gera Java bem-formado."""
    example_path = EXAMPLES_DIR / example_name
    assert example_path.is_file(), f"Script obrigatório não encontrado: {example_path}"

    out_path = compile_file(example_path, tmp_path / f"{example_path.stem}.java")
    java_code = out_path.read_text(encoding="utf-8")

    assert java_code.startswith("public class Main {\n")
    assert "public static void main(String[] args) {" in java_code
    assert java_code.count("{") == java_code.count("}")
    assert java_code.endswith("}\n")


def test_e2e_deeply_nested_control_flow_and_precedence() -> None:
    """Valida aninhamento profundo de ``while`` e ``if/elif/else`` com expressões complexas."""
    source = (
        "a = 2\n"
        "b = 3\n"
        "c = 4\n"
        "resultado = a + b * c - (a + b) * c\n"
        "iteracao = 0\n"
        "while iteracao < 5:\n"
        "    if resultado < 0:\n"
        "        if iteracao == 0:\n"
        "            resultado += 10\n"
        "        elif iteracao == 1:\n"
        "            resultado += 5\n"
        "        else:\n"
        "            resultado += 1\n"
        "    else:\n"
        "        resultado -= 2\n"
        "    iteracao += 1\n"
    )
    java_code = compile_source(source)

    assert "int resultado = ((a + (b * c)) - ((a + b) * c));" in java_code
    assert "while ((iteracao < 5)) {" in java_code
    assert "} else if ((iteracao == 1)) {" in java_code
    assert java_code.count("{") == java_code.count("}")


@pytest.mark.parametrize(
    ("invalid_source", "expected_exception", "expected_line"),
    [
        ("x = 10\ny = $ + 1\n", LexicalError, 2),
        ('msg = "string sem fechar\n', LexicalError, 1),
        ("if True:\n    x = 1\n  y = 2\n", ParserError, 3),
        ("if x == 1\n    y = 2\n", ParserError, 1),
        ("    x = 10\n", ParserError, 1),
        ("x = nao_declarada + 1\n", SemanticError, 1),
        ('x = 10\nx = "incompativel"\n', SemanticError, 2),
        ("x = 10\nif x:\n    x = 20\n", SemanticError, 2),
        ("if True:\n    interna = 5\nfora = interna + 1\n", SemanticError, 3),
    ],
)
def test_e2e_pipeline_rejects_invalid_programs_with_exact_line(
    invalid_source: str,
    expected_exception: type[Exception],
    expected_line: int,
) -> None:
    """Garante que violações léxicas, sintáticas e semânticas interrompem o pipeline na linha correta."""
    with pytest.raises(expected_exception) as exc_info:
        compile_source(invalid_source)

    assert getattr(exc_info.value, "line", None) == expected_line


# ==============================================================================
# 3. Integridade da Documentação e do mkdocs.yml
# ==============================================================================


def test_mkdocs_nav_files_exist_and_cover_all_compiler_phases() -> None:
    """Valida que todos os arquivos referenciados em ``mkdocs.yml`` existem em ``docs/``."""
    assert MKDOCS_CONFIG.is_file(), "Arquivo mkdocs.yml não encontrado na raiz."
    config_text = MKDOCS_CONFIG.read_text(encoding="utf-8")

    # Extrai todos os caminhos .md declarados na seção nav do mkdocs.yml
    nav_section = config_text.split("nav:", maxsplit=1)[1]
    md_paths = re.findall(r":\s*([a-zA-Z0-9_./-]+\.md)", nav_section)

    expected_specs = {
        "index.md",
        "GLOSSARY.md",
        "estrutura.md",
        "compiladores.md",
        "specs/lexico.md",
        "arch/scanner.md",
        "parser/index.md",
        "parser/ast.md",
        "parser/grammar.md",
        "parser/errors.md",
        "semantic/symbol_table.md",
        "semantic/analyzer.md",
        "semantic/types.md",
        "codegen/architecture.md",
        "codegen/expressions.md",
        "codegen/control_flow.md",
        "usage.md",
    }
    assert expected_specs.issubset(set(md_paths)), (
        f"Especificações ausentes no nav do mkdocs.yml: {expected_specs - set(md_paths)}"
    )

    for rel_path in md_paths:
        target = DOCS_DIR / rel_path
        assert target.is_file(), f"Arquivo referenciado no mkdocs.yml não existe: {target}"


def test_documentation_has_no_emojis() -> None:
    """Garante que os arquivos de documentação do projeto não contenham emojis."""
    emoji_pattern = re.compile(r"[\U00010000-\U0010ffff\u2600-\u27bf\u2b50]")
    md_files = [
        PROJECT_ROOT / "README.md",
        PROJECT_ROOT / "CONTRIBUTING.md",
        *DOCS_DIR.rglob("*.md"),
    ]

    files_with_emojis: list[str] = []
    for md_file in md_files:
        content = md_file.read_text(encoding="utf-8")
        matches = emoji_pattern.findall(content)
        if matches:
            rel = md_file.relative_to(PROJECT_ROOT)
            files_with_emojis.append(f"{rel}: {matches}")

    assert not files_with_emojis, (
        "Foram encontrados emojis nos seguintes arquivos de documentação:\n"
        + "\n".join(files_with_emojis)
    )

