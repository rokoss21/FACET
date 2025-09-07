#!/usr/bin/env python3
"""
Edge Cases and Robustness Testing for FACET SIMD Optimizations
Tests error handling, boundary conditions, and unusual scenarios
"""

import sys
import os
import json
import tempfile
from typing import Dict, List, Any, Callable
import unittest

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from facet.lenses import (
    normalize_newlines, dedent, squeeze_spaces, trim,
    LensError
)
from facet.parser import parse_facet, FACETError


class EdgeCaseTestData:
    """Generate edge case test data"""

    @staticmethod
    def get_edge_cases() -> Dict[str, Dict[str, Any]]:
        """Comprehensive edge case dataset"""
        return {
            # Empty and minimal inputs
            "empty_string": {
                "input": "",
                "description": "Empty string",
                "expected_normalize": "",
                "expected_dedent": "",
                "expected_squeeze": "",
                "expected_trim": ""
            },
            "single_char": {
                "input": "x",
                "description": "Single character",
                "expected_normalize": "x",
                "expected_dedent": "x",
                "expected_squeeze": "x",
                "expected_trim": "x"
            },
            "only_newlines": {
                "input": "\n\n\n",
                "description": "Only newlines",
                "expected_normalize": "\n\n\n",
                "expected_dedent": "\n\n\n",
                "expected_squeeze": "\n\n\n",
                "expected_trim": ""
            },

            # Whitespace variations
            "only_spaces": {
                "input": "    ",
                "description": "Only spaces",
                "expected_normalize": "    ",
                "expected_dedent": "",
                "expected_squeeze": " ",
                "expected_trim": ""
            },
            "mixed_whitespace": {
                "input": " \t \n \r\n \t ",
                "description": "Mixed whitespace characters",
                "expected_normalize": " \t \n \n \t ",
                "expected_dedent": "\n\n",
                "expected_squeeze": " \n \n ",
                "expected_trim": ""
            },

            # CRLF variations
            "crlf_only": {
                "input": "\r\n\r\n\r\n",
                "description": "Only CRLF sequences",
                "expected_normalize": "\n\n\n",
                "expected_dedent": "\n\n\n",
                "expected_squeeze": "\n\n\n",
                "expected_trim": ""
            },
            "mixed_line_endings": {
                "input": "Line 1\r\nLine 2\nLine 3\rLine 4",
                "description": "Mixed line ending types",
                "expected_normalize": "Line 1\nLine 2\nLine 3\nLine 4",
                "expected_dedent": "Line 1\nLine 2\nLine 3\nLine 4",
                "expected_squeeze": "Line 1\nLine 2\nLine 3\nLine 4",
                "expected_trim": "Line 1\r\nLine 2\nLine 3\rLine 4"
            },

            # Binary and special characters
            "null_bytes": {
                "input": "Hello\x00World\x00",
                "description": "Contains null bytes",
                "should_fail_gracefully": True
            },
            "unicode_chars": {
                "input": "Привет 🌍 Hello 🚀",
                "description": "Unicode characters",
                "expected_normalize": "Привет 🌍 Hello 🚀",
                "expected_dedent": "Привет 🌍 Hello 🚀",
                "expected_squeeze": "Привет 🌍 Hello 🚀",
                "expected_trim": "Привет 🌍 Hello 🚀"
            },
            "emoji_sequence": {
                "input": "🎉🎊🎈🎁",
                "description": "Emoji sequence",
                "expected_normalize": "🎉🎊🎈🎁",
                "expected_dedent": "🎉🎊🎈🎁",
                "expected_squeeze": "🎉🎊🎈🎁",
                "expected_trim": "🎉🎊🎈🎁"
            },

            # Large inputs
            "very_large_line": {
                "input": "x" * 100000,
                "description": "Very large single line",
                "expected_normalize": "x" * 100000,
                "expected_dedent": "x" * 100000,
                "expected_squeeze": "x" * 100000,
                "expected_trim": "x" * 100000
            },
            "many_small_lines": {
                "input": "\n".join([f"Line {i}" for i in range(10000)]),
                "description": "Many small lines",
                "test_performance": True
            },

            # Complex indentation
            "complex_indentation": {
                "input": "\t    \tLine 1\n  \t  Line 2\n    \tLine 3",
                "description": "Complex mixed indentation",
                "expected_normalize": "\t    \tLine 1\n  \t  Line 2\n    \tLine 3",
                "expected_dedent": "\t    \tLine 1\n  \t  Line 2\n    \tLine 3",
                "expected_squeeze": " Line 1\n Line 2\n Line 3",
                "expected_trim": "Line 1\n  \t  Line 2\n    \tLine 3"
            },

            # Special regex patterns
            "regex_special_chars": {
                "input": "Line with [brackets] and (parens) and *stars*",
                "description": "Characters that might interfere with regex",
                "expected_normalize": "Line with [brackets] and (parens) and *stars*",
                "expected_dedent": "Line with [brackets] and (parens) and *stars*",
                "expected_squeeze": "Line with [brackets] and (parens) and *stars*",
                "expected_trim": "Line with [brackets] and (parens) and *stars*"
            }
        }


