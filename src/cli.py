"""Interface de Linha de Comando (CLI) e Driver do pipeline do compilador PyToJava."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
from typing import Sequence

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.codegen import CodeGenerator
from src.lexer import LexicalError, Scanner
from src.parser import Parser, ParserError
from src.semantic import SemanticAnalyzer, SemanticError


def compile_source(source_code: str) -> str:
    """Executa o pipeline completo de compilação (Lexer -> Parser -> Semântico -> Codegen).

    Args:
        source_code: Código-fonte no subconjunto procedural de Python.

    Returns:
        Código-fonte Java equivalente e formatado.

    Raises:
        LexicalError: Se houver token ou caractere inválido na análise léxica.
        ParserError: Se houver violação gramatical na análise sintática.
        SemanticError: Se houver erro de escopo ou incompatibilidade de tipos.
    """
    tokens = Scanner(source_code).scan()
    ast = Parser(tokens).parse()
    SemanticAnalyzer().analyze(ast)
    java_code = CodeGenerator().generate(ast)
    return java_code


def compile_file(
    input_path: str | Path,
    output_path: str | Path | None = None,
) -> Path:
    """Lê um arquivo ``.py``, compila para Java e grava o arquivo ``.java`` de saída.

    Args:
        input_path: Caminho do arquivo Python de entrada.
        output_path: Caminho opcional do arquivo Java de destino. Quando omitido,
            utiliza ``output/<nome_do_arquivo>.java``.

    Returns:
        Objeto ``Path`` apontando para o arquivo ``.java`` gerado.
    """
    in_path = Path(input_path)
    source_code = in_path.read_text(encoding="utf-8")
    java_code = compile_source(source_code)

    out_path = (
        Path(output_path)
        if output_path is not None
        else Path("output") / f"{in_path.stem}.java"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(java_code, encoding="utf-8")
    return out_path


def build_arg_parser() -> argparse.ArgumentParser:
    """Constrói e retorna o gerenciador de argumentos de linha de comando (``argparse``)."""
    parser = argparse.ArgumentParser(
        prog="pytojava",
        description="Compilador/transpilador de um subconjunto procedural de Python para Java.",
    )
    parser.add_argument(
        "input_file",
        help="Caminho para o arquivo-fonte Python (.py) de entrada.",
    )
    parser.add_argument(
        "-o",
        "--output",
        dest="output",
        default=None,
        help="Caminho para o arquivo Java (.java) de saída (padrão: output/<nome>.java).",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Ponto de entrada principal da CLI do compilador PyToJava.

    Args:
        argv: Lista de argumentos de linha de comando (usa ``sys.argv[1:]`` por padrão).

    Returns:
        Código de saída do processo (``0`` em caso de sucesso, ``1`` em erro de compilação/E/S).
    """
    arg_parser = build_arg_parser()
    args = arg_parser.parse_args(argv)

    try:
        output_path = compile_file(args.input_file, args.output)
    except FileNotFoundError:
        print(
            f"Erro de Arquivo: arquivo de entrada não encontrado: '{args.input_file}'",
            file=sys.stderr,
        )
        return 1
    except (LexicalError, ParserError, SemanticError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    except (OSError, ValueError) as exc:
        print(f"Erro de Compilação: {exc}", file=sys.stderr)
        return 1

    print(f"Arquivo Java gerado com sucesso em: {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
