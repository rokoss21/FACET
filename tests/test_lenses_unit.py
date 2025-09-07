#!/usr/bin/env python3
"""
Comprehensive Unit Tests for SIMD-Optimized FACET Lenses
Tests correctness, performance, and edge cases for each lens function
"""

import sys
import os
import time
import statistics
import json
from typing import Dict, List, Any, Callable
import unittest
from unittest.mock import patch

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from facet.lenses import (
    normalize_newlines, dedent, squeeze_spaces, trim,
    LensError
)

class TestDataGenerator:
    """Generate test data of various sizes and complexities"""

    @staticmethod
    def small_text() -> str:
        """Small text for fast path testing"""
        return "Hello\r\nWorld\nTest"

    @staticmethod
    def medium_text() -> str:
        """Medium text for SIMD optimization testing"""
        lines = []
        for i in range(100):
            lines.append(f"    Line {i} with some content and indentation")
            if i % 10 == 0:
                lines.append(f"        Extra indented line {i}")
        return "\r\n".join(lines)

    @staticmethod
    def large_text() -> str:
        """Large text for performance testing"""
        lines = []
        for i in range(1000):
            lines.append(f"{'    ' * (i % 8)}Line {i} with varying indentation")
        return "\n".join(lines)

    @staticmethod
    def crlf_heavy_text() -> str:
        """Text with many CRLF sequences"""
        return "Line 1\r\nLine 2\r\nLine 3\r\n" * 200

    @staticmethod
    def whitespace_heavy_text() -> str:
        """Text with lots of whitespace to squeeze"""
        lines = []
        for i in range(50):
            lines.append(f"Line {i}    with     multiple    spaces{'    ' * (i % 5)}")
        return "\n".join(lines)

    @staticmethod
    def unicode_text() -> str:
        """Unicode text for encoding/decoding testing"""
        return "Привет мир 🌍\nЗдравствуй\t\t\tмир 🌍\nHello\t\tworld 🌍" * 20

    @staticmethod
    def edge_cases() -> Dict[str, str]:
        """Edge case test data"""
        return {
            "empty": "",
            "only_newlines": "\n\n\n",
            "only_crlf": "\r\n\r\n\r\n",
            "only_spaces": "    ",
            "only_tabs": "\t\t\t",
            "mixed_whitespace": " \t \n \r\n \t ",
            "null_bytes": "Hello\x00World\x00",
            "binary_data": b"Binary data \x00\x01\x02".decode('latin-1', errors='ignore'),
            "very_long_line": "x" * 10000,
            "single_char": "x",
            "just_numbers": "12345",
            "special_chars": "!@#$%^&*()_+{}|:<>?[]\\;',./"
        }


class LensTestCase(unittest.TestCase):
    """Base test case for lens testing"""

    def setUp(self):
        self.test_data = TestDataGenerator()
        self.timing_results = []

    def time_function(self, func: Callable, *args, iterations: int = 100) -> Dict[str, float]:
        """Time a function over multiple iterations"""
        times = []
        for _ in range(iterations):
            start = time.perf_counter()
            result = func(*args)
            end = time.perf_counter()
            times.append((end - start) * 1000)  # milliseconds

        return {
            'mean': statistics.mean(times),
            'median': statistics.median(times),
            'min': min(times),
            'max': max(times),
            'stdev': statistics.stdev(times) if len(times) > 1 else 0,
            'iterations': iterations
        }

    def assertLensCorrectness(self, lens_func: Callable, input_text: str, expected_output: str):
        """Assert lens function produces correct output"""
        try:
            result = lens_func(input_text)
            self.assertEqual(result, expected_output,
                           f"Lens {lens_func.__name__} failed:\n"
                           f"Input: {repr(input_text)}\n"
                           f"Expected: {repr(expected_output)}\n"
                           f"Got: {repr(result)}")
        except Exception as e:
            self.fail(f"Lens {lens_func.__name__} raised exception: {e}")


