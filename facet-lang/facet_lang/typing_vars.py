from __future__ import annotations
import re
from typing import Any
from .errors import raise_f

ALLOWED_TYPES = {"string", "int", "float", "bool", "array", "object"}

def _typeof(x: Any) -> str:
    if isinstance(x, str): return "string"
    if isinstance(x, bool): return "bool"
    if isinstance(x, int) and not isinstance(x, bool): return "int"
    if isinstance(x, float): return "float"
    if isinstance(x, list): return "array"
    if isinstance(x, dict): return "object"
    return "object"

def validate_var_types(vars_map: dict[str, Any], specs: dict[str, dict]):
    for path, spec in (specs or {}).items():
        t = spec.get("type")
        if t not in ALLOWED_TYPES:
            raise_f("F451", f"Unknown type '{t}' for '{path}'")
        # navigate
        parts = path.split('.')
        cur: Any = vars_map
        for p in parts:
            if not isinstance(cur, dict) or p not in cur:
                raise_f("F451", f"Path '{path}' not found in @vars for typing")
            cur = cur[p]
        # type check
        actual = _typeof(cur)
        if t == "int" and actual == "float":
            raise_f("F451", f"Type mismatch for '{path}': expected int, got float")
        if t != actual and not (t == "float" and actual == "int"):
            raise_f("F451", f"Type mismatch for '{path}': expected {t}, got {actual}")
        # constraints
        if "enum" in spec:
            if cur not in spec["enum"]:
                raise_f("F452", f"Enum violation for '{path}': {cur} not in {spec['enum']}")
        if t in ("int", "float"):
            if "min" in spec and cur < spec["min"]:
                raise_f("F452", f"min violation for '{path}': {cur} < {spec['min']}")
            if "max" in spec and cur > spec["max"]:
                raise_f("F452", f"max violation for '{path}': {cur} > {spec['max']}")
        if t == "string" and "pattern" in spec:
            if not re.fullmatch(spec["pattern"], cur or ""):
                raise_f("F452", f"pattern violation for '{path}'")
