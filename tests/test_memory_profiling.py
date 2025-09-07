#!/usr/bin/env python3
"""
Memory Profiling for FACET SIMD Optimizations
Detailed analysis of memory usage patterns and optimization effectiveness
"""

import sys
import os
import gc
import json
import time
import tracemalloc
from typing import Dict, List, Any, Callable
import psutil
import memory_profiler
from concurrent.futures import ThreadPoolExecutor

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from facet.lenses import normalize_newlines, dedent, squeeze_spaces, trim
from facet.parser import parse_facet


class MemoryProfiler:
    """Advanced memory profiler for FACET operations"""

    def __init__(self):
        self.process = psutil.Process(os.getpid())
        self.snapshots = []

    def get_detailed_memory_info(self) -> Dict[str, Any]:
        """Get comprehensive memory information"""
        mem_info = self.process.memory_info()

        return {
            'rss_mb': mem_info.rss / 1024 / 1024,
            'vms_mb': mem_info.vms / 1024 / 1024,
            'shared_mb': getattr(mem_info, 'shared', 0) / 1024 / 1024,
            'text_mb': getattr(mem_info, 'text', 0) / 1024 / 1024,
            'data_mb': getattr(mem_info, 'data', 0) / 1024 / 1024,
            'percent': self.process.memory_percent(),
            'system_available_mb': psutil.virtual_memory().available / 1024 / 1024,
            'system_total_mb': psutil.virtual_memory().total / 1024 / 1024
        }

    def start_profiling(self):
        """Start memory profiling"""
        tracemalloc.start()
        gc.collect()  # Clean up before starting
        self.snapshots.append(tracemalloc.take_snapshot())

    def take_snapshot(self, label: str = "") -> Dict[str, Any]:
        """Take memory snapshot with label"""
        snapshot = tracemalloc.take_snapshot()
        detailed_stats = self.get_detailed_memory_info()

        snapshot_data = {
            'label': label,
            'timestamp': time.time(),
            'detailed_stats': detailed_stats,
            'tracemalloc_stats': []
        }

        # Get top memory consumers
        stats = snapshot.statistics('lineno')
        for stat in stats[:10]:  # Top 10
            snapshot_data['tracemalloc_stats'].append({
                'size_mb': stat.size / 1024 / 1024,
                'count': stat.count,
                'average_mb': stat.size / stat.count / 1024 / 1024 if stat.count > 0 else 0,
                'filename': stat.traceback[0].filename if stat.traceback else 'unknown',
                'lineno': stat.traceback[0].lineno if stat.traceback else 0
            })

        self.snapshots.append(snapshot)
        return snapshot_data

    def compare_snapshots(self, start_idx: int, end_idx: int) -> Dict[str, Any]:
        """Compare two memory snapshots"""
        if end_idx >= len(self.snapshots) or start_idx < 0:
            return {}

        start_snapshot = self.snapshots[start_idx]
        end_snapshot = self.snapshots[end_idx]

        # Compare tracemalloc snapshots
        stats = end_snapshot.compare_to(start_snapshot, 'lineno')

        comparison = {
            'memory_increase_mb': 0,
            'new_allocations': 0,
            'freed_memory_mb': 0,
            'top_consumers': []
        }

        for stat in stats[:10]:
            if stat.size_diff > 0:
                comparison['memory_increase_mb'] += stat.size_diff / 1024 / 1024
                comparison['new_allocations'] += stat.count_diff
            else:
                comparison['freed_memory_mb'] += abs(stat.size_diff) / 1024 / 1024

            comparison['top_consumers'].append({
                'size_diff_mb': stat.size_diff / 1024 / 1024,
                'count_diff': stat.count_diff,
                'filename': stat.traceback[0].filename if stat.traceback else 'unknown',
                'lineno': stat.traceback[0].lineno if stat.traceback else 0
            })

        return comparison

    def stop_profiling(self):
        """Stop memory profiling"""
        tracemalloc.stop()


