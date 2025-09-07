"""
Golden tests for FACET parser - validates exact canonical JSON output.
"""
import json
import pytest
from pathlib import Path

from facet import parser


def load_facet_and_expected_json(facet_path: Path):
    """Load a .facet file and its corresponding .json file."""
    with open(facet_path, 'r', encoding='utf-8') as f:
        facet_content = f.read()

    json_path = facet_path.with_suffix('.json')
    if not json_path.exists():
        pytest.skip(f"Expected JSON file {json_path} not found")

    with open(json_path, 'r', encoding='utf-8') as f:
        expected_json = json.load(f)

    return facet_content, expected_json


@pytest.mark.parametrize("facet_file", [
    "examples/recursion.facet",
    "examples/test_extended.facet",
    "examples/simplified_complex_test.facet",
    "tests/complete_test.facet"
])
def test_golden_output(facet_file):
    """Test that FACET files produce exact expected JSON output."""
    facet_path = Path(__file__).parent.parent / facet_file
    facet_content, expected_json = load_facet_and_expected_json(facet_path)

    # Parse the FACET content
    actual_json_str = parser.to_json(facet_content)
    actual_json = json.loads(actual_json_str)

    # Compare the actual and expected JSON
    assert actual_json == expected_json, f"Golden test failed for {facet_file}"

    # Also verify that the JSON string is properly formatted
    # Re-parse to ensure it's valid JSON
    reparsed = json.loads(actual_json_str)
    assert reparsed == actual_json


def test_canonical_formatting():
    """Test that the JSON output follows canonical formatting rules."""
    facet_content = """
@meta
  id: "test"
  version: 1.0

@system
  role: "Assistant"
  constraints: ["Be helpful"]
"""

    json_output = parser.to_json(facet_content)

    # Parse and check structure
    parsed = json.loads(json_output)

    # Verify top-level structure
    assert isinstance(parsed, dict)
    assert "meta" in parsed
    assert "system" in parsed

    # Verify facet attributes are in _attrs
    assert "_attrs" not in parsed["system"]  # No attributes in this test

    # Verify key order is preserved (implementation detail)
    system_keys = list(parsed["system"].keys())
    expected_order = ["role", "constraints"]
    assert system_keys == expected_order


def test_extended_scalars():
    """Test extended scalar types in golden output."""
    facet_content = """
@meta
  timestamp: @2024-01-01T12:00:00Z
  duration: 5m
  size: 1024KB
  pattern: /test/i
"""

    json_output = parser.to_json(facet_content)
    parsed = json.loads(json_output)

    # Verify extended scalars are serialized as strings
    assert isinstance(parsed["meta"]["timestamp"], str)
    assert isinstance(parsed["meta"]["duration"], str)
    assert isinstance(parsed["meta"]["size"], str)
    assert isinstance(parsed["meta"]["pattern"], str)

    # Verify values are preserved exactly
    assert parsed["meta"]["timestamp"] == "2024-01-01T12:00:00Z"
    assert parsed["meta"]["duration"] == "5m"
    assert parsed["meta"]["size"] == "1024KB"
    assert parsed["meta"]["pattern"] == "/test/i"


def test_lenses_applied():
    """Test that lenses are applied and their results are in the output."""
    facet_content = """
@user
  message: """
    Hello,   world!
    This has extra spaces.
  """
    |> dedent |> squeeze_spaces |> trim
"""

    json_output = parser.to_json(facet_content)
    parsed = json.loads(json_output)

    # Verify lens result
    expected = "Hello, world!\nThis has extra spaces."
    assert parsed["user"]["message"] == expected


def test_anchors_and_aliases():
    """Test anchor/alias resolution in golden output."""
    facet_content = """
@system
  style &polite: "Polite and helpful"
  personality: *polite
  greeting: "Hello"
"""

    json_output = parser.to_json(facet_content)
    parsed = json.loads(json_output)

    # Anchors should not appear in output, only aliases should resolve
    assert "style" in parsed["system"]
    assert parsed["system"]["personality"] == "Polite and helpful"
    assert parsed["system"]["greeting"] == "Hello"

    # Verify no anchor artifacts remain
    assert "&polite" not in json_output
