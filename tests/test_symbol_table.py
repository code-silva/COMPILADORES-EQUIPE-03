"""Testes da tabela de símbolos com escopos aninhados (#30)."""

from dataclasses import FrozenInstanceError

import pytest

from src.semantic import Symbol, SymbolTable


def sym(name: str, type_: str = "int", line: int = 1) -> Symbol:
    return Symbol(name=name, type=type_, line=line)


# --------------------------------------------------------------------- Symbol


def test_symbol_guarda_nome_tipo_e_posicao() -> None:
    s = Symbol(name="total", type="float", line=3, column=5)
    assert (s.name, s.type, s.line, s.column) == ("total", "float", 3, 5)


def test_symbol_coluna_padrao_e_zero() -> None:
    assert Symbol(name="x", type="int", line=1).column == 0


def test_symbol_e_imutavel() -> None:
    s = sym("x")
    with pytest.raises(FrozenInstanceError):
        s.type = "str"  # type: ignore[misc]


@pytest.mark.parametrize("type_", ["int", "float", "str", "bool", "None"])
def test_symbol_aceita_tipos_primitivos(type_: str) -> None:
    assert sym("v", type_).type == type_


# ---------------------------------------------------------------- escopo único


def test_tabela_nova_esta_vazia_e_e_global() -> None:
    table = SymbolTable()
    assert table.symbols == {}
    assert table.parent is None
    assert table.depth == 0


def test_define_e_lookup_no_mesmo_escopo() -> None:
    table = SymbolTable()
    x = table.define(sym("x"))
    assert table.lookup("x") is x
    assert table.lookup_current_scope("x") is x
    assert table.symbols == {"x": x}


def test_varios_simbolos_no_mesmo_escopo() -> None:
    table = SymbolTable()
    table.define(sym("a", "int"))
    table.define(sym("b", "str"))
    assert table.lookup("a").type == "int"
    assert table.lookup("b").type == "str"


def test_redeclaracao_no_mesmo_escopo_e_rejeitada() -> None:
    table = SymbolTable()
    table.define(sym("x", line=1))
    with pytest.raises(ValueError, match="'x' já declarada neste escopo \\(linha 1\\)"):
        table.define(sym("x", "str", line=4))
    assert table.lookup("x").type == "int"


# ------------------------------------------------------- identificador ausente


def test_lookup_de_nome_inexistente_retorna_none() -> None:
    table = SymbolTable()
    assert table.lookup("fantasma") is None
    assert table.lookup_current_scope("fantasma") is None
    assert "fantasma" not in table


def test_lookup_inexistente_em_escopos_aninhados() -> None:
    inner = SymbolTable(parent=SymbolTable(parent=SymbolTable()))
    assert inner.lookup("fantasma") is None


# --------------------------------------------------------- escopos aninhados


def test_filho_enxerga_simbolo_do_pai() -> None:
    global_scope = SymbolTable()
    x = global_scope.define(sym("x"))
    block = SymbolTable(parent=global_scope)

    assert block.lookup("x") is x
    assert block.lookup_current_scope("x") is None
    assert "x" in block


def test_resolucao_sobe_varios_niveis() -> None:
    global_scope = SymbolTable()
    x = global_scope.define(sym("x"))
    level1 = SymbolTable(parent=global_scope)
    level2 = SymbolTable(parent=level1)

    assert level2.depth == 2
    assert level2.lookup("x") is x


def test_pai_nao_enxerga_simbolo_do_filho() -> None:
    global_scope = SymbolTable()
    block = SymbolTable(parent=global_scope)
    block.define(sym("local"))

    assert global_scope.lookup("local") is None
    assert "local" not in global_scope


def test_escopos_irmaos_sao_isolados() -> None:
    global_scope = SymbolTable()
    then_block = SymbolTable(parent=global_scope)
    else_block = SymbolTable(parent=global_scope)
    then_block.define(sym("y"))

    assert else_block.lookup("y") is None


def test_sombreamento_usa_o_escopo_mais_proximo() -> None:
    global_scope = SymbolTable()
    outer_x = global_scope.define(sym("x", "int", line=1))
    block = SymbolTable(parent=global_scope)
    inner_x = block.define(sym("x", "str", line=3))

    assert block.lookup("x") is inner_x
    assert global_scope.lookup("x") is outer_x


def test_mesmo_nome_no_pai_nao_e_redeclaracao() -> None:
    global_scope = SymbolTable()
    global_scope.define(sym("x"))
    block = SymbolTable(parent=global_scope)
    block.define(sym("x", "float"))  # não deve lançar
    assert block.lookup_current_scope("x").type == "float"


def test_repr_mostra_simbolos_e_profundidade() -> None:
    table = SymbolTable()
    table.define(sym("x"))
    assert repr(table) == "SymbolTable(symbols=['x'], depth=0)"
