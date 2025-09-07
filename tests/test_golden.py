"""
Golden tests for FACET parser - validates exact canonical JSON output.
"""

import json
from pathlib import Path

import pytest

from facet import parser


def load_facet_and_expected_json(facet_path: Path):
    """Load a .facet file and its corresponding .json file."""
    with open(facet_path, "r", encoding="utf-8") as f:
        facet_content = f.read()

    json_path = facet_path.with_suffix(".json")
    if not json_path.exists():
        pytest.skip(f"Expected JSON file {json_path} not found")

    with open(json_path, "r", encoding="utf-8") as f:
        expected_json = json.load(f)

    return facet_content, expected_json


@pytest.mark.parametrize(
    "facet_file",
    [
        "examples/recursion.facet",
        "examples/test_extended.facet",
        "examples/simplified_complex_test.facet",
        "tests/complete_test.facet",
    ],
)
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
    facet_file = Path(__file__).parent / "fixtures" / "test_formatting.facet"
    expected_file = Path(__file__).parent / "fixtures" / "test_formatting.json"

    with open(facet_file, "r", encoding="utf-8") as f:
        facet_content = f.read()

    json_output = parser.to_json(facet_content)

    # Parse and check structure
    parsed = json.loads(json_output)

    # Load expected result
    with open(expected_file, "r", encoding="utf-8") as f:
        expected = json.load(f)

    assert parsed == expected

    # Verify key order is preserved (implementation detail)
    system_keys = list(parsed["system"].keys())
    expected_order = ["role", "constraints"]
    assert system_keys == expected_order


def test_extended_scalars():
    """Test extended scalar types in golden output."""
    facet_file = Path(__file__).parent / "fixtures" / "test_extended_scalars.facet"
    expected_file = Path(__file__).parent / "fixtures" / "test_extended_scalars.json"

    with open(facet_file, "r", encoding="utf-8") as f:
        facet_content = f.read()

    json_output = parser.to_json(facet_content)
    parsed = json.loads(json_output)

    # Load expected result
    with open(expected_file, "r", encoding="utf-8") as f:
        expected = json.load(f)

    assert parsed == expected

    # Verify extended scalars are serialized as objects with _type
    assert isinstance(parsed["meta"]["timestamp"], dict)
    assert parsed["meta"]["timestamp"]["_type"] == "timestamp"
    assert isinstance(parsed["meta"]["duration"], dict)
    assert parsed["meta"]["duration"]["_type"] == "duration"
    assert isinstance(parsed["meta"]["size"], dict)
    assert parsed["meta"]["size"]["_type"] == "size"
    assert isinstance(parsed["meta"]["pattern"], dict)
    assert parsed["meta"]["pattern"]["_type"] == "regex"


def test_lenses_applied():
    """Test that lenses are applied and their results are in the output."""
    facet_file = Path(__file__).parent / "fixtures" / "test_lenses.facet"
    expected_file = Path(__file__).parent / "fixtures" / "test_lenses.json"

    with open(facet_file, "r", encoding="utf-8") as f:
        facet_content = f.read()

    json_output = parser.to_json(facet_content)
    parsed = json.loads(json_output)

    # Load expected result
    with open(expected_file, "r", encoding="utf-8") as f:
        expected = json.load(f)

    assert parsed == expected


def test_anchors_and_aliases():
    """Test anchor/alias resolution in golden output."""
    facet_file = Path(__file__).parent / "fixtures" / "test_anchors.facet"
    expected_file = Path(__file__).parent / "fixtures" / "test_anchors.json"

    with open(facet_file, "r", encoding="utf-8") as f:
        facet_content = f.read()

    json_output = parser.to_json(facet_content)
    parsed = json.loads(json_output)

    # Load expected result
    with open(expected_file, "r", encoding="utf-8") as f:
        expected = json.load(f)

    assert parsed == expected

    # Verify no anchor artifacts remain
    assert "&polite" not in json_output
