
import json, re, textwrap

class LensError(Exception): ...

def _ensure_str(v, name):
    if not isinstance(v, str):
        raise LensError(f"F102: lens '{name}' expects string, got {type(v).__name__}")

def trim(v): _ensure_str(v, "trim"); return v.strip()

def dedent(v):
    _ensure_str(v, "dedent")
    v = v.replace("\r\n", "\n").replace("\r", "\n")
    return textwrap.dedent(v)

def squeeze_spaces(v):
    _ensure_str(v, "squeeze_spaces")
    lines = v.splitlines()
    return "\n".join(re.sub(r"[ \t]+", " ", ln) for ln in lines)

def limit(v, n=0):
    _ensure_str(v, "limit")
    try: n = int(n)
    except: raise LensError("F102: limit(N) requires integer N")
    if n < 0: return v
    b = v.encode("utf-8")
    if len(b) <= n: return v
    b = b[:n]
    while True:
        try: return b.decode("utf-8")
        except UnicodeDecodeError: b = b[:-1]

def normalize_newlines(v):
    _ensure_str(v, "normalize_newlines")
    return v.replace("\r\n", "\n").replace("\r", "\n")

def json_minify(v):
    _ensure_str(v, "json_minify")
    try:
        obj = json.loads(v)
        return json.dumps(obj, separators=(",", ":"), ensure_ascii=False)
    except Exception:
        return v

def json_parse(v):
    _ensure_str(v, "json_parse")
    try:
        return json.loads(v)
    except Exception:
        return v

def strip_markdown(v):
    _ensure_str(v, "strip_markdown")
    s = v
    s = re.sub(r"`{1,3}", "", s)
    s = re.sub(r"\*{1,3}", "", s)
    s = re.sub(r"^#{1,6}\s*", "", s, flags=re.MULTILINE)
    s = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", s)
    s = re.sub(r"!\[([^\]]*)\]\([^)]*\)", r"\1", s)
    return s

REGISTRY = {
    "trim": (trim, 0),
    "dedent": (dedent, 0),
    "squeeze_spaces": (squeeze_spaces, 0),
    "limit": (limit, 1),
    "normalize_newlines": (normalize_newlines, 0),
    "json_minify": (json_minify, 0),
    "json_parse": (json_parse, 0),
    "strip_markdown": (strip_markdown, 0),
}

def apply_lenses(value, lenses):
    out = value
    for name, args in lenses:
        if name not in REGISTRY:
            raise LensError(f"F102: unknown lens '{name}'")
        fn, argc = REGISTRY[name]
        out = fn(out, *args) if argc else fn(out)
    return out
