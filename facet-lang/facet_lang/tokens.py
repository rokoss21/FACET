from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from .errors import Pos

class TokKind(Enum):
    AT = auto()               # '@'
    IDENT = auto()
    STRING = auto()
    NUMBER = auto()
    BOOLEAN = auto()
    NULL = auto()
    LBRACE = auto()
    RBRACE = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    LPAREN = auto()
    RPAREN = auto()
    COMMA = auto()
    COLON = auto()
    AMP = auto()              # '&'
    STAR = auto()             # '*'
    EQUAL = auto()
    DASH = auto()
    PIPE = auto()             # '|>' as a single token (PIPE)
    NEWLINE = auto()
    INDENT = auto()
    DEDENT = auto()
    FENCE = auto()            # triple backtick block captured as a single token with text
    EOF = auto()

@dataclass
class Token:
    kind: TokKind
    value: str
    pos: Pos
