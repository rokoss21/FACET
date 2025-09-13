from __future__ import annotations
from dataclasses import dataclass

@dataclass
class Pos:
    line: int
    col: int

    def __str__(self) -> str:
        return f"{self.line}:{self.col}"

class FacetError(Exception):
    def __init__(self, code: str, msg: str, pos: Pos | None = None, snippet: str | None = None):
        self.code = code
        self.msg = msg
        self.pos = pos
        self.snippet = snippet
        loc = f" at {pos}" if pos else ""
        super().__init__(f"{code}{loc}: {msg}")

def raise_f(code: str, msg: str, pos: Pos | None = None, snippet: str | None = None):
    raise FacetError(code, msg, pos, snippet)