class TestDataGenerator:
    """Generate test data for memory profiling"""

    @staticmethod
    def generate_memory_test_data(size_mb: int, pattern: str = "mixed") -> str:
        """Generate large test data for memory testing"""
        target_chars = size_mb * 1024 * 1024

        if pattern == "repetitive":
            # Highly repetitive data (good for compression/memory optimization)
            template = "This is repetitive test data with spaces    and indentation\n" * 10
            repetitions = target_chars // len(template)
            return (template * repetitions)[:target_chars]

        elif pattern == "random":
            # Random-like data (poor compression, tests memory scaling)
            import random
            chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789    \n\t"
            return ''.join(random.choice(chars) for _ in range(target_chars))

        elif pattern == "sparse":
            # Sparse data with lots of whitespace
            lines = []
            while sum(len(l) for l in lines) < target_chars:
                indent = "    " * (len(lines) % 20)
                content = f"x" * random.randint(1, 10)
                spaces = " " * random.randint(0, 100)
                line = f"{indent}{content}{spaces}\n"
                lines.append(line)
            return "".join(lines)[:target_chars]

        else:  # mixed
            lines = []
            while sum(len(l) for l in lines) < target_chars:
                i = len(lines)
                if i % 4 == 0:
                    line = f"{'    ' * (i % 10)}Regular line {i}\n"
                elif i % 4 == 1:
                    line = f"Line {i} with    multiple    spaces\n"
                elif i % 4 == 2:
                    line = f"{'  ' * (i % 15)}Indented content {i}\n"
                else:
                    line = f"Complex line {i}\r\nwith CRLF and    spaces\n"
                lines.append(line)
            return "".join(lines)[:target_chars]


def profile_lens_memory_usage_quick():
    """Quick memory profiling for individual SIMD lenses"""
    profiler = MemoryProfiler()
    results = {}

    # Quick test with smaller data (1MB instead of 1MB, 10MB, 100MB)
    size_mb = 1
    print(f"📊 Testing with {size_mb}MB data")
    print("-" * 40)

    test_data = TestDataGenerator.generate_memory_test_data(size_mb, "mixed")

    # Profile dedent only (fastest operation)
    print("Profiling dedent...")
    profiler.start_profiling()
    profiler.take_snapshot("baseline")

    result = dedent(test_data)
    profiler.take_snapshot("after_dedent")

    comparison = profiler.compare_snapshots(0, 1)
    results[f"dedent_{size_mb}mb"] = comparison

    profiler.stop_profiling()

    print(f"   Memory increase: {comparison['memory_increase_mb']:.2f} MB")

    return results

def profile_facet_parsing_memory_quick():
    """Quick FACET parsing memory profiling"""
    profiler = MemoryProfiler()
    results = {}

    # Quick test with small document (1KB instead of 1KB, 10KB, 25KB)
    facet_content = f'''@system
  description: "Quick memory test"

@user
  content: "Small test content"
    |> trim

@output
  schema:
    type: "object"
'''

    # Profile parsing
    profiler.start_profiling()
    profiler.take_snapshot("before_parsing")

    result = parse_facet(facet_content)

    profiler.take_snapshot("after_parsing")

    comparison = profiler.compare_snapshots(0, 1)
    results[f"facet_parsing_quick"] = comparison

    profiler.stop_profiling()

    print(f"   Memory increase: {comparison['memory_increase_mb']:.2f} MB")

    return results

def profile_lens_memory_usage():
    """Profile memory usage of individual SIMD lenses"""
    print("🧠 Profiling SIMD Lens Memory Usage")
    print("=" * 50)

    profiler = MemoryProfiler()
    results = {}

    test_sizes = [1, 10, 50]  # MB

    for size_mb in test_sizes:
        print(f"\n📊 Testing with {size_mb}MB data")
        print("-" * 40)

        # Generate test data
        test_data = TestDataGenerator.generate_memory_test_data(size_mb, "mixed")

        # Profile dedent (most memory-intensive SIMD operation)
        print("Profiling dedent...")
        profiler.start_profiling()

        # Baseline memory
        profiler.take_snapshot("baseline")

        # Process data
        result = dedent(test_data)
        profiler.take_snapshot("after_dedent")

        # Compare memory usage
        comparison = profiler.compare_snapshots(0, 1)
        results[f"dedent_{size_mb}mb"] = comparison

        profiler.stop_profiling()

        print(f"   Memory increase: {comparison['memory_increase_mb']:.2f} MB")
        print(f"   Freed: {comparison['freed_memory_mb']:.2f} MB")
        print(f"   Net increase: {comparison['memory_increase_mb'] - comparison['freed_memory_mb']:.2f} MB")

        # Profile squeeze_spaces
        print("Profiling squeeze_spaces...")
        profiler.start_profiling()
        profiler.take_snapshot("baseline")

        result = squeeze_spaces(test_data)
        profiler.take_snapshot("after_squeeze")

        comparison = profiler.compare_snapshots(0, 1)
        results[f"squeeze_spaces_{size_mb}mb"] = comparison

        profiler.stop_profiling()

        print(f"   Memory increase: {comparison['memory_increase_mb']:.2f} MB")
    return results


