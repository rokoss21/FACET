#!/usr/bin/env python3
"""
Integration Tests for FACET Parser with SIMD Optimizations
Tests end-to-end functionality and complex scenarios
"""

import sys
import os
import time
import json
import glob
from typing import Dict, List, Any, Optional
import unittest

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from facet.parser import parse_facet, FACETError
from facet.lenses import normalize_newlines, dedent, squeeze_spaces, trim


class FACETIntegrationTestCase(unittest.TestCase):
    """Base class for FACET integration tests"""

    def setUp(self):
        self.test_files_dir = "test_facet_files"
        os.makedirs(self.test_files_dir, exist_ok=True)
        self.performance_results = []

    def tearDown(self):
        # Clean up test files
        for f in glob.glob(f"{self.test_files_dir}/*.facet"):
            os.remove(f)
        if os.path.exists(self.test_files_dir):
            os.rmdir(self.test_files_dir)

    def create_test_facet_file(self, content: str, filename: str) -> str:
        """Create a test FACET file and return its path"""
        filepath = os.path.join(self.test_files_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return filepath

    def parse_facet_file(self, filepath: str) -> Dict[str, Any]:
        """Parse FACET file and return result"""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        return parse_facet(content)

    def time_parsing(self, facet_content: str, iterations: int = 100) -> Dict[str, float]:
        """Time FACET parsing over multiple iterations"""
        times = []
        for _ in range(iterations):
            start = time.perf_counter()
            result = parse_facet(facet_content)
            end = time.perf_counter()
            times.append((end - start) * 1000)  # milliseconds

        import statistics
        return {
            'mean': statistics.mean(times),
            'median': statistics.median(times),
            'min': min(times),
            'max': max(times),
            'stdev': statistics.stdev(times) if len(times) > 1 else 0
        }


class TestBasicFacetIntegration(FACETIntegrationTestCase):
    """Test basic FACET parsing with SIMD lenses"""

    def test_simple_facet_with_lenses(self):
        """Test simple FACET file with SIMD lenses"""
        facet_content = '''@user
  text: "Hello   world   with   spaces"
    |> squeeze_spaces

@output
  schema:
    type: "object"
'''

        result = parse_facet(facet_content)

        # Verify structure
        self.assertIn('user', result)
        self.assertIn('output', result)

        # Verify SIMD squeeze_spaces worked
        self.assertEqual(result['user']['text'], "Hello world with spaces")

    def test_multiple_lenses_chain(self):
        """Test chaining multiple SIMD lenses"""
        facet_content = '''@user
  text: """
      This is indented text
      with   multiple   spaces
      and CRLF line endings
  """
    |> dedent |> squeeze_spaces |> trim

@output
  schema:
    type: "object"
'''

        result = parse_facet(facet_content)

        # Verify all lenses worked in sequence
        expected = "This is indented text\nwith multiple spaces\nand CRLF line endings"
        self.assertEqual(result['user']['text'], expected)

    def test_normalize_newlines_integration(self):
        """Test normalize_newlines in FACET context"""
        facet_content = '''@user
  text: "Line 1\\r\\nLine 2\\r\\nLine 3"
    |> normalize_newlines

@output
  schema:
    type: "object"
'''

        result = parse_facet(facet_content)

        # Should convert CRLF to LF
        self.assertEqual(result['user']['text'], "Line 1\nLine 2\nLine 3")


class TestComplexFacetIntegration(FACETIntegrationTestCase):
    """Test complex FACET files with multiple facets and advanced features"""

    def test_multi_facet_document(self):
        """Test document with multiple facets using SIMD lenses"""
        facet_content = '''@system(role="Test")
  description: "Complex FACET test"
  features:
    - "SIMD optimizations"
    - "Multiple lenses"

@user
  input_data: """
    Raw input with    extra spaces
    and    indentation issues
  """
    |> dedent |> squeeze_spaces

@assistant
  response_template: "Processing: {input_data}"
    |> trim

@output
  format: "json"
  schema:
    type: "object"
    required: ["result"]
'''

        result = parse_facet(facet_content)

        # Verify all facets parsed correctly
        self.assertIn('system', result)
        self.assertIn('user', result)
        self.assertIn('assistant', result)
        self.assertIn('output', result)

        # Verify SIMD lenses worked
        expected_input = "Raw input with extra spaces\nand indentation issues"
        self.assertEqual(result['user']['input_data'], expected_input)

        # Verify template processing
        self.assertEqual(result['assistant']['response_template'], "Processing: {input_data}")

    def test_nested_structures_with_lenses(self):
        """Test nested structures with SIMD lenses"""
        facet_content = '''@config
  database:
    host: "localhost"
    credentials:
      username: "   admin   "
      password: "   secret   "
        |> trim
  cache:
    ttl: 3600
    servers:
      - "server1:11211"
      - "   server2:11211   "
        |> trim

@output
  schema:
    type: "object"
'''

        result = parse_facet(facet_content)

        # Verify nested structure preserved
        self.assertEqual(result['config']['database']['credentials']['username'], "admin")
        self.assertEqual(result['config']['database']['credentials']['password'], "secret")
        self.assertEqual(result['config']['cache']['servers'][1], "server2:11211")


class TestPerformanceIntegration(FACETIntegrationTestCase):
    """Test performance of FACET parsing with SIMD optimizations"""

    def test_large_facet_performance(self):
        """Test performance with large FACET documents"""
        # Generate large FACET content
        large_content = '''@data
  items:'''

        for i in range(100):
            large_content += f'''
    - "Item {i} with    multiple spaces and indentation"
        |> squeeze_spaces'''

        large_content += '''

@output
  schema:
    type: "object"
'''

        # Time parsing
        timing = self.time_parsing(large_content, iterations=50)

        # Should complete in reasonable time
        self.assertLess(timing['mean'], 200, "Large FACET parsing should be reasonably fast")

        # Parse and verify
        result = parse_facet(large_content)

        # Verify SIMD lenses worked on all items
        self.assertEqual(len(result['data']['items']), 100)
        for i, item in enumerate(result['data']['items']):
            expected = f"Item {i} with multiple spaces and indentation"
            self.assertEqual(item, expected)

    def test_memory_efficiency(self):
        """Test memory efficiency with large documents"""
        import psutil
        import os

        # Generate very large content
        large_content = '''@content
  text: """'''

        # Add large text with lots of whitespace to optimize
        for i in range(1000):
            large_content += f'''
    Line {i} with    lots    of    spaces    and    indentation{'    ' * (i % 10)}'''

        large_content += '''"""
    |> squeeze_spaces

@output
  schema:
    type: "object"
'''

        # Get memory before
        process = psutil.Process(os.getpid())
        mem_before = process.memory_info().rss / 1024 / 1024  # MB

        # Parse large content
        result = parse_facet(large_content)

        # Get memory after
        mem_after = process.memory_info().rss / 1024 / 1024  # MB

        # Memory increase should be reasonable
        mem_increase = mem_after - mem_before
        self.assertLess(mem_increase, 100, "Memory usage should be reasonable")

        # Verify SIMD optimization worked
        self.assertIsInstance(result['content']['text'], str)
        self.assertGreater(len(result['content']['text']), 10000)


class TestEdgeCasesIntegration(FACETIntegrationTestCase):
    """Test edge cases and error handling in FACET parsing"""

    def test_empty_facets(self):
        """Test handling of empty or minimal facets"""
        facet_content = '''@system

@user
  data: ""

@output
  schema:
    type: "object"
'''

        result = parse_facet(facet_content)
        self.assertEqual(result['user']['data'], "")

    def test_unicode_handling(self):
        """Test Unicode handling in FACET documents"""
        facet_content = '''@user
  text: "Привет мир 🌍 Hello world"
    |> trim

@output
  schema:
    type: "object"
'''

        result = parse_facet(facet_content)

        # Unicode should be preserved
        self.assertEqual(result['user']['text'], "Привет мир 🌍 Hello world")

    def test_binary_data_handling(self):
        """Test handling of binary-like data"""
        # Create content that might cause issues
        facet_content = '''@user
  data: "Data with null \\x00 and special chars"
    |> trim

@output
  schema:
    type: "object"
'''

        # Should handle gracefully
        result = parse_facet(facet_content)
        self.assertIsInstance(result['user']['data'], str)

    def test_lens_error_handling(self):
        """Test error handling when SIMD lenses fail"""
        facet_content = '''@user
  data: 123  # Not a string
    |> trim

@output
  schema:
    type: "object"
'''

        # Should handle lens errors gracefully
        with self.assertRaises(FACETError):
            parse_facet(facet_content)


class TestFacetFileIntegration(FACETIntegrationTestCase):
    """Test integration with actual FACET files from examples"""

    def test_example_files_parsing(self):
        """Test parsing of example FACET files"""
        example_files = glob.glob("examples/*.facet")

        for filepath in example_files[:3]:  # Test first 3 files
            with self.subTest(filepath=filepath):
                try:
                    result = self.parse_facet_file(filepath)
                    self.assertIsInstance(result, dict)
                    self.assertGreater(len(result), 0)

                except Exception as e:
                    self.fail(f"Failed to parse {filepath}: {e}")

    def test_ai_prompt_example(self):
        """Test specific AI prompt example with SIMD lenses"""
        facet_content = '''@system(role="Code Reviewer", version=1)
  style: "Thorough, constructive"
  constraints:
    - "Use markdown formatting"
    - "Focus on maintainability"

@user
  task: "Review this Python function"
  code: """
def factorial(n):
    if n <= 1:
        return n
    return factorial(n-1) * n
  """
    |> dedent |> trim

@output(format="json")
  schema:
    type: "object"
    required: ["issues", "rating"]
'''

        result = parse_facet(facet_content)

        # Verify structure
        self.assertIn('system', result)
        self.assertIn('user', result)
        self.assertIn('output', result)

        # Verify SIMD lenses worked on code
        expected_code = '''def factorial(n):
    if n <= 1:
        return n
    return factorial(n-1) * n
'''
        self.assertEqual(result['user']['code'], expected_code.strip())


def run_integration_performance_test():
    """Run performance test for integration scenarios"""
    print("\n🚀 FACET Integration Performance Test")
    print("=" * 50)

    test_case = FACETIntegrationTestCase()

    # Test 1: Simple document
    simple_content = '''@user
  text: "Hello world"
    |> trim

@output
  schema:
    type: "object"
'''

    timing = test_case.time_parsing(simple_content, iterations=1000)
    print(f"Simple document parsing: {timing['mean']:.2f}ms")
    # Test 2: Complex document
    complex_content = '''@system
  description: "Complex test"
  features:
    - "Feature 1"
    - "Feature 2"

@user
  data: "Complex   data   with   spaces"
    |> squeeze_spaces

@output
  schema:
    type: "object"
    properties:
      result:
        type: "string"
'''

    timing = test_case.time_parsing(complex_content, iterations=500)
    print(f"Simple document parsing: {timing['mean']:.2f}ms")
    return {
        'simple': timing,
        'complex': timing
    }


if __name__ == '__main__':
    print("🧪 Running FACET Integration Tests")
    print("=" * 50)

    # Run unit tests
    unittest.main(argv=[''], exit=False, verbosity=2)

    # Run performance tests
    perf_results = run_integration_performance_test()

    # Save results
    with open('integration_test_results.json', 'w') as f:
        json.dump({
            'timestamp': time.time(),
            'performance': perf_results,
            'status': 'completed'
        }, f, indent=2)

    print("\n💾 Results saved to integration_test_results.json")
