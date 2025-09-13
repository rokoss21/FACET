from __future__ import annotations
from pathlib import Path
from typing import Iterable, Any
from .errors import raise_f
from . import limits
import re

# Minimal @import expansion with allowlist and simple merge/replace

def _is_allowed(path: Path, roots: list[Path]) -> bool:
    try:
        rp = path.resolve()
    except Exception:
        return False
    for r in roots:
        try:
            rr = Path(r).resolve()
        except Exception:
            continue
        try:
            rp.relative_to(rr)
            return True
        except Exception:
            continue
    return False

def _auto_detect_roots(current_file: Path | None = None) -> list[Path]:
    """Auto-detect allowlist roots based on common project patterns"""
    detected_roots = []
    
    if current_file:
        # Start from current file's directory
        current_dir = current_file.parent if current_file.is_file() else current_file
    else:
        # Start from current working directory
        current_dir = Path.cwd()
    
    # Look for common project indicators
    search_dir = current_dir
    for _ in range(5):  # Search up to 5 levels up
        # Common project root indicators
        indicators = [
            'pyproject.toml', 'setup.py', 'requirements.txt',
            'package.json', 'Cargo.toml', '.git', '.gitignore',
            'facet.config.json'
        ]
        
        if any((search_dir / indicator).exists() for indicator in indicators):
            # Add common subdirectories that might contain FACET files
            potential_dirs = [
                search_dir,
                search_dir / 'facets',
                search_dir / 'templates',
                search_dir / 'common',
                search_dir / 'shared',
                search_dir / 'configs',
                search_dir / 'samples'
            ]
            
            for d in potential_dirs:
                if d.exists() and d.is_dir():
                    detected_roots.append(d)
            break
        
        if search_dir.parent == search_dir:  # Reached filesystem root
            break
        search_dir = search_dir.parent
    
    # Fallback: current directory and its subdirectories
    if not detected_roots:
        detected_roots = [current_dir]
    
    return detected_roots

def expand_imports(facets: list, *, roots: list[Path] | None = None, strict_merge: bool = False, _stack: list[Path] | None = None, _count: list[int] | None = None, current_file: Path | None = None) -> list:
    result = []
    _stack = _stack or []
    _count = _count or [0]
    
    # Auto-detect roots if not provided
    if roots is None:
        roots = _auto_detect_roots(current_file)
    elif not roots:  # empty list provided
        roots = _auto_detect_roots(current_file)
    for f in facets:
        if getattr(f, 'name', None) == 'import':
            path = f.attrs.get('path') if isinstance(f.attrs, dict) else None
            if not isinstance(path, str):
                raise_f("F601", "@import path missing or invalid")
            p = Path(path)
            if p.is_absolute():
                raise_f("F601", "Absolute paths are forbidden in @import")
            if re.match(r"^[a-z]+://", path):
                raise_f("F601", "Network URLs are forbidden in @import")
            # resolve relative to CWD; for real impl, use current file dir
            full = (Path.cwd() / p)
            if not _is_allowed(full, roots):
                raise_f("F601", "Import path not allowed")
            if not full.exists():
                raise_f("F601", "Import not found")
            if len(_stack) >= limits.MAX_IMPORT_DEPTH:
                raise_f("F602", "Import depth exceeded")
            _count[0] += 1
            if _count[0] > limits.MAX_IMPORTS:
                raise_f("F602", "Import count exceeded")
            if full in _stack:
                raise_f("F602", "Import cycle detected")
            text = full.read_text(encoding='utf-8')
            from .lexer import lex
            from .parser import parse
            sub = parse(lex(text))
            # Recursively expand imports
            sub = expand_imports(sub, roots=roots, strict_merge=strict_merge, _stack=_stack + [full], _count=_count)
            # Merge strategy
            strategy = f.attrs.get('strategy') if isinstance(f.attrs, dict) else 'merge'
            if strategy not in (None, 'merge', 'replace'):
                strategy = 'merge'
            result = _merge_facets(result, sub, strategy=strategy, strict=strict_merge)
        else:
            result.append(f)
    return result

def _merge_facets(dst: list, src: list, *, strategy: str, strict: bool) -> list:
    # Merge by facet name
    out = list(dst)
    for f in src:
        # find existing by name
        idx = next((i for i, x in enumerate(out) if getattr(x, 'name', None) == f.name), None)
        if idx is None or strategy == 'replace':
            if idx is not None and strategy == 'replace':
                out[idx] = f
            else:
                out.append(f)
        else:
            # deep-merge maps and concat lists inside bodies
            a = out[idx]
            # merge attrs map last-wins (simple)
            if isinstance(a.attrs, dict) and isinstance(f.attrs, dict):
                attrs = dict(a.attrs)
                attrs.update(f.attrs)
                a.attrs = attrs
            # merge body assuming KV maps; lists concatenated
            merged_body = []
            from .ast import KV, ListItem
            if all(isinstance(x, KV) for x in a.body) and all(isinstance(x, KV) for x in f.body):
                # map merge: last key wins, keep first appearance order
                seen = {}
                for kv in a.body + f.body:
                    if isinstance(kv, KV):
                        if kv.key not in seen:
                            seen[kv.key] = kv
                        else:
                            seen[kv.key] = kv
                merged_body = list(seen.values())
                a.body = merged_body
            elif all(isinstance(x, ListItem) for x in a.body) and all(isinstance(x, ListItem) for x in f.body):
                a.body = list(a.body) + list(f.body)
            else:
                # type mismatch: replace unless strict
                if strict:
                    raise_f("F606", "Import merge type mismatch in strict mode")
                out[idx] = f
    return out
