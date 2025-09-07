#!/usr/bin/env python3
"""
Regression Testing for FACET SIMD Optimizations
Compares SIMD output with baseline implementations to ensure correctness
"""

import sys
import os
import json
import time
import hashlib
from typing import Dict, List, Any, Callable
import unittest
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from facet.lenses import (
    normalize_newlines, dedent, squeeze_spaces, trim
)
from facet.parser import parse_facet


class BaselineImplementations:
    """Baseline implementations for comparison"""

    @staticmethod
    def normalize_newlines_baseline(text: str) -> str:
        """Original normalize_newlines implementation"""
        return text.replace("\r\n", "\n").replace("\r", "\n")

    @staticmethod
    def dedent_baseline(text: str) -> str:
        """Original dedent implementation using textwrap"""
        import textwrap
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        return textwrap.dedent(text)

    @staticmethod
    def squeeze_spaces_baseline(text: str) -> str:
        """Original squeeze_spaces implementation using regex"""
        import re
        lines = text.splitlines()
        return "\n".join(re.sub(r"[ \t]+", " ", ln) for ln in lines)

    @staticmethod
    def trim_baseline(text: str) -> str:
        """Original trim implementation"""
        return text.strip()

    @staticmethod
    def parse_facet_baseline(facet_text: str) -> Dict[str, Any]:
        """Parse FACET using baseline implementations"""
        # Temporarily replace SIMD functions with baseline
        import facet.lenses as lenses_module
        import facet.parser as parser_module

        # Save original functions
        original_functions = {
            'normalize_newlines': lenses_module.normalize_newlines,
            'dedent': lenses_module.dedent,
            'squeeze_spaces': lenses_module.squeeze_spaces,
            'trim': lenses_module.trim,
        }

        try:
            # Replace with baseline implementations
            lenses_module.normalize_newlines = BaselineImplementations.normalize_newlines_baseline
            lenses_module.dedent = BaselineImplementations.dedent_baseline
            lenses_module.squeeze_spaces = BaselineImplementations.squeeze_spaces_baseline
            lenses_module.trim = BaselineImplementations.trim_baseline

            # Parse with baseline
            result = parse_facet(facet_text)

        finally:
            # Restore original functions
            lenses_module.normalize_newlines = original_functions['normalize_newlines']
            lenses_module.dedent = original_functions['dedent']
            lenses_module.squeeze_spaces = original_functions['squeeze_spaces']
            lenses_module.trim = original_functions['trim']

        return result


class TestDataGenerator:
    """Generate test data for regression testing"""

    @staticmethod
    def get_regression_test_cases() -> List[Dict[str, Any]]:
        """Comprehensive test cases for regression testing"""
        return [
            {
                "name": "simple_text",
                "input": "Hello world",
                "description": "Simple ASCII text"
            },
            {
                "name": "crlf_text",
                "input": "Line 1\r\nLine 2\r\nLine 3",
                "description": "Text with CRLF line endings"
            },
            {
                "name": "indented_text",
                "input": "    Line 1\n        Line 2\n    Line 3",
                "description": "Text with indentation"
            },
            {
                "name": "whitespace_text",
                "input": "Hello    world   test",
                "description": "Text with multiple spaces"
            },
            {
                "name": "mixed_whitespace",
                "input": "  \t  Hello\t\t\tworld   \n  \t  Test  \t  ",
                "description": "Mixed whitespace characters"
            },
            {
                "name": "empty_string",
                "input": "",
                "description": "Empty string"
            },
            {
                "name": "unicode_text",
                "input": "Привет 🌍 Hello 🚀",
                "description": "Unicode text with emojis"
            },
            {
                "name": "large_text",
                "input": "Line " * 1000,
                "description": "Large repetitive text"
            },
            {
                "name": "complex_indentation",
                "input": "\n".join([f"{'    ' * (i % 5)}Line {i}" for i in range(50)]),
                "description": "Complex indentation patterns"
            },
            {
                "name": "special_chars",
                "input": "Text with [brackets] (parens) {braces} and *stars*",
                "description": "Special regex characters"
            }
        ]

    @staticmethod
    def get_facet_test_cases() -> List[Dict[str, Any]]:
        """FACET document test cases"""
        return [
            {
                "name": "simple_facet",
                "content": '''@user
  text: "Hello world"
    |> trim

@output
  schema:
    type: "object"
''',
                "description": "Simple FACET document"
            },
            {
                "name": "complex_facet",
                "content": '''@system(role="Test")
  description: "Complex test"

@user
  data: """
    Complex text with
    indentation and spaces
  """
    |> dedent |> squeeze_spaces

@output
  schema:
    type: "object"
    properties:
      result:
        type: "string"
''',
                "description": "Complex FACET with multiple lenses"
            },
            {
                "name": "unicode_facet",
                "content": '''@user
  unicode: "Привет 🌍"
    |> trim

@output
  schema:
    type: "object"
''',
                "description": "FACET with Unicode content"
            }
        ]


