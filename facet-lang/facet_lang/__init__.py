"""FACET v1.1 (Draft r3) — Python package."""
from .canon import canonize
from .errors import FacetError

__version__ = "0.0.2"
__all__ = ["canonize", "FacetError", "__version__"]
