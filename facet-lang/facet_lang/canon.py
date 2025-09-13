from __future__ import annotations
from typing import Any
from .lexer import lex
from .parser import parse
from .imports import expand_imports
from .interpolator import interpolate_string, substitute_scalar
from .expr import eval_if
from .anchors import resolve_anchors
from .lenses import apply_pipeline, LensCall as LensCallDef
from .typing_vars import validate_var_types
from .errors import FacetError, raise_f
from . import limits

# NOTE: This is a minimal skeleton pipeline that returns an empty JSON for now.

def canonize(text: str, *, host_vars: dict[str, Any] | None = None, resolve_mode: str = "host",
             import_roots: list | None = None, strict_merge: bool = False, config: Any | None = None, 
             current_file: str | None = None) -> dict:
    tokens = lex(text)
    facets = parse(tokens)
    
    # Convert current_file to Path if provided
    current_path = None
    if current_file:
        from pathlib import Path
        current_path = Path(current_file)
    
    # Convert import_roots to Path objects if provided
    roots_paths = None
    if import_roots is not None:
        from pathlib import Path
        roots_paths = [Path(r) for r in import_roots]
    
    facets = expand_imports(facets, roots=roots_paths, strict_merge=strict_merge, current_file=current_path)

    # Compile-time facets: @vars and @var_types
    compile_vars: dict[str, Any] = {}
    var_types_specs: dict[str, Any] = {}
    normal_facets = []
    for f in facets:
        if f.name == 'vars':
            # top-down resolution inside @vars
            for node in f.body:
                from .ast import KV
                if isinstance(node, KV):
                    key = node.key
                    val = _resolve_value_topdown(node.value, compile_vars)
                    compile_vars[key] = val
            continue
        if f.name == 'var_types':
            # collect type specs as plain map
            spec_map: dict[str, Any] = {}
            for node in f.body:
                from .ast import KV
                if isinstance(node, KV):
                    spec_map[node.key] = node.value
            var_types_specs = spec_map
            continue
        normal_facets.append(f)

    # Step 4b: validate var types
    if var_types_specs:
        validate_var_types(compile_vars, var_types_specs)

    # Resolve environment by mode
    if resolve_mode == 'all':
        env = {**(compile_vars or {}), **(host_vars or {})}
    else:
        env = host_vars or {}
    # Step 5: conditionals on list items and facets (only list items supported in MVP)
    out: dict[str, Any] = {}
    for f in normal_facets:
        # Filter facet by if attribute if present and quoted string (enforced by parser in list-items; for facets we accept attr 'if')
        f_if = f.attrs.get('if') if isinstance(f.attrs, dict) else None
        if f_if is not None and not isinstance(f_if, str):
            raise_f("F704", "If expression must be quoted")
        if isinstance(f_if, str) and f_if != "":
            if not eval_if(f_if, env):
                continue
        # Build body map/list
        # Determine if body is a map or list (all ListItem -> list)
        from .ast import KV, ListItem, Fence
        is_list = all(isinstance(x, ListItem) for x in f.body) and len(f.body) > 0
        if is_list:
            arr: list[Any] = []
            for li in f.body:
                # item_if filter
                if li.item_if is not None and not eval_if(li.item_if, env):
                    continue
                v = li.value
                # fences: do not interpolate
                if not isinstance(v, Fence):
                    v = substitute_scalar(v, env)
                    if isinstance(v, str):
                        v = interpolate_string(v, env)
                else:
                    v = v.value
                # apply lenses if any
                if li.lenses:
                    calls = _convert_lenses(li.lenses)
                    if len(calls) > limits.MAX_LENS_CHAIN:
                        raise_f("F803", "Lens chain too long")
                    v = apply_pipeline(v, calls)
                arr.append(v)
            obj: dict[str, Any] = {"_attrs": f.attrs} if f.attrs else {}
            # Represent list-only facet body under a conventional key 'items'
            obj["items"] = arr
            
            # Handle anchor in facet header
            if f.attrs and "&" in f.attrs:
                anchor_name = f.attrs["&"]
                out[f.name] = {"&": anchor_name, "value": obj}
            else:
                out[f.name] = obj
        else:
            body_obj: dict[str, Any] = {}
            if f.attrs:
                body_obj["_attrs"] = f.attrs
            for item in f.body:
                if isinstance(item, KV):
                    val = item.value
                    if isinstance(val, list) and all(isinstance(x, ListItem) for x in val):
                        lst: list[Any] = []
                        for li in val:
                            if li.item_if is not None and not eval_if(li.item_if, env):
                                continue
                            v = li.value
                            if not isinstance(v, Fence):
                                v = substitute_scalar(v, env)
                                if isinstance(v, str):
                                    v = interpolate_string(v, env)
                            else:
                                v = v.value
                            if li.lenses:
                                calls = _convert_lenses(li.lenses)
                                if len(calls) > limits.MAX_LENS_CHAIN:
                                    raise_f("F803", "Lens chain too long")
                                v = apply_pipeline(v, calls)
                            lst.append(v)
                        val = lst
                    else:
                        if not isinstance(val, Fence):
                            val = substitute_scalar(val, env)
                            if isinstance(val, str):
                                val = interpolate_string(val, env)
                        else:
                            val = val.value
                    # lenses
                    if getattr(item, 'lenses', None):
                        calls = _convert_lenses(item.lenses)
                        if len(calls) > limits.MAX_LENS_CHAIN:
                            raise_f("F803", "Lens chain too long")
                        val = apply_pipeline(val, calls)
                    body_obj[item.key] = val
            
            # Handle anchor in facet header
            if f.attrs and "&" in f.attrs:
                anchor_name = f.attrs["&"]
                out[f.name] = {"&": anchor_name, "value": body_obj}
            else:
                out[f.name] = body_obj
    # Resolve anchors/aliases on the full JSON
    out = resolve_anchors(out)
    return out

