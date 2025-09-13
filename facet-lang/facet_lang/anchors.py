from __future__ import annotations
from typing import Any
from .errors import raise_f

# Simple anchor/alias resolution over already-evaluated JSON-like structures.
# Collect anchors &name attached to values and substitute aliases *name.

ANCHOR_KEY = "&"
ALIAS_KEY = "*"


def _walk_collect(value: Any, anchors: dict[str, Any]):
    if isinstance(value, dict):
        # anchor on this node?
        if ANCHOR_KEY in value and "value" in value:
            name = value[ANCHOR_KEY]
            if name in anchors:
                raise_f("F202", f"Anchor redefinition: {name}")
            # store a deep reference (already evaluated value without anchor key)
            v = value["value"]
            anchors[name] = v
        for k, v in list(value.items()):
            if k not in (ANCHOR_KEY, "value"):
                _walk_collect(v, anchors)
    elif isinstance(value, list):
        for it in value:
            _walk_collect(it, anchors)


def _walk_substitute(value: Any, anchors: dict[str, Any], visiting: set[str] | None = None) -> Any:
    visiting = visiting or set()
    if isinstance(value, dict):
        if ALIAS_KEY in value and len(value) == 1:
            name = value[ALIAS_KEY]
            if name in visiting:
                raise_f("F201", "Anchor cycle detected")
            if name not in anchors:
                raise_f("F201", f"Undefined anchor alias: {name}")
            visiting.add(name)
            result = _walk_substitute(anchors[name], anchors, visiting)
            visiting.remove(name)
            return result
        # Handle anchored values: remove anchor metadata and process the actual value
        if ANCHOR_KEY in value and "value" in value:
            # This is an anchored value - return only the processed content, not the anchor metadata
            actual_value = value["value"]
            return _walk_substitute(actual_value, anchors, visiting)
        return {k: _walk_substitute(v, anchors, visiting) for k, v in value.items()}
    if isinstance(value, list):
        return [_walk_substitute(it, anchors, visiting) for it in value]
    return value


def resolve_anchors(json_obj: Any) -> Any:
    anchors: dict[str, Any] = {}
    _walk_collect(json_obj, anchors)
    return _walk_substitute(json_obj, anchors)
