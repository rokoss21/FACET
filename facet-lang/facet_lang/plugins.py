from __future__ import annotations
from typing import Any

# Placeholder sandbox runtime; to be implemented in later iteration.
class PluginRuntime:
    def __init__(self, paths: list, timeout_ms: int = 50):
        self.paths = paths
        self.timeout_ms = timeout_ms

    def call(self, name: str, value: Any, args: list[Any], kwargs: dict[str, Any]) -> Any:
        raise NotImplementedError("Plugin runtime not implemented in skeleton")