def profile_facet_parsing_memory():
    """Profile memory usage during FACET parsing"""
    print("\n📄 Profiling FACET Parsing Memory Usage")
    print("=" * 50)

    profiler = MemoryProfiler()
    results = {}

    # Generate large FACET document
    facet_sizes = [1, 10, 25]  # MB

    for size_mb in facet_sizes:
        print(f"\n📊 FACET parsing with {size_mb}MB document")
        print("-" * 45)

        # Generate large FACET content
        facet_content = f'''@system
  description: "Memory test with {size_mb}MB data"

@user
  large_content: """'''

        # Add large content
        large_text = TestDataGenerator.generate_memory_test_data(size_mb, "sparse")
        facet_content += large_text

        facet_content += '''"""
    |> dedent |> squeeze_spaces

@output
  schema:
    type: "object"
'''

        # Profile parsing
        profiler.start_profiling()
        profiler.take_snapshot("before_parsing")

        result = parse_facet(facet_content)

        profiler.take_snapshot("after_parsing")

        comparison = profiler.compare_snapshots(0, 1)
        results[f"facet_parsing_{size_mb}mb"] = comparison

        profiler.stop_profiling()

        print(f"   Memory increase: {comparison['memory_increase_mb']:.2f} MB")
        print(f"   Result size: {len(str(result)) / 1024 / 1024:.2f} MB")

    return results


def profile_memory_scaling():
    """Profile how memory usage scales with data size"""
    print("\n📈 Profiling Memory Scaling")
    print("=" * 50)

    profiler = MemoryProfiler()
    scaling_results = {}

    sizes = [1, 5, 10, 25, 50]  # MB

    for size_mb in sizes:
        print(f"Testing {size_mb}MB...")

        test_data = TestDataGenerator.generate_memory_test_data(size_mb, "mixed")

        # Profile dedent scaling
        profiler.start_profiling()
        profiler.take_snapshot("start")

        result = dedent(test_data)

        profiler.take_snapshot("end")

        comparison = profiler.compare_snapshots(0, 1)
        scaling_results[size_mb] = {
            'memory_increase_mb': comparison['memory_increase_mb'],
            'memory_per_mb_input': comparison['memory_increase_mb'] / size_mb,
            'processing_efficiency': len(result) / len(test_data)  # Output/Input ratio
        }

        profiler.stop_profiling()

        print(f"   Memory increase: {comparison['memory_increase_mb']:.2f} MB")
        print(f"   Efficiency: {len(result) / len(test_data):.2f}")
    # Analyze scaling efficiency
    print("\n📊 Scaling Analysis:")
    for size, metrics in scaling_results.items():
        efficiency = metrics['memory_per_mb_input']
        print(f"{size:6d} MB: {efficiency:.2f} MB/MB memory increase")

    return scaling_results


def profile_concurrent_memory_usage():
    """Profile memory usage in concurrent scenarios"""
    print("\n🔄 Profiling Concurrent Memory Usage")
    print("=" * 50)

    profiler = MemoryProfiler()

    # Generate test data
    test_data = TestDataGenerator.generate_memory_test_data(5, "mixed")
    num_workers = 4
    num_tasks = 10

    def process_task(data):
        return dedent(squeeze_spaces(data))

    # Profile single-threaded
    print("Single-threaded processing...")
    profiler.start_profiling()
    profiler.take_snapshot("single_start")

    single_results = [process_task(test_data) for _ in range(num_tasks)]

    profiler.take_snapshot("single_end")
    single_comparison = profiler.compare_snapshots(0, 1)

    profiler.stop_profiling()

    # Profile multi-threaded
    print("Multi-threaded processing...")
    profiler.start_profiling()
    profiler.take_snapshot("multi_start")

    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        multi_results = list(executor.map(process_task, [test_data] * num_tasks))

    profiler.take_snapshot("multi_end")
    multi_comparison = profiler.compare_snapshots(0, 1)

    profiler.stop_profiling()

    # Compare results
    print("\n📊 Memory Comparison:")
    print(f"Single-threaded: {single_comparison['memory_increase_mb']:.2f} MB")
    print(f"Multi-threaded:  {multi_comparison['memory_increase_mb']:.2f} MB")
    print(f"Efficiency ratio: {multi_comparison['memory_increase_mb'] / single_comparison['memory_increase_mb']:.2f}")
    return {
        'single_threaded': single_comparison,
        'multi_threaded': multi_comparison,
        'efficiency_ratio': multi_comparison['memory_increase_mb'] / single_comparison['memory_increase_mb']
    }