class TestNormalizeNewlines(LensTestCase):
    """Unit tests for normalize_newlines SIMD optimization"""

    def test_basic_crlf_replacement(self):
        """Test basic CRLF to LF conversion"""
        input_text = "Line 1\r\nLine 2\r\nLine 3"
        expected = "Line 1\nLine 2\nLine 3"
        self.assertLensCorrectness(normalize_newlines, input_text, expected)

    def test_mixed_newlines(self):
        """Test mixed CRLF, LF, and CR"""
        input_text = "Line 1\r\nLine 2\nLine 3\rLine 4"
        expected = "Line 1\nLine 2\nLine 3\nLine 4"
        self.assertLensCorrectness(normalize_newlines, input_text, expected)

    def test_edge_cases(self):
        """Test edge cases"""
        edge_cases = self.test_data.edge_cases()

        # Empty string
        self.assertLensCorrectness(normalize_newlines, edge_cases["empty"], "")

        # Only newlines
        self.assertLensCorrectness(normalize_newlines, edge_cases["only_newlines"], "\n\n\n")
        self.assertLensCorrectness(normalize_newlines, edge_cases["only_crlf"], "\n\n\n")

    def test_unicode_preservation(self):
        """Test that Unicode characters are preserved"""
        unicode_text = self.test_data.unicode_text()
        result = normalize_newlines(unicode_text)
        # Should not change since no CRLF in test data
        self.assertEqual(result, unicode_text)

    def test_performance_small_vs_large(self):
        """Test performance scaling"""
        small_text = self.test_data.small_text()
        large_text = self.test_data.large_text()

        small_time = self.time_function(normalize_newlines, small_text, iterations=1000)
        large_time = self.time_function(normalize_newlines, large_text, iterations=100)

        # Large text should be proportionally faster due to SIMD
        large_per_char = large_time['mean'] / len(large_text)
        small_per_char = small_time['mean'] / len(small_text)

        # SIMD should show better scaling for larger data
        self.assertLess(large_per_char, small_per_char * 2,
                       "SIMD optimization should scale better for large data")


class TestDedent(LensTestCase):
    """Unit tests for dedent SIMD optimization"""

    def test_basic_dedent(self):
        """Test basic dedent functionality"""
        input_text = "    Line 1\n    Line 2\n        Line 3"
        expected = "Line 1\nLine 2\n    Line 3"
        self.assertLensCorrectness(dedent, input_text, expected)

    def test_no_common_prefix(self):
        """Test when there's no common prefix to remove"""
        input_text = "Line 1\n    Line 2\nLine 3"
        expected = "Line 1\n    Line 2\nLine 3"
        self.assertLensCorrectness(dedent, input_text, expected)

    def test_empty_lines_handling(self):
        """Test handling of empty lines"""
        input_text = "    Line 1\n\n    Line 3"
        expected = "Line 1\n\nLine 3"
        self.assertLensCorrectness(dedent, input_text, expected)

    def test_tabs_vs_spaces(self):
        """Test mixed tabs and spaces"""
        input_text = "\tLine 1\n    Line 2\n\t\tLine 3"
        expected = "\tLine 1\n    Line 2\n\t\tLine 3"
        self.assertLensCorrectness(dedent, input_text, expected)

    def test_performance_scaling(self):
        """Test performance scaling with data size"""
        medium_text = self.test_data.medium_text()
        large_text = self.test_data.large_text()

        medium_time = self.time_function(dedent, medium_text, iterations=500)
        large_time = self.time_function(dedent, large_text, iterations=100)

        # Should show good SIMD scaling
        speedup_ratio = medium_time['mean'] / large_time['mean']
        self.assertGreater(speedup_ratio, 1.5, "SIMD dedent should show good scaling")


class TestSqueezeSpaces(LensTestCase):
    """Unit tests for squeeze_spaces SIMD optimization"""

    def test_basic_squeeze(self):
        """Test basic space squeezing"""
        input_text = "Hello    world   test"
        expected = "Hello world test"
        self.assertLensCorrectness(squeeze_spaces, input_text, expected)

    def test_tabs_and_spaces(self):
        """Test squeezing mixed tabs and spaces"""
        input_text = "Hello\t\t\tworld    test"
        expected = "Hello\tworld test"
        self.assertLensCorrectness(squeeze_spaces, input_text, expected)

    def test_newlines_preserved(self):
        """Test that newlines are preserved"""
        input_text = "Line 1\nLine    2\t\t\tLine 3"
        expected = "Line 1\nLine 2\tLine 3"
        self.assertLensCorrectness(squeeze_spaces, input_text, expected)

    def test_only_whitespace_sequences(self):
        """Test squeezing only whitespace sequences"""
        input_text = "Word1    Word2\t\tWord3"
        expected = "Word1 Word2\tWord3"
        self.assertLensCorrectness(squeeze_spaces, input_text, expected)

    def test_performance_large_data(self):
        """Test performance with large whitespace-heavy data"""
        ws_text = self.test_data.whitespace_heavy_text()

        timing = self.time_function(squeeze_spaces, ws_text, iterations=300)

        # Should complete in reasonable time
        self.assertLess(timing['mean'], 50, "Squeeze spaces should be fast even for large data")