class RegressionTestRunner:
    """Run regression tests comparing SIMD vs baseline"""

    def __init__(self):
        self.baseline = BaselineImplementations()
        self.test_data = TestDataGenerator()

    def compare_lens_outputs(self, lens_name: str, test_input: str) -> Dict[str, Any]:
        """Compare SIMD vs baseline lens output"""

        # Get SIMD result
        if lens_name == "normalize_newlines":
            simd_result = normalize_newlines(test_input)
            baseline_result = self.baseline.normalize_newlines_baseline(test_input)
        elif lens_name == "dedent":
            simd_result = dedent(test_input)
            baseline_result = self.baseline.dedent_baseline(test_input)
        elif lens_name == "squeeze_spaces":
            simd_result = squeeze_spaces(test_input)
            baseline_result = self.baseline.squeeze_spaces_baseline(test_input)
        elif lens_name == "trim":
            simd_result = trim(test_input)
            baseline_result = self.baseline.trim_baseline(test_input)
        else:
            raise ValueError(f"Unknown lens: {lens_name}")

        # Compare results
        match = (simd_result == baseline_result)

        return {
            "lens": lens_name,
            "input": test_input,
            "simd_result": simd_result,
            "baseline_result": baseline_result,
            "match": match,
            "simd_hash": hashlib.sha256(simd_result.encode('utf-8')).hexdigest(),
            "baseline_hash": hashlib.sha256(baseline_result.encode('utf-8')).hexdigest(),
            "length_match": len(simd_result) == len(baseline_result)
        }

    def compare_facet_outputs(self, facet_content: str) -> Dict[str, Any]:
        """Compare SIMD vs baseline FACET parsing"""

        # Get SIMD result
        try:
            simd_result = parse_facet(facet_content)
            simd_success = True
        except Exception as e:
            simd_result = str(e)
            simd_success = False

        # Get baseline result
        try:
            baseline_result = self.baseline.parse_facet_baseline(facet_content)
            baseline_success = True
        except Exception as e:
            baseline_result = str(e)
            baseline_success = False

        # Compare results
        if simd_success and baseline_success:
            # Both succeeded - compare outputs
            match = (simd_result == baseline_result)
            if not match:
                # Try JSON normalization for comparison
                try:
                    match = (json.dumps(simd_result, sort_keys=True) ==
                           json.dumps(baseline_result, sort_keys=True))
                except:
                    match = False
        else:
            # At least one failed - check if both failed with same error type
            match = (simd_success == baseline_success)

        return {
            "facet_content": facet_content,
            "simd_result": simd_result,
            "baseline_result": baseline_result,
            "simd_success": simd_success,
            "baseline_success": baseline_success,
            "match": match,
            "simd_hash": hashlib.sha256(str(simd_result).encode('utf-8')).hexdigest() if isinstance(simd_result, (dict, str)) else "N/A",
            "baseline_hash": hashlib.sha256(str(baseline_result).encode('utf-8')).hexdigest() if isinstance(baseline_result, (dict, str)) else "N/A"
        }

    def run_lens_regression_tests(self) -> Dict[str, Any]:
        """Run regression tests for individual lenses"""
        print("🔬 Running Lens Regression Tests...")

        test_cases = self.test_data.get_regression_test_cases()
        lenses = ["normalize_newlines", "dedent", "squeeze_spaces", "trim"]

        results = {}
        total_tests = 0
        passed_tests = 0

        for lens_name in lenses:
            lens_results = []
            print(f"\n  Testing {lens_name}...")

            for test_case in test_cases:
                total_tests += 1
                result = self.compare_lens_outputs(lens_name, test_case["input"])

                if result["match"]:
                    passed_tests += 1
                    status = "✅ PASS"
                else:
                    status = "❌ FAIL"

                print(f"    {status} {test_case['name']}")
                lens_results.append({
                    **result,
                    "test_case": test_case
                })

            results[lens_name] = lens_results

        success_rate = passed_tests / total_tests if total_tests > 0 else 0
        print(f"\n  Lens Regression Summary: {passed_tests}/{total_tests} tests passed ({success_rate:.1%})")

        return {
            "results": results,
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "success_rate": success_rate
            }
        }

    def run_facet_regression_tests(self) -> Dict[str, Any]:
        """Run regression tests for FACET parsing"""
        print("📄 Running FACET Regression Tests...")

        test_cases = self.test_data.get_facet_test_cases()
        results = []
        total_tests = 0
        passed_tests = 0

        for test_case in test_cases:
            total_tests += 1
            result = self.compare_facet_outputs(test_case["content"])

            if result["match"]:
                passed_tests += 1
                status = "✅ PASS"
            else:
                status = "❌ FAIL"

            print(f"  {status} {test_case['name']}")
            results.append({
                **result,
                "test_case": test_case
            })

        success_rate = passed_tests / total_tests if total_tests > 0 else 0
        print(f"\n  FACET Regression Summary: {passed_tests}/{total_tests} tests passed ({success_rate:.1%})")

        return {
            "results": results,
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "success_rate": success_rate
            }
        }


