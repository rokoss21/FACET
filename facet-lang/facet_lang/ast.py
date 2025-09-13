from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
from .errors import Pos

@dataclass
class Fence:
    value: str

@dataclass
class LensCall:
    name: str
    args: list[Any] = field(default_factory=list)
    kwargs: dict[str, Any] = field(default_factory=dict)

@dataclass
class KV:
    key: str
    value: Any
    lenses: list[LensCall]
    pos: Pos

@dataclass
class ListItem:
    value: Any
    item_if: str | None
    lenses: list[LensCall]
    pos: Pos

@dataclass
class Facet:
    name: str
    attrs: dict[str, Any]
    body: list[Any]
    pos: Pos