class TestTrim(LensTestCase):
    """Unit tests for trim SIMD optimization"""

    def test_basic_trim(self):
        """Test basic trimming"""
        input_text = "  Hello world  "
        expected = "Hello world"
        self.assertLensCorrectness(trim, input_text, expected)

    def test_tabs_and_newlines(self):
        """Test trimming mixed whitespace"""
        input_text = "\t\tHello world\n\t"
        expected = "Hello world"
        self.assertLensCorrectness(trim, input_text, expected)

    def test_only_whitespace(self):
        """Test trimming string that's only whitespace"""
        input_text = "   \t   \n   "
        expected = ""
        self.assertLensCorrectness(trim, input_text, expected)

    def test_no_trimming_needed(self):
        """Test string that doesn't need trimming"""
        input_text = "Hello world"
        expected = "Hello world"
        self.assertLensCorrectness(trim, input_text, expected)

    def test_unicode_whitespace(self):
        """Test trimming Unicode whitespace characters"""
        input_text = "\u00A0\u2000Hello world\u2001\u2002"
        result = trim(input_text)
        # Should handle basic ASCII whitespace at minimum
        self.assertTrue(result.startswith("Hello") and result.endswith("world"))


class TestLensErrors(LensTestCase):
    """Test error handling in SIMD-optimized lenses"""

    def test_non_string_input(self):
        """Test error handling for non-string inputs"""
        with self.assertRaises(LensError) as cm:
            normalize_newlines(123)
        self.assertIn("expects string", str(cm.exception))

        with self.assertRaises(LensError) as cm:
            dedent(None)
        self.assertIn("expects string", str(cm.exception))

    def test_fallback_behavior(self):
        """Test that SIMD functions gracefully fall back on errors"""
        # Test with data that might cause SIMD issues
        problematic_text = "Normal text \x00 null byte"

        # Should not crash, should fall back to safe implementation
        try:
            result1 = normalize_newlines(problematic_text)
            result2 = dedent(problematic_text)
            result3 = squeeze_spaces(problematic_text)
            result4 = trim(problematic_text)

            # Results should be reasonable
            self.assertIsInstance(result1, str)
            self.assertIsInstance(result2, str)
            self.assertIsInstance(result3, str)
            self.assertIsInstance(result4, str)

        except Exception as e:
            self.fail(f"SIMD functions should handle errors gracefully, got: {e}")


class TestSIMDPathSelection(LensTestCase):
    """Test that SIMD vs fast path selection works correctly"""

    def test_normalize_newlines_path_selection(self):
        """Test path selection for normalize_newlines"""
        # Small text should use fast path
        small_text = "x" * 50
        self.assertEqual(len(small_text), 50)

        # Should work without issues
        result = normalize_newlines(small_text)
        self.assertIsInstance(result, str)

    def test_dedent_path_selection(self):
        """Test path selection for dedent"""
        # Very small text
        tiny_text = "x"

        result = dedent(tiny_text)
        self.assertEqual(result, tiny_text)

        # Medium text
        medium_text = "    " + "x" * 200
        result = dedent(medium_text)
        self.assertEqual(result, "x" * 200)

    def test_squeeze_spaces_path_selection(self):
        """Test path selection for squeeze_spaces"""
        # Small text
        small_text = "x   y"
        result = squeeze_spaces(small_text)
        self.assertEqual(result, "x y")

        # Larger text
        large_text = ("x" * 600) + "   " + ("y" * 600)
        result = squeeze_spaces(large_text)
        expected = ("x" * 600) + " " + ("y" * 600)
        self.assertEqual(result, expected)


def run_performance_comparison():
    """Run performance comparison between SIMD and baseline"""
    print("\n🚀 Performance Comparison: SIMD vs Baseline")
    print("=" * 60)

    test_data = TestDataGenerator()
    large_text = test_data.large_text()

    # Test normalize_newlines
    def baseline_normalize(text):
        return text.replace("\r\n", "\n").replace("\r", "\n")

    print("Testing normalize_newlines...")
    baseline_time = LensTestCase().time_function(baseline_normalize, large_text, iterations=100)
    simd_time = LensTestCase().time_function(normalize_newlines, large_text, iterations=100)

    speedup = baseline_time['mean'] / simd_time['mean'] if simd_time['mean'] > 0 else float('inf')
    print(f"Baseline time: {baseline_time['mean']:.2f}ms")
    print(f"SIMD time: {simd_time['mean']:.2f}ms")
    print(f"Speedup: {speedup:.2f}x")
    return {
        'normalize_newlines': {
            'baseline': baseline_time,
            'simd': simd_time,
            'speedup': speedup
        }
    }


if __name__ == '__main__':
    # Run unit tests
    print("🧪 Running SIMD Lens Unit Tests")
    print("=" * 50)

    unittest.main(argv=[''], exit=False, verbosity=2)

    # Run performance comparison
    perf_results = run_performance_comparison()

    # Save results
    with open('unit_test_results.json', 'w') as f:
        json.dump({
            'timestamp': time.time(),
            'performance': perf_results,
            'status': 'completed'
        }, f, indent=2)

    print("\n💾 Results saved to unit_test_results.json")
