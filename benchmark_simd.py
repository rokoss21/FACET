#!/usr/bin/env python3
"""
SIMD Optimization Benchmark for FACET Lenses
Tests performance improvements from SIMD optimizations
"""

import time
import statistics
from typing import List, Callable, Any
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from facet.lenses import (
    normalize_newlines, dedent, squeeze_spaces, trim
)
import numpy as np

class BenchmarkRunner:
    def __init__(self, iterations: int = 1000):
        self.iterations = iterations

    def time_function(self, func: Callable, *args, **kwargs) -> List[float]:
        """Time a function over multiple iterations"""
        times = []
        for _ in range(self.iterations):
            start = time.perf_counter()
            result = func(*args, **kwargs)
            end = time.perf_counter()
            times.append((end - start) * 1000)  # Convert to milliseconds
        return times

    def compare_functions(self, name: str, func1: Callable, func2: Callable,
                         *args, **kwargs) -> dict:
        """Compare two functions performance"""
        print(f"\n🔬 Benchmarking: {name}")
        print("=" * 50)

        # Warm up functions
        for _ in range(10):
            func1(*args, **kwargs)
            func2(*args, **kwargs)

        times1 = self.time_function(func1, *args, **kwargs)
        times2 = self.time_function(func2, *args, **kwargs)

        stats1 = {
            'mean': statistics.mean(times1),
            'median': statistics.median(times1),
            'min': min(times1),
            'max': max(times1),
            'stdev': statistics.stdev(times1) if len(times1) > 1 else 0
        }

        stats2 = {
            'mean': statistics.mean(times2),
            'median': statistics.median(times2),
            'min': min(times2),
            'max': max(times2),
            'stdev': statistics.stdev(times2) if len(times2) > 1 else 0
        }

        speedup = stats1['mean'] / stats2['mean'] if stats2['mean'] > 0 else float('inf')

        print(f"Original:  {stats1['mean']:.2f}ms ±{stats1['stdev']:.2f}ms (min: {stats1['min']:.2f}ms, max: {stats1['max']:.2f}ms)")
        print(f"Optimized: {stats2['mean']:.2f}ms ±{stats2['stdev']:.2f}ms (min: {stats2['min']:.2f}ms, max: {stats2['max']:.2f}ms)")
        print(f"Speedup:   {speedup:.2f}x faster")
        return {
            'name': name,
            'original': stats1,
            'optimized': stats2,
            'speedup': speedup,
            'times_original': times1,
            'times_optimized': times2
        }

def generate_test_data():
    """Generate test data of various sizes"""
    # Small text (fast path)
    small_text = """Hello world
    This is a test
    With some content"""

    # Medium text (SIMD path)
    medium_text = "\r\n".join([f"    Line {i} with some content and spaces    " for i in range(100)])

    # Large text (SIMD optimization benefits)
    large_text = "\r\n".join([f"{'    ' * (i % 10)}Line {i} with varying indentation and multiple     spaces" for i in range(1000)])

    # CRLF heavy text (normalize_newlines test)
    crlf_text = "Line 1\r\nLine 2\r\nLine 3\r\n" * 500

    return {
        'small': small_text,
        'medium': medium_text,
        'large': large_text,
        'crlf': crlf_text
    }

def benchmark_normalize_newlines():
    """Benchmark normalize_newlines optimization"""
    test_data = generate_test_data()
    benchmark = BenchmarkRunner(iterations=500)

    results = []

    for size_name, text in test_data.items():
        print(f"\n📊 Testing normalize_newlines with {size_name} data ({len(text)} chars)")

        # Original implementation
        def original_normalize(text):
            return text.replace("\r\n", "\n").replace("\r", "\n")

        # Optimized implementation
        def optimized_normalize(text):
            return normalize_newlines(text)

        result = benchmark.compare_functions(
            f"normalize_newlines_{size_name}",
            original_normalize,
            optimized_normalize,
            text
        )
        results.append(result)

    return results

