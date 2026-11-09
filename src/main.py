"""Ponto de entrada (CLI) do compilador PyToJava."""

from __future__ import annotations

from pathlib import Path
import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.cli import build_arg_parser, compile_file, compile_source, main

__all__ = [
    "build_arg_parser",
    "compile_file",
    "compile_source",
    "main",
]


if __name__ == "__main__":
    sys.exit(main())
