"""
tests/test_lexer.py

Testes unitarios basicos do lexer. Rodem com:
    pytest tests/test_lexer.py -v
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "lexer"))
from lexer import tokenize  # noqa: E402


def types_of(tokens):
    """Extrai so a sequencia de tipos, ignorando NEWLINE/ENDMARKER pra facilitar leitura."""
    return [t.type for t in tokens]


def test_atribuicao_simples():
    tokens = tokenize("x = 10\n")
    assert types_of(tokens) == ["NAME", "OP", "NUMBER", "NEWLINE", "ENDMARKER"]


def test_operadores_aritmeticos():
    tokens = tokenize("y = a + b * 2\n")
    valores = [t.value for t in tokens if t.type not in ("NEWLINE", "ENDMARKER")]
    assert valores == ["y", "=", "a", "+", "b", "*", "2"]


def test_string_literal():
    tokens = tokenize('nome = "Ana"\n')
    tipos = types_of(tokens)
    assert "STRING" in tipos


def test_if_com_indentacao():
    codigo = (
        "if x > 0:\n"
        "    print(x)\n"
        "else:\n"
        "    print(0)\n"
    )
    tokens = tokenize(codigo)
    tipos = types_of(tokens)
    # Espera INDENT apos o ':' do if, e DEDENT antes do else
    assert "INDENT" in tipos
    assert "DEDENT" in tipos
    assert tipos.count("INDENT") == 2  # um para o bloco do if, um para o do else


def test_def_com_return():
    codigo = (
        "def soma(a, b):\n"
        "    return a + b\n"
    )
    tokens = tokenize(codigo)
    tipos = types_of(tokens)
    assert "DEF" in tipos
    assert "RETURN" in tipos
    assert "INDENT" in tipos and "DEDENT" in tipos


def test_comentario_e_ignorado():
    tokens = tokenize("x = 1  # isso e um comentario\n")
    for t in tokens:
        assert t.type != "COMMENT"


def test_for_range():
    codigo = "for i in range(10):\n    print(i)\n"
    tokens = tokenize(codigo)
    valores = [t.value for t in tokens if t.type not in ("NEWLINE", "ENDMARKER", "INDENT", "DEDENT")]
    assert valores[:6] == ["for", "i", "in", "range", "(", "10"]


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