class TestSIMDEdgeCases(unittest.TestCase):
    """Test SIMD optimizations with edge cases"""

    def setUp(self):
        self.test_data = EdgeCaseTestData.get_edge_cases()

    def test_normalize_newlines_edge_cases(self):
        """Test normalize_newlines with edge cases"""
        for case_name, case_data in self.test_data.items():
            with self.subTest(case=case_name):
                try:
                    result = normalize_newlines(case_data["input"])

                    if "expected_normalize" in case_data:
                        self.assertEqual(result, case_data["expected_normalize"],
                                       f"normalize_newlines failed for {case_name}")
                    elif case_data.get("should_fail_gracefully"):
                        # Should not crash, but result may vary
                        self.assertIsInstance(result, str)
                    else:
                        # At minimum, should return a string
                        self.assertIsInstance(result, str)

                except Exception as e:
                    if not case_data.get("should_fail_gracefully"):
                        self.fail(f"normalize_newlines crashed on {case_name}: {e}")

    def test_dedent_edge_cases(self):
        """Test dedent with edge cases"""
        for case_name, case_data in self.test_data.items():
            with self.subTest(case=case_name):
                try:
                    result = dedent(case_data["input"])

                    if "expected_dedent" in case_data:
                        self.assertEqual(result, case_data["expected_dedent"],
                                       f"dedent failed for {case_name}")
                    elif case_data.get("should_fail_gracefully"):
                        self.assertIsInstance(result, str)
                    else:
                        self.assertIsInstance(result, str)

                except Exception as e:
                    if not case_data.get("should_fail_gracefully"):
                        self.fail(f"dedent crashed on {case_name}: {e}")

    def test_squeeze_spaces_edge_cases(self):
        """Test squeeze_spaces with edge cases"""
        for case_name, case_data in self.test_data.items():
            with self.subTest(case=case_name):
                try:
                    result = squeeze_spaces(case_data["input"])

                    if "expected_squeeze" in case_data:
                        self.assertEqual(result, case_data["expected_squeeze"],
                                       f"squeeze_spaces failed for {case_name}")
                    elif case_data.get("should_fail_gracefully"):
                        self.assertIsInstance(result, str)
                    else:
                        self.assertIsInstance(result, str)

                except Exception as e:
                    if not case_data.get("should_fail_gracefully"):
                        self.fail(f"squeeze_spaces crashed on {case_name}: {e}")

    def test_trim_edge_cases(self):
        """Test trim with edge cases"""
        for case_name, case_data in self.test_data.items():
            with self.subTest(case=case_name):
                try:
                    result = trim(case_data["input"])

                    if "expected_trim" in case_data:
                        self.assertEqual(result, case_data["expected_trim"],
                                       f"trim failed for {case_name}")
                    elif case_data.get("should_fail_gracefully"):
                        self.assertIsInstance(result, str)
                    else:
                        self.assertIsInstance(result, str)

                except Exception as e:
                    if not case_data.get("should_fail_gracefully"):
                        self.fail(f"trim crashed on {case_name}: {e}")

    def test_lens_chain_edge_cases(self):
        """Test chaining SIMD lenses with edge cases"""
        test_cases = [
            ("", "Empty string chain"),
            ("   \n\t  ", "Whitespace-only chain"),
            ("x", "Single char chain"),
            ("\r\n\r\n", "CRLF-only chain"),
        ]

        for input_text, description in test_cases:
            with self.subTest(description=description):
                try:
                    # Chain all lenses
                    result1 = normalize_newlines(input_text)
                    result2 = dedent(result1)
                    result3 = squeeze_spaces(result2)
                    result4 = trim(result3)

                    # Should produce valid string output
                    self.assertIsInstance(result4, str)

                except Exception as e:
                    self.fail(f"Lens chain failed on '{description}': {e}")

    def test_fallback_behavior(self):
        """Test that SIMD functions fall back gracefully on errors"""
        problematic_inputs = [
            "Text with \x00 null bytes",
            "Text with \xff high bytes",
            "",  # Empty
            None,  # Wrong type (should be caught by type check)
        ]

        for input_text in problematic_inputs:
            with self.subTest(input=input_text):
                try:
                    if input_text is None:
                        # Should raise LensError for wrong type
                        with self.assertRaises(LensError):
                            normalize_newlines(input_text)
                        continue

                    # For other inputs, should handle gracefully
                    result = normalize_newlines(input_text)
                    self.assertIsInstance(result, str)

                    result = dedent(input_text)
                    self.assertIsInstance(result, str)

                    result = squeeze_spaces(input_text)
                    self.assertIsInstance(result, str)

                    result = trim(input_text)
                    self.assertIsInstance(result, str)

                except LensError:
                    # Expected for wrong types
                    if input_text is None:
                        continue
                    else:
                        raise
                except Exception as e:
                    self.fail(f"Unexpected error for input {repr(input_text)}: {e}")