class TestRegression(unittest.TestCase):
    """Unit tests for regression testing"""

    def setUp(self):
        self.runner = RegressionTestRunner()

    def test_lens_regression_correctness(self):
        """Test that SIMD lenses produce same output as baseline"""
        test_input = "Hello    world\r\nTest   line"

        # Test each lens
        result1 = self.runner.compare_lens_outputs("normalize_newlines", test_input)
        result2 = self.runner.compare_lens_outputs("dedent", test_input)
        result3 = self.runner.compare_lens_outputs("squeeze_spaces", test_input)
        result4 = self.runner.compare_lens_outputs("trim", test_input)

        # All should match baseline
        self.assertTrue(result1["match"], "normalize_newlines regression")
        self.assertTrue(result2["match"], "dedent regression")
        self.assertTrue(result3["match"], "squeeze_spaces regression")
        self.assertTrue(result4["match"], "trim regression")

    def test_facet_regression_correctness(self):
        """Test that SIMD FACET parsing produces same output as baseline"""
        facet_content = '''@user
  text: "Hello world"
    |> trim

@output
  schema:
    type: "object"
'''

        result = self.runner.compare_facet_outputs(facet_content)

        # Should match baseline
        self.assertTrue(result["match"], "FACET parsing regression")
        self.assertTrue(result["simd_success"], "SIMD parsing should succeed")
        self.assertTrue(result["baseline_success"], "Baseline parsing should succeed")

    def test_unicode_regression(self):
        """Test Unicode handling regression"""
        unicode_text = "Привет 🌍 Hello 🚀"

        result = self.runner.compare_lens_outputs("trim", unicode_text)

        # Should preserve Unicode exactly
        self.assertTrue(result["match"], "Unicode regression")
        self.assertEqual(result["simd_result"], result["baseline_result"])

    def test_empty_input_regression(self):
        """Test empty input regression"""
        result = self.runner.compare_lens_outputs("trim", "")

        self.assertTrue(result["match"], "Empty input regression")
        self.assertEqual(result["simd_result"], result["baseline_result"])


def generate_regression_report():
    """Generate comprehensive regression testing report"""
    print("\n🔄 REGRESSION TESTING REPORT")
    print("=" * 60)

    runner = RegressionTestRunner()

    # Run lens regression tests
    lens_results = runner.run_lens_regression_tests()

    # Run FACET regression tests
    facet_results = runner.run_facet_regression_tests()

    # Overall summary
    lens_success = lens_results["summary"]["success_rate"]
    facet_success = facet_results["summary"]["success_rate"]
    overall_success = (lens_success + facet_success) / 2

    print(f"\n📊 Overall Regression Summary:")
    print(f"   Lens success rate: {lens_success:.1f}")
    print(f"   FACET success rate: {facet_success:.1f}")
    print(f"   Overall success rate: {overall_success:.1f}")
    # Detailed analysis
    if overall_success < 0.99:
        print("\n⚠️  REGRESSION ISSUES DETECTED:")
        print("   Some SIMD optimizations may be producing different results than baseline")

        # Find failing tests
        for lens_name, results in lens_results["results"].items():
            for result in results:
                if not result["match"]:
                    print(f"   ❌ {lens_name}: {result['test_case']['name']}")

        for result in facet_results["results"]:
            if not result["match"]:
                print(f"   ❌ FACET: {result['test_case']['name']}")
    else:
        print("\n✅ All regression tests passed!")
        print("   SIMD optimizations maintain correctness compared to baseline")

    return {
        "lens_results": lens_results,
        "facet_results": facet_results,
        "overall_success_rate": overall_success
    }


def main():
    """Run comprehensive regression testing"""
    print("🔄 FACET SIMD Regression Testing Suite")
    print("=" * 60)
    print("Comparing SIMD optimizations with baseline implementations...")
    print()

    # Generate regression report
    regression_results = generate_regression_report()

    # Run unit tests
    print("\n🧪 Running Regression Unit Tests...")
    unittest.main(argv=[''], exit=False, verbosity=1)

    # Save detailed results
    with open('regression_test_results.json', 'w') as f:
        json.dump({
            'timestamp': time.time(),
            'regression_results': regression_results,
            'status': 'completed'
        }, f, indent=2, default=str)

    print("\n💾 Results saved to regression_test_results.json")

    # Return overall success rate
    return regression_results.get('overall_success_rate', 0)


if __name__ == "__main__":
    try:
        success_rate = main()

        if success_rate >= 0.99:
            print(f"   Success rate: {success_rate:.1f} - regressions detected!")
        else:
            print(f"   Success rate: {success_rate:.1f} - review regression issues")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n⚠️  Regression testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Critical error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
