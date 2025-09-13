from __future__ import annotations
from typing import Any, Mapping
import json
from .errors import raise_f

# Minimal interpolation: replace "{{name}}" with env[name] stringified.

def _get_path(env: Mapping[str, Any], path: str) -> Any:
    cur: Any = env
    for part in path.split('.'):
        if isinstance(cur, Mapping) and part in cur:
            cur = cur[part]
        else:
            raise_f("F402A", f"Undefined template variable '{{{{{path}}}}}'")
    return cur

def interpolate_string(text: str, env: Mapping[str, Any]) -> str:
    out = []
    i = 0
    while i < len(text):
        if text.startswith("\\{{", i):
            out.append("{{"); i += 3; continue
        if text.startswith("\\}}", i):
            out.append("}}"); i += 3; continue
        if text.startswith("{{", i):
            j = text.find("}}", i+2)
            if j == -1:
                raise_f("F402B", "Unclosed template_ref in string")
            key = text[i+2:j].strip()
            if not key:
                raise_f("F402B", "Empty template_ref")
            # Support nested paths a.b.c
            val = _get_path(env, key)
            # JSON-serialize non-strings
            if isinstance(val, str):
                out.append(val)
            else:
                out.append(json.dumps(val, ensure_ascii=False))
            i = j+2
        else:
            out.append(text[i]); i += 1
    return "".join(out)

def substitute_scalar(value: Any, env: Mapping[str, Any]) -> Any:
    # $name or ${a.b}
    if isinstance(value, str):
        if value.startswith("${") and value.endswith("}"):
            path = value[2:-1].strip()
            return _get_path(env, path)
        if value.startswith("$") and len(value) > 1:
            name = value[1:]
            return _get_path(env, name)
    return value