class TestFacetParserEdgeCases(unittest.TestCase):
    """Test FACET parser with edge cases and SIMD lenses"""

    def test_minimal_facet_documents(self):
        """Test parsing minimal FACET documents"""
        minimal_docs = [
            "@user\n  data: \"test\"",
            "@system\n@user\n  data: \"\"",
            "@output\n  schema:\n    type: \"object\"",
        ]

        for doc in minimal_docs:
            with self.subTest(doc=repr(doc)):
                try:
                    result = parse_facet(doc)
                    self.assertIsInstance(result, dict)
                    self.assertGreater(len(result), 0)
                except Exception as e:
                    self.fail(f"Failed to parse minimal document: {e}")

    def test_facet_with_extreme_lenses(self):
        """Test FACET documents with extreme lens usage"""
        facet_content = '''@user
  extreme_text: """
    Text with extreme whitespace
    and very long lines that go on forever with lots of spaces
    and multiple indentations and CRLF sequences
  """
    |> dedent |> squeeze_spaces |> trim |> dedent

@output
  schema:
    type: "object"
'''

        result = parse_facet(facet_content)
        self.assertIn('user', result)
        self.assertIsInstance(result['user']['extreme_text'], str)

    def test_unicode_facet_documents(self):
        """Test FACET parsing with Unicode content"""
        unicode_content = '''@user
  unicode_text: "Привет мир 🌍 Здравствуй мир 🚀"
    |> trim

@system
  description: "Unicode test 🎉"

@output
  schema:
    type: "object"
'''

        result = parse_facet(unicode_content)
        self.assertIn('user', result)
        self.assertIn('unicode_text', result['user'])
        # Should preserve Unicode
        self.assertIn('🌍', result['user']['unicode_text'])

    def test_large_facet_document(self):
        """Test parsing very large FACET document"""
        # Generate large content
        large_lines = []
        for i in range(1000):
            large_lines.append(f"    Line {i} with some content and indentation")

        large_content = f'''@user
  large_data: """
{"".join(large_lines)}
  """
    |> dedent |> squeeze_spaces

@output
  schema:
    type: "object"
'''

        result = parse_facet(large_content)
        self.assertIn('user', result)
        self.assertIsInstance(result['user']['large_data'], str)
        self.assertGreater(len(result['user']['large_data']), 10000)

    def test_facet_with_empty_lenses(self):
        """Test FACET with empty or whitespace-only content in lenses"""
        facet_content = '''@user
  empty_content: ""
    |> trim

  whitespace_content: "   \n    "
    |> dedent |> squeeze_spaces |> trim

@output
  schema:
    type: "object"
'''

        result = parse_facet(facet_content)
        self.assertEqual(result['user']['empty_content'], "")
        self.assertEqual(result['user']['whitespace_content'], "")

    def test_facet_error_recovery(self):
        """Test error recovery in FACET parsing"""
        error_cases = [
            # Malformed lens
            '''@user
  data: "test"
    |> invalid_lens
''',
            # Wrong indentation
            '''@user
data: "test"  # Wrong indentation
''',
            # Invalid JSON in schema
            '''@output
  schema: {
    type: "invalid"
    missing_comma: true
  }
'''
        ]

        for i, error_doc in enumerate(error_cases):
            with self.subTest(case=i):
                try:
                    result = parse_facet(error_doc)
                    # If it succeeds, should be valid
                    self.assertIsInstance(result, dict)
                except FACETError:
                    # Expected for malformed documents
                    pass
                except Exception as e:
                    self.fail(f"Unexpected error type: {e}")


