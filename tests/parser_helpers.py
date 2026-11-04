"""Utilitários compartilhados pelos testes do analisador sintático."""

from dataclasses import fields, is_dataclass, replace

from src.parser import Node


def strip_positions(value):
    """Zera ``line``/``column`` recursivamente para comparar só a estrutura.

    Como ``Node`` usa ``kw_only=True``, a igualdade dos dataclasses também
    compara a posição; este helper permite escrever a árvore esperada sem ela.
    """
    if isinstance(value, list):
        return [strip_positions(item) for item in value]
    if is_dataclass(value) and isinstance(value, Node):
        changes = {
            f.name: strip_positions(getattr(value, f.name))
            for f in fields(value)
            if f.name not in ("line", "column")
        }
        return replace(value, line=0, column=0, **changes)
    return value
