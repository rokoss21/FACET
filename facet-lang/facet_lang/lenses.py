from __future__ import annotations
import json
from hashlib import blake2b
from typing import Any
from .errors import raise_f
import re

ALGOVERSION = "r3.1"  # bump if algorithms change

# ------------------------ helpers ------------------------

def _canonical_bytes(value: Any) -> bytes:
    # JSON bytes with stable ordering; ensure_ascii False to keep UTF-8
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")

def _seed_key(seed: Any, value: Any) -> int:
    h = blake2b(digest_size=16)
    h.update(str(seed).encode("utf-8"))
    h.update(b"\x1F")
    h.update(_canonical_bytes(value))
    return int.from_bytes(h.digest()[:8], "big")

# ------------------------ builtin lenses (subset) ------------------------

def trim(x: Any) -> Any:
    if isinstance(x, str):
        return x.strip()
    return x

def dedent(x: Any) -> Any:
    if not isinstance(x, str):
        raise_f("F102", "dedent expects string")
    import textwrap
    return textwrap.dedent(x)

def squeeze_spaces(x: Any) -> Any:
    if not isinstance(x, str):
        raise_f("F102", "squeeze_spaces expects string")
    import re
    return re.sub(r"[ \t]+", " ", x)

def limit(x: Any, n: int) -> Any:
    if not isinstance(x, str):
        raise_f("F102", "limit expects string")
    b = x.encode("utf-8")
    if len(b) <= n:
        return x
    return b[:n].decode("utf-8", errors="ignore")

def lower(x: Any) -> Any:
    if not isinstance(x, str):
        raise_f("F102", "lower expects string")
    return x.lower()

def upper(x: Any) -> Any:
    if not isinstance(x, str):
        raise_f("F102", "upper expects string")
    return x.upper()

def replace(x: Any, old: str, new: str) -> Any:
    if not isinstance(x, str):
        raise_f("F102", "replace expects string")
    return x.replace(old, new)

def regex_replace(x: Any, pattern: str, repl: str) -> Any:
    if not isinstance(x, str):
        raise_f("F102", "regex_replace expects string")
    try:
        return re.sub(pattern, repl, x)
    except re.error:
        raise_f("F803", "regex timeout or error")

# --------------------- deterministic lenses ---------------------

def choose(x: Any, *, seed: Any | None = None) -> Any:
    if seed is None:
        raise_f("F804", "Seed required for deterministic lens 'choose'")
    if not isinstance(x, list):
        raise_f("F102", "choose expects list")
    if not x:
        raise_f("F102", "choose expects non-empty list")
    k = _seed_key(seed, x)
    return x[k % len(x)]

def shuffle(x: Any, *, seed: Any | None = None) -> Any:
    if seed is None:
        raise_f("F804", "Seed required for deterministic lens 'shuffle'")
    if not isinstance(x, list):
        raise_f("F102", "shuffle expects list")
    import random
    k = _seed_key(seed, x)
    rng = random.Random(k)
    out = list(x)
    rng.shuffle(out)
    return out

BUILTINS = {
    "trim": trim,
    "dedent": dedent,
    "squeeze_spaces": squeeze_spaces,
    "limit": limit,
    "lower": lower,
    "upper": upper,
    "replace": replace,
    "regex_replace": regex_replace,
    "choose": choose,
    "shuffle": shuffle,
}

from dataclasses import dataclass
@dataclass
class LensCall:
    name: str
    args: tuple
    kwargs: dict

# simple pipeline applier (no plugins yet)

def apply_pipeline(value: Any, pipeline: list[LensCall]) -> Any:
    out = value
    for call in pipeline:
        fn = BUILTINS.get(call.name)
        if fn is None:
            raise_f("F802", f"Unknown custom/builtin lens '{call.name}'")
        # split args/kwargs; our skeleton only supports kwargs for choose/shuffle
        out = fn(out, *call.args, **call.kwargs)
    return out