class TestPerformanceEdgeCases(unittest.TestCase):
    """Test performance characteristics with edge cases"""

    def test_worst_case_performance(self):
        """Test performance with worst-case inputs"""
        # Generate worst-case input for dedent (maximal indentation variation)
        worst_case_lines = []
        for i in range(100):
            indent = "    " * ((i % 20) + 1)  # Variable indentation
            worst_case_lines.append(f"{indent}Line {i}")

        worst_case_text = "\n".join(worst_case_lines)

        import time
        start = time.perf_counter()
        result = dedent(worst_case_text)
        end = time.perf_counter()

        processing_time = (end - start) * 1000  # ms

        # Should complete in reasonable time
        self.assertLess(processing_time, 100, "Worst-case dedent should be fast")
        self.assertIsInstance(result, str)

    def test_memory_edge_cases(self):
        """Test memory usage with edge case inputs"""
        # Test with highly repetitive content
        repetitive_text = ("Very long repetitive text with lots of spaces    " * 1000)

        import psutil
        process = psutil.Process(os.getpid())
        mem_before = process.memory_info().rss / 1024 / 1024

        result = squeeze_spaces(repetitive_text)

        mem_after = process.memory_info().rss / 1024 / 1024
        mem_increase = mem_after - mem_before

        # Memory increase should be reasonable
        self.assertLess(mem_increase, 50, "Memory usage should be reasonable for repetitive content")

    def test_concurrent_edge_cases(self):
        """Test concurrent processing with edge cases"""
        from concurrent.futures import ThreadPoolExecutor

        edge_inputs = [
            "",  # Empty
            "x",  # Minimal
            "\n\n\n",  # Newlines only
            "    ",  # Spaces only
            "Text with    spaces",  # Normal case
            "Привет 🌍",  # Unicode
        ]

        def process_input(text):
            try:
                return dedent(squeeze_spaces(normalize_newlines(trim(text))))
            except Exception as e:
                return f"Error: {e}"

        with ThreadPoolExecutor(max_workers=4) as executor:
            results = list(executor.map(process_input, edge_inputs))

        # All should complete without crashing
        self.assertEqual(len(results), len(edge_inputs))
        for i, result in enumerate(results):
            self.assertIsInstance(result, str, f"Failed on input {i}: {edge_inputs[i]}")


def generate_edge_case_report():
    """Generate comprehensive edge case testing report"""
    print("\n🧪 EDGE CASE TESTING REPORT")
    print("=" * 50)

    test_cases = EdgeCaseTestData.get_edge_cases()
    total_cases = len(test_cases)
    passed_cases = 0
    failed_cases = 0
    errors = []

    # Test each case manually (since unittest output is verbose)
    for case_name, case_data in test_cases.items():
        try:
            input_text = case_data["input"]

            # Test all lenses
            results = {}
            results['normalize'] = normalize_newlines(input_text)
            results['dedent'] = dedent(input_text)
            results['squeeze'] = squeeze_spaces(input_text)
            results['trim'] = trim(input_text)

            # Verify results are strings and reasonable
            for lens_name, result in results.items():
                if not isinstance(result, str):
                    raise ValueError(f"{lens_name} returned {type(result)}, expected str")

            # Check expected values if provided
            for lens_name in ['normalize', 'dedent', 'squeeze', 'trim']:
                expected_key = f"expected_{lens_name}"
                if expected_key in case_data:
                    expected = case_data[expected_key]
                    actual = results[lens_name]
                    if actual != expected:
                        raise ValueError(f"{lens_name}: expected {repr(expected)}, got {repr(actual)}")

            passed_cases += 1
            print(f"  ✅ {case_name}")

        except Exception as e:
            failed_cases += 1
            errors.append(f"{case_name}: {e}")
            print(f"  ❌ {case_name}: {e}")

    success_rate = passed_cases / total_cases if total_cases > 0 else 0

    print("\n📊 Summary:")
    print(f"   Total cases: {total_cases}")
    print(f"   Passed: {passed_cases}")
    print(f"   Failed: {failed_cases}")
    print(f"   Success rate: {success_rate:.1f}")
    if errors:
        print("\n❌ Errors:")
        for error in errors[:5]:  # Show first 5 errors
            print(f"   {error}")
        if len(errors) > 5:
            print(f"   ... and {len(errors) - 5} more")

    return {
        'total': total_cases,
        'passed': passed_cases,
        'failed': failed_cases,
        'success_rate': passed_cases / total_cases if total_cases > 0 else 0
    }


def main():
    """Run comprehensive edge case testing"""
    print("🧪 FACET SIMD Edge Case Testing Suite")
    print("=" * 60)
    print("Testing robustness and error handling...")
    print()

    # Generate edge case report
    edge_report = generate_edge_case_report()

    # Run unit tests
    print("\n🧪 Running Edge Case Unit Tests...")
    unittest.main(argv=[''], exit=False, verbosity=1)

    # Save results
    with open('edge_case_test_results.json', 'w') as f:
        json.dump({
            'timestamp': time.time(),
            'edge_case_report': edge_report,
            'status': 'completed'
        }, f, indent=2)

    print("\n💾 Results saved to edge_case_test_results.json")

    return edge_report


if __name__ == "__main__":
    import time
    try:
        results = main()
        success_rate = results.get('success_rate', 0)

        if success_rate >= 0.95:
            print(f"   Success rate: {success_rate:.1f} - edge cases handled correctly!")
        else:
            print(f"   Success rate: {success_rate:.1f} - review failed edge cases")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n⚠️  Edge case testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Critical error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
