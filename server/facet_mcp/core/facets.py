"""
FACET Execution Engine for MCP Server

Provides high-performance FACET document execution with SIMD optimizations
and template variable substitution.
"""

import time
import json
from typing import Any, Dict, List, Optional
from pathlib import Path
import sys

# Add the src directory to the path to import facet
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from facet import parse_facet, to_json, FACETError
from facet.lenses import apply_lenses


class FACETExecutionResult:
    """Result of FACET document execution"""

    def __init__(self, result: Dict[str, Any], execution_time_ms: float):
        self.result = result
        self.execution_time_ms = execution_time_ms
        self.success = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary for MCP response"""
        result = self.result.copy()
        result["_meta"] = {
            "execution_time_ms": self.execution_time_ms,
            "server": "FACET MCP Server v0.1.0"
        }
        return result


class FACETExecutionError:
    """Error during FACET execution"""

    def __init__(self, error: str, error_type: str):
        self.error = error
        self.error_type = error_type
        self.success = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for MCP response"""
        return {
            "success": False,
            "error": self.error,
            "error_type": self.error_type
        }


class FACETEngine:
    """
    High-performance FACET execution engine for MCP server.

    Features:
    - SIMD-optimized lens execution
    - Template variable substitution
    - Error handling and validation
    - Performance monitoring
    """

    def __init__(self):
        self.template_engine = TemplateEngine()

    async def execute_facet(
        self,
        facet_source: str,
        variables: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a complete FACET document with SIMD optimizations.

        Args:
            facet_source: Complete FACET document as string
            variables: Optional template variables for substitution

        Returns:
            Execution result as dictionary
        """
        start_time = time.time()

        try:
            # Apply template variables if provided
            if variables:
                facet_source = self.template_engine.substitute_variables(
                    facet_source, variables
                )

            # Parse and execute FACET document
            parsed = parse_facet(facet_source)
            result_json = to_json(parsed)

            # Parse JSON result for further processing
            result_dict = json.loads(result_json)

            execution_time = (time.time() - start_time) * 1000

            return FACETExecutionResult(result_dict, execution_time).to_dict()

        except FACETError as e:
            return FACETExecutionError(str(e), "FACETError").to_dict()
        except Exception as e:
            return FACETExecutionError(str(e), type(e).__name__).to_dict()

    async def apply_lenses_to_text(
        self,
        text: str,
        lenses: List[str]
    ) -> str:
        """
        Apply FACET lenses to text with SIMD optimizations where beneficial.

        Args:
            text: Input text to process
            lenses: List of lens names to apply (e.g., ['dedent', 'trim'])

        Returns:
            Processed text after applying all lenses
        """
        try:
            result = text

            # Apply each lens in sequence
            for lens_spec in lenses:
                result = self._apply_single_lens(result, lens_spec)

            return result

        except Exception as e:
            raise ValueError(f"Error applying lenses: {e}")

    def _apply_single_lens(self, text: str, lens_spec: str) -> str:
        """Apply a single lens to text"""
        try:
            # Parse lens specification (e.g., "limit(100)" -> function_name="limit", args=[100])
            if "(" in lens_spec and lens_spec.endswith(")"):
                func_name = lens_spec.split("(")[0]
                args_str = lens_spec.split("(")[1][:-1]  # Remove closing paren
                if args_str.strip():
                    # Parse arguments (simple case - single integer)
                    try:
                        args = [int(args_str.strip())]
                    except ValueError:
                        raise ValueError(f"Unsupported lens arguments: {args_str}")
                else:
                    args = []
            else:
                func_name = lens_spec
                args = []

            # Apply the lens using FACET's lens system
            if args:
                result = apply_lenses(text, [(func_name, args[0])])
            else:
                result = apply_lenses(text, [(func_name, None)])

            return result

        except Exception as e:
            raise ValueError(f"Error applying lens '{lens_spec}': {e}")


class TemplateEngine:
    """
    Simple template engine for variable substitution in FACET documents.

    Supports basic {{variable}} syntax for template substitution.
    """

    def substitute_variables(
        self,
        facet_source: str,
        variables: Dict[str, Any]
    ) -> str:
        """
        Substitute variables in FACET document.

        Args:
            facet_source: FACET document with {{variable}} placeholders
            variables: Dictionary of variable values

        Returns:
            FACET document with variables substituted
        """
        result = facet_source

        for key, value in variables.items():
            placeholder = "{{" + key + "}}"

            # Convert value to appropriate string representation
            if isinstance(value, str):
                replacement = value
            elif isinstance(value, (int, float, bool)):
                replacement = str(value)
            elif isinstance(value, dict):
                replacement = json.dumps(value, ensure_ascii=False)
            elif isinstance(value, list):
                replacement = json.dumps(value, ensure_ascii=False)
            else:
                replacement = str(value)

            result = result.replace(placeholder, replacement)

        return result
