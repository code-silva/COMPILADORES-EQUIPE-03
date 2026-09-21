"""Testes unitários da tabela de símbolos e dos erros léxicos."""

import unittest

from src.lexer.errors import LexicalError
from src.lexer.symbol_table import Symbol, SymbolTable
from src.lexer.token_type import TokenType


class LexicalErrorTests(unittest.TestCase):
    def test_formats_message_with_source_position(self) -> None:
        error = LexicalError("Caractere inesperado '@'", 3, 11)

        self.assertEqual(error.message, "Caractere inesperado '@'")
        self.assertEqual(error.line, 3)
        self.assertEqual(error.column, 11)
        self.assertEqual(
            str(error),
            "LexicalError[3:11]: Caractere inesperado '@'",
        )


class SymbolTableTests(unittest.TestCase):
    def setUp(self) -> None:
        self.table = SymbolTable()

    def test_inserts_and_finds_symbol(self) -> None:
        symbol = self.table.insert("total", TokenType.IDENTIFIER, 2, 5)

        self.assertEqual(
            symbol,
            Symbol("total", TokenType.IDENTIFIER, 2, 5),
        )
        self.assertTrue(self.table.contains("total"))
        self.assertIs(self.table.lookup("total"), symbol)

    def test_preserves_first_occurrence(self) -> None:
        first = self.table.insert("total", TokenType.IDENTIFIER, 2, 5)
        repeated = self.table.insert("total", TokenType.IDENTIFIER, 9, 3)

        self.assertIs(repeated, first)
        self.assertEqual(repeated.first_declared_line, 2)
        self.assertEqual(repeated.first_declared_col, 5)
        self.assertEqual(len(self.table.all_symbols()), 1)

    def test_returns_none_for_unknown_symbol(self) -> None:
        self.assertIsNone(self.table.lookup("ausente"))
        self.assertFalse(self.table.contains("ausente"))

    def test_lists_symbols_in_insertion_order(self) -> None:
        first = self.table.insert("x", TokenType.IDENTIFIER, 1, 1)
        second = self.table.insert("y", TokenType.IDENTIFIER, 2, 1)

        self.assertEqual(self.table.all_symbols(), [first, second])


if __name__ == "__main__":
    unittest.main()