def benchmark_dedent():
    """Benchmark dedent optimization"""
    test_data = generate_test_data()
    benchmark = BenchmarkRunner(iterations=300)

    results = []

    for size_name, text in test_data.items():
        print(f"\n📊 Testing dedent with {size_name} data ({len(text)} chars)")

        # Original implementation (using textwrap)
        import textwrap
        def original_dedent(text):
            text = text.replace("\r\n", "\n").replace("\r", "\n")
            return textwrap.dedent(text)

        # Optimized implementation
        def optimized_dedent(text):
            return dedent(text)

        result = benchmark.compare_functions(
            f"dedent_{size_name}",
            original_dedent,
            optimized_dedent,
            text
        )
        results.append(result)

    return results

def benchmark_squeeze_spaces():
    """Benchmark squeeze_spaces optimization"""
    benchmark = BenchmarkRunner(iterations=300)

    # Generate text with lots of spaces to squeeze
    test_text = "\n".join([f"Line {i}    with     multiple    spaces{'    ' * (i % 5)}" for i in range(200)])

    print(f"\n📊 Testing squeeze_spaces with {len(test_text)} chars")

    # Original implementation
    import re
    def original_squeeze(text):
        lines = text.splitlines()
        return "\n".join(re.sub(r"[ \t]+", " ", ln) for ln in lines)

    # Optimized implementation
    def optimized_squeeze(text):
        return squeeze_spaces(text)

    result = benchmark.compare_functions(
        "squeeze_spaces",
        original_squeeze,
        optimized_squeeze,
        test_text
    )

    return [result]

def benchmark_trim():
    """Benchmark trim optimization"""
    benchmark = BenchmarkRunner(iterations=1000)

    # Generate text with leading/trailing whitespace
    test_text = f"{'    ' * 50}Content with lots of whitespace{'    ' * 50}"

    print(f"\n📊 Testing trim with {len(test_text)} chars")

    # Original implementation
    def original_trim(text):
        return text.strip()

    # Optimized implementation
    def optimized_trim(text):
        return trim(text)

    result = benchmark.compare_functions(
        "trim",
        original_trim,
        optimized_trim,
        test_text
    )

    return [result]

def run_full_benchmark():
    """Run complete benchmark suite"""
    print("🚀 FACET SIMD Optimization Benchmark Suite")
    print("=" * 60)
    print(f"Running {BenchmarkRunner().iterations} iterations per test")
    print()

    all_results = []

    # Run all benchmarks
    print("\n1️⃣ Testing normalize_newlines...")
    all_results.extend(benchmark_normalize_newlines())

    print("\n2️⃣ Testing dedent...")
    all_results.extend(benchmark_dedent())

    print("\n3️⃣ Testing squeeze_spaces...")
    all_results.extend(benchmark_squeeze_spaces())

    print("\n4️⃣ Testing trim...")
    all_results.extend(benchmark_trim())

    # Generate summary
    print("\n" + "=" * 60)
    print("📈 PERFORMANCE SUMMARY")
    print("=" * 60)

    total_speedup = 0
    count = 0

    for result in all_results:
        speedup = result['speedup']
        if speedup > 1:
            status = "✅ IMPROVED"
        elif speedup < 1:
            status = "❌ REGRESSED"
        else:
            status = "➖ SAME"

        print(f"{result['name']:<25} {speedup:>8.2f}x {status}")
        total_speedup += speedup
        count += 1

    avg_speedup = total_speedup / count if count > 0 else 1
    print(f"\n📊 Average speedup: {avg_speedup:.2f}x")
    print(f"📈 Total tests: {count}")
    return all_results

if __name__ == "__main__":
    try:
        results = run_full_benchmark()

        # Save detailed results
        import json
        with open('benchmark_results.json', 'w') as f:
            # Convert numpy arrays to lists for JSON serialization
            json_results = []
            for result in results:
                json_result = result.copy()
                json_result['times_original'] = result['times_original']
                json_result['times_optimized'] = result['times_optimized']
                json_results.append(json_result)

            json.dump(json_results, f, indent=2)

        print("\n💾 Detailed results saved to benchmark_results.json")

    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("Install required packages:")
        print("pip install numba numpy")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Benchmark failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