def _resolve_value_topdown(value: Any, env: dict) -> Any:
    # In @vars: allow references only to previously declared names in env
    from .ast import Fence
    if isinstance(value, Fence):
        return value.value
    if isinstance(value, str):
        # scalar first ($name / ${a.b}) with F404 on missing
        if value.startswith("${") and value.endswith("}"):
            path = value[2:-1].strip()
            if not _path_exists(env, path):
                raise_f("F404", f"Variable forward reference '{path}'")
            return _get_path(env, path)
        if value.startswith("$") and len(value) > 1:
            name = value[1:]
            if not _path_exists(env, name):
                raise_f("F404", f"Variable forward reference '{name}'")
            return _get_path(env, name)
        # then interpolation {{a.b}} with F404 on missing
        if "{{" in value:
            # quick scan for refs and ensure present
            import re
            for m in re.finditer(r"\{\{\s*([a-zA-Z_][\w\.]+)\s*\}\}", value):
                ref = m.group(1)
                if not _path_exists(env, ref):
                    raise_f("F404", f"Variable forward reference '{ref}'")
            return interpolate_string(value, env)
        return value
    if isinstance(value, list):
        return [_resolve_value_topdown(v, env) for v in value]
    if isinstance(value, dict):
        return {k: _resolve_value_topdown(v, env) for k, v in value.items()}
    return value

def _convert_lenses(calls_ast: list) -> list[LensCallDef]:
    out = []
    for c in calls_ast:
        out.append(LensCallDef(c.name, tuple(c.args), dict(c.kwargs)))
    return out

def _path_exists(env: dict, path: str) -> bool:
    cur: Any = env
    for p in path.split('.'):
        if isinstance(cur, dict) and p in cur:
            cur = cur[p]
        else:
            return False
    return True

def _get_path(env: dict, path: str) -> Any:
    cur: Any = env
    for p in path.split('.'):
        cur = cur[p]
    return cur