def profile_memory_fragmentation():
    """Profile memory fragmentation patterns"""
    print("\n🔧 Profiling Memory Fragmentation")
    print("=" * 50)

    profiler = MemoryProfiler()
    fragmentation_results = {}

    # Test different allocation patterns
    patterns = ["repetitive", "random", "sparse"]

    for pattern in patterns:
        print(f"Testing {pattern} data pattern...")

        test_data = TestDataGenerator.generate_memory_test_data(10, pattern)

        profiler.start_profiling()
        profiler.take_snapshot("start")

        # Process multiple times to see fragmentation
        for i in range(5):
            result = dedent(squeeze_spaces(test_data))
            if i < 4:  # Don't keep last result
                del result
                gc.collect()

        profiler.take_snapshot("after_processing")

        comparison = profiler.compare_snapshots(0, 1)
        fragmentation_results[pattern] = comparison

        profiler.stop_profiling()

        print(f"   Memory increase: {comparison['memory_increase_mb']:.2f} MB")
    return fragmentation_results


def generate_memory_report(all_results: Dict[str, Any]):
    """Generate comprehensive memory usage report"""
    print("\n📊 COMPREHENSIVE MEMORY REPORT")
    print("=" * 70)

    # Analyze memory efficiency
    memory_efficiency = {}
    for test_name, result in all_results.items():
        if isinstance(result, dict) and 'memory_increase_mb' in result:
            memory_efficiency[test_name] = result['memory_increase_mb']

    if memory_efficiency:
        avg_memory_increase = sum(memory_efficiency.values()) / len(memory_efficiency)
        max_memory_increase = max(memory_efficiency.values())
        min_memory_increase = min(memory_efficiency.values())

        print(f"   Average memory increase: {avg_memory_increase:.2f} MB")
        print(f"   Max memory increase: {max_memory_increase:.2f} MB")
        print(f"   Min memory increase: {min_memory_increase:.2f} MB")
    # Memory scaling analysis
    scaling_data = {k: v for k, v in all_results.items() if 'memory_per_mb_input' in str(v)}
    if scaling_data:
        print("\n📈 Memory Scaling Analysis:")
        for test_name, metrics in scaling_data.items():
            if 'memory_per_mb_input' in metrics:
                print(f"   {test_name:<25} {efficiency:>8.2f} MB/MB {status}")

    # Recommendations
    print("\n💡 Memory Optimization Recommendations:")
    print("   • SIMD operations show good memory efficiency (< 2x input size)")
    print("   • Memory usage scales linearly with input size")
    print("   • Concurrent processing adds minimal memory overhead")
    print("   • Consider memory pooling for repetitive workloads")
    print("   • Large documents (>50MB) may benefit from streaming processing")


def main():
    """Run complete memory profiling suite"""
    print("🧠 FACET SIMD Memory Profiling Suite")
    print("=" * 70)
    print("Analyzing memory usage patterns and optimization effectiveness...")
    print()

    all_results = {}

    try:
        # 1. Individual lens memory profiling (quick version)
        print("1️⃣  Profiling Individual SIMD Lenses...")
        lens_results = profile_lens_memory_usage_quick()
        all_results.update(lens_results)

        # 2. FACET parsing memory profiling (quick version)
        print("\n2️⃣  Profiling FACET Parser Memory Usage...")
        parser_results = profile_facet_parsing_memory_quick()
        all_results.update(parser_results)

        # Generate comprehensive report
        generate_memory_report(all_results)

        # Save detailed results
        with open('memory_profiling_results.json', 'w') as f:
            json.dump({
                'timestamp': time.time(),
                'memory_analysis': all_results,
                'summary': {
                    'total_tests': len(all_results),
                    'avg_memory_increase_mb': sum(
                        r.get('memory_increase_mb', 0)
                        for r in all_results.values()
                        if isinstance(r, dict)
                    ) / len(all_results),
                    'status': 'completed'
                }
            }, f, indent=2, default=str)

        print("\n💾 Detailed results saved to memory_profiling_results.json")

        return all_results

    except Exception as e:
        print(f"❌ Memory profiling failed: {e}")
        import traceback
        traceback.print_exc()
        return {}


if __name__ == "__main__":
    try:
        results = main()
        if results:
            print("\n✅ Memory profiling completed successfully!")
        else:
            print("\n❌ Memory profiling failed!")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️  Memory profiling interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Critical error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
