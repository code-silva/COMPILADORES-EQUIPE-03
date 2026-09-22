"""Testes unitários da tabela de símbolos e dos erros léxicos."""

import unittest

from src.lexer.errors import LexicalError
from src.lexer.symbol_table import (
    Symbol,
    contains_symbol,
    create_symbol_table,
    insert_symbol,
    lookup_symbol,
)
from src.lexer.token_type import TokenType


class LexicalErrorTests(unittest.TestCase):
    def test_formats_message_with_source_position(self) -> None:
        error = LexicalError("Caractere inesperado '@'", 3, 11)

        self.assertEqual(error.message, "Caractere inesperado '@'")
        self.assertEqual(error.line, 3)
        self.assertEqual(error.column, 11)
        self.assertEqual(
            str(error),
            "Erro Léxico [Linha 3, Coluna 11]: Caractere inesperado '@'",
        )


class SymbolTableTests(unittest.TestCase):
    def setUp(self) -> None:
        self.table = create_symbol_table()

    def test_inserts_and_finds_symbol(self) -> None:
        symbol = insert_symbol(
            self.table,
            "total",
            TokenType.IDENTIFIER,
            2,
            5,
        )

        self.assertEqual(
            symbol,
            Symbol("total", TokenType.IDENTIFIER, 2, 5),
        )
        self.assertTrue(contains_symbol(self.table, "total"))
        self.assertIs(lookup_symbol(self.table, "total"), symbol)

    def test_preserves_first_occurrence(self) -> None:
        first = insert_symbol(
            self.table,
            "total",
            TokenType.IDENTIFIER,
            2,
            5,
        )
        repeated = insert_symbol(
            self.table,
            "total",
            TokenType.IDENTIFIER,
            9,
            3,
        )

        self.assertIs(repeated, first)
        self.assertEqual(repeated.first_declared_line, 2)
        self.assertEqual(repeated.first_declared_col, 5)
        self.assertEqual(len(self.table), 1)

    def test_returns_none_for_unknown_symbol(self) -> None:
        self.assertIsNone(lookup_symbol(self.table, "ausente"))
        self.assertFalse(contains_symbol(self.table, "ausente"))

    def test_lists_symbols_in_insertion_order(self) -> None:
        first = insert_symbol(
            self.table,
            "x",
            TokenType.IDENTIFIER,
            1,
            1,
        )
        second = insert_symbol(
            self.table,
            "y",
            TokenType.IDENTIFIER,
            2,
            1,
        )

        self.assertEqual(list(self.table.values()), [first, second])


if __name__ == "__main__":
    unittest.main()
