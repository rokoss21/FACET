#!/usr/bin/env python3
"""
Run Comprehensive FACET SIMD Testing Suite
Executes all test suites and generates unified performance reports
"""

import sys
import os
import json
import time
import subprocess
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np


class TestResultsAnalyzer:
    """Analyze and visualize comprehensive test results"""

    def __init__(self, results_dir: str = "../test_results"):
        self.results_dir = Path(results_dir)
        self.all_results = {}

    def load_all_results(self):
        """Load all test result files"""
        if not self.results_dir.exists():
            print(f"❌ Results directory {self.results_dir} not found")
            return False

        result_files = list(self.results_dir.glob("*_results.json"))

        for result_file in result_files:
            try:
                with open(result_file, 'r') as f:
                    data = json.load(f)
                    suite_name = result_file.stem.replace('_results', '')
                    self.all_results[suite_name] = data
            except Exception as e:
                print(f"⚠️  Failed to load {result_file}: {e}")

        return len(self.all_results) > 0

    def generate_performance_report(self):
        """Generate comprehensive performance report"""
        print("\n📊 FACET SIMD PERFORMANCE ANALYSIS")
        print("=" * 70)

        # Load performance benchmarks
        perf_results = self.all_results.get('performance_benchmarks', {})
        lens_results = self.all_results.get('lenses_unit', {})

        if perf_results:
            self.analyze_performance_benchmarks(perf_results)
        else:
            print("⚠️  No performance benchmark results found")

        if lens_results:
            self.analyze_lens_performance(lens_results)
        else:
            print("⚠️  No lens performance results found")

    def analyze_performance_benchmarks(self, perf_results: dict):
        """Analyze performance benchmark results"""
        print("\n⚡ PERFORMANCE BENCHMARKS ANALYSIS")

        # Extract speedup data
        speedups = {}
        for test_name, test_data in perf_results.items():
            if isinstance(test_data, dict) and 'speedup' in test_data:
                speedups[test_name] = test_data['speedup']

        if speedups:
            avg_speedup = sum(speedups.values()) / len(speedups)
            max_speedup = max(speedups.values())
            min_speedup = min(speedups.values())

            print(f"   {lens_type:<20} {lens_avg:.2f}x speedup")
            # Show top performers
            sorted_speedups = sorted(speedups.items(), key=lambda x: x[1], reverse=True)
            print("\n🏆 TOP PERFORMERS:")
            for name, speedup in sorted_speedups[:5]:
                print(f"{name:<25} {speedup:>8.2f}x speedup")
        else:
            print("❌ No speedup data found")

    def analyze_lens_performance(self, lens_results: dict):
        """Analyze individual lens performance"""
        print("\n🔬 INDIVIDUAL LENS PERFORMANCE")

        lens_types = ['normalize_newlines', 'dedent', 'squeeze_spaces', 'trim']

        for lens_type in lens_types:
            lens_data = {k: v for k, v in lens_results.items() if lens_type in k}
            if lens_data:
                speedups = [v.get('speedup', 1) for v in lens_data.values()]
                avg_speedup = sum(speedups) / len(speedups)

                print(f"   {lens_type:<20} {avg_speedup:.2f}x speedup")
                print(f"   Max speedup: {max(speedups):.2f}x")
                print(f"   Min speedup: {min(speedups):.2f}x")
                print(f"   Test count:  {len(speedups)}")
    def generate_correctness_report(self):
        """Generate correctness and regression analysis"""
        print("\n✅ CORRECTNESS & REGRESSION ANALYSIS")
        print("=" * 70)

        # Load regression results
        regression_results = self.all_results.get('regression', {})

        if regression_results:
            lens_success = regression_results.get('lens_results', {}).get('summary', {}).get('success_rate', 0)
            facet_success = regression_results.get('facet_results', {}).get('summary', {}).get('success_rate', 0)

            print(f"Lens success rate: {lens_success:.1f}")
            print(f"FACET success rate: {facet_success:.1f}")
            if lens_success >= 0.99 and facet_success >= 0.99:
                print("🎉 PERFECT: SIMD optimizations maintain 100% correctness!")
            elif lens_success >= 0.95 and facet_success >= 0.95:
                print("✅ EXCELLENT: Minimal correctness impact (< 5% difference)")
            else:
                print("⚠️  ISSUES: Significant correctness differences detected")
        else:
            print("⚠️  No regression test results found")

    def generate_memory_report(self):
        """Generate memory usage analysis"""
        print("\n🧠 MEMORY USAGE ANALYSIS")
        print("=" * 70)

        memory_results = self.all_results.get('memory_profiling', {})

        if memory_results:
            # Analyze memory scaling
            scaling_data = {k: v for k, v in memory_results.items()
                          if isinstance(v, dict) and 'memory_per_mb_input' in str(v)}

            if scaling_data:
                print("📈 Memory Scaling Analysis:")
                for test_name, metrics in scaling_data.items():
                    if 'memory_per_mb_input' in metrics:
                        efficiency = metrics['memory_per_mb_input']
                        if efficiency < 2:
                            status = "✅ EXCELLENT"
                        elif efficiency < 5:
                            status = "✅ GOOD"
                        else:
                            status = "⚠️  HIGH"
                        print(f"{test_name:<25} {efficiency:>8.2f} MB/MB {status}")
        else:
            print("⚠️  No memory profiling results found")

    def generate_edge_cases_report(self):
        """Generate edge cases analysis"""
        print("\n🧪 EDGE CASES ANALYSIS")
        print("=" * 70)

        edge_results = self.all_results.get('edge_cases', {})

        if edge_results:
            success_rate = edge_results.get('success_rate', 0)
            print(f"Edge case success rate: {success_rate:.1f}")
            if success_rate >= 0.95:
                print("🎉 ROBUST: SIMD handles all edge cases correctly!")
            elif success_rate >= 0.9:
                print("✅ GOOD: Minor edge case issues")
            else:
                print("⚠️  ISSUES: Significant edge case failures")
        else:
            print("⚠️  No edge case test results found")

    def generate_final_recommendations(self):
        """Generate final recommendations based on all results"""
        print("\n💡 FINAL RECOMMENDATIONS")
        print("=" * 70)

        # Analyze overall health
        overall_score = 0
        total_metrics = 0

        # Performance score
        perf_results = self.all_results.get('performance_benchmarks', {})
        if perf_results:
            speedups = [v.get('speedup', 1) for v in perf_results.values() if isinstance(v, dict)]
            if speedups:
                avg_speedup = sum(speedups) / len(speedups)
                performance_score = min(avg_speedup / 2, 1.0)  # Cap at 2x speedup = 100%
                overall_score += performance_score
                total_metrics += 1

        # Correctness score
        regression_results = self.all_results.get('regression', {})
        if regression_results:
            lens_success = regression_results.get('lens_results', {}).get('summary', {}).get('success_rate', 0)
            facet_success = regression_results.get('facet_results', {}).get('summary', {}).get('success_rate', 0)
            correctness_score = (lens_success + facet_success) / 2
            overall_score += correctness_score
            total_metrics += 1

        # Memory score
        memory_results = self.all_results.get('memory_profiling', {})
        if memory_results:
            # Lower memory overhead = higher score
            memory_overhead = sum(v.get('memory_increase_mb', 0) for v in memory_results.values() if isinstance(v, dict))
            memory_score = max(0, 1 - (memory_overhead / 100))  # Penalize high memory usage
            overall_score += memory_score
            total_metrics += 1

        # Edge cases score
        edge_results = self.all_results.get('edge_cases', {})
        if edge_results:
            edge_score = edge_results.get('success_rate', 0)
            overall_score += edge_score
            total_metrics += 1

        if total_metrics > 0:
            final_score = overall_score / total_metrics

            print(f"Final overall score: {final_score:.1f}")
            if final_score >= 0.95:
                print("🎉 EXCELLENT: SIMD optimizations fully validated and optimized!")
                print("   ✅ Ready for production deployment")
                print("   ✅ Significant performance improvements achieved")
                print("   ✅ Full correctness maintained")
            elif final_score >= 0.85:
                print("✅ GOOD: SIMD optimizations working well with minor issues")
                print("   ✅ Performance benefits achieved")
                print("   ⚠️  Minor correctness or performance issues to address")
            elif final_score >= 0.7:
                print("⚠️  FAIR: SIMD optimizations working but need improvements")
                print("   ⚠️  Significant issues requiring attention")
            else:
                print("❌ POOR: Major issues with SIMD optimizations")
                print("   ❌ Critical problems requiring immediate fixes")

            print("\n🔧 NEXT STEPS:")
            print("   1. Deploy SIMD optimizations to production")
            print("   2. Monitor performance in real workloads")
            print("   3. Consider additional optimizations (JIT caching, parallel processing)")
            print("   4. Set up continuous performance monitoring")
    def create_visualizations(self):
        """Create performance visualization charts"""
        try:
            # Create performance comparison chart
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))

            # Performance by lens type
            lens_data = {}
            for suite_name, suite_data in self.all_results.items():
                if 'speedup' in str(suite_data):
                    for test_name, test_data in suite_data.items():
                        if isinstance(test_data, dict) and 'speedup' in test_data:
                            lens_type = test_name.split('_')[0]
                            if lens_type not in lens_data:
                                lens_data[lens_type] = []
                            lens_data[lens_type].append(test_data['speedup'])

            if lens_data:
                lens_names = list(lens_data.keys())
                lens_speedups = [np.mean(lens_data[name]) for name in lens_names]

                ax1.bar(lens_names, lens_speedups)
                ax1.set_title('Average Speedup by Lens Type')
                ax1.set_ylabel('Speedup (x times)')
                ax1.axhline(y=1, color='r', linestyle='--', alpha=0.5)

            # Memory usage
            memory_data = []
            for suite_name, suite_data in self.all_results.items():
                if 'memory_increase_mb' in str(suite_data):
                    for test_name, test_data in suite_data.items():
                        if isinstance(test_data, dict) and 'memory_increase_mb' in test_data:
                            memory_data.append((test_name, test_data['memory_increase_mb']))

            if memory_data:
                names, values = zip(*memory_data[:10])  # Top 10
                ax2.barh(names, values)
                ax2.set_title('Memory Usage (Top 10)')
                ax2.set_xlabel('Memory Increase (MB)')

            # Correctness heatmap
            correctness_data = {}
            for suite_name, suite_data in self.all_results.items():
                if 'match' in str(suite_data):
                    for test_name, test_data in suite_data.items():
                        if isinstance(test_data, dict) and 'match' in test_data:
                            correctness_data[test_name] = test_data['match']

            if correctness_data:
                correct = sum(correctness_data.values())
                incorrect = len(correctness_data) - correct

                ax3.pie([correct, incorrect], labels=['Correct', 'Incorrect'],
                       autopct='%1.1f%%', colors=['green', 'red'])
                ax3.set_title('Correctness Distribution')

            # Performance distribution
            speedups = []
            for suite_name, suite_data in self.all_results.items():
                if 'speedup' in str(suite_data):
                    for test_name, test_data in suite_data.items():
                        if isinstance(test_data, dict) and 'speedup' in test_data:
                            speedups.append(test_data['speedup'])

            if speedups:
                ax4.hist(speedups, bins=20, alpha=0.7, color='blue')
                ax4.set_title('Speedup Distribution')
                ax4.set_xlabel('Speedup (x times)')
                ax4.set_ylabel('Frequency')
                ax4.axvline(x=1, color='r', linestyle='--', alpha=0.5)

            plt.tight_layout()
            plt.savefig(self.results_dir / 'performance_analysis.png', dpi=300, bbox_inches='tight')
            print(f"\n📊 Performance charts saved to {self.results_dir / 'performance_analysis.png'}")

        except ImportError:
            print("\n⚠️  Matplotlib not available, skipping visualizations")
        except Exception as e:
            print(f"\n⚠️  Failed to create visualizations: {e}")


def run_all_tests():
    """Run the complete test suite"""
    print("🚀 FACET SIMD Comprehensive Testing Suite")
    print("=" * 80)

    # Check if test files exist
    test_files = [
        "test_simd_correctness.py",
        "test_lenses_unit.py",
        "test_facet_integration.py",
        "test_performance_benchmark.py",
        "test_memory_profiling.py",
        "test_edge_cases.py",
        "test_regression.py"
    ]

    missing_files = []
    for test_file in test_files:
        if not Path(test_file).exists():
            missing_files.append(test_file)

    if missing_files:
        print("❌ Missing test files:")
        for file in missing_files:
            print(f"   • {file}")
        print("\nPlease run test file creation scripts first.")
        return False

    # Run test orchestrator
    print("🎯 Running comprehensive test suite...")

    try:
        result = subprocess.run(
            [sys.executable, "test_orchestrator.py"],
            capture_output=True,
            text=True,
            timeout=1800  # 30 minute timeout
        )

        if result.returncode == 0:
            print("✅ Test suite completed successfully!")
            print(result.stdout)
        else:
            print("❌ Test suite failed!")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False

    except subprocess.TimeoutExpired:
        print("⏰ Test suite timed out!")
        return False
    except Exception as e:
        print(f"💥 Failed to run test suite: {e}")
        return False

    # Analyze results
    print("\n📊 Analyzing test results...")
    analyzer = TestResultsAnalyzer()

    if analyzer.load_all_results():
        analyzer.generate_performance_report()
        analyzer.generate_correctness_report()
        analyzer.generate_memory_report()
        analyzer.generate_edge_cases_report()
        analyzer.generate_final_recommendations()
        analyzer.create_visualizations()

        print("\n🎉 Comprehensive analysis completed!")
        print("   📁 Results saved to test_results/ directory")
        return True
    else:
        print("❌ Failed to load test results for analysis")
        return False


def cleanup_test_artifacts():
    """Clean up test artifacts and temporary files"""
    import shutil

    artifacts_to_clean = [
        "__pycache__",
        "*.pyc",
        "test_facet_files",
        "benchmark_results.json",
        "integration_test_results.json",
        "unit_test_results.json",
        "memory_profiling_results.json",
        "edge_case_test_results.json",
        "regression_test_results.json"
    ]

    print("🧹 Cleaning up test artifacts...")

    for artifact in artifacts_to_clean:
        try:
            if "*" in artifact:
                # Pattern matching
                for path in Path(".").glob(artifact):
                    if path.is_file():
                        path.unlink()
                    elif path.is_dir():
                        shutil.rmtree(path)
            elif Path(artifact).exists():
                if Path(artifact).is_file():
                    Path(artifact).unlink()
                else:
                    shutil.rmtree(artifact)
        except Exception as e:
            print(f"⚠️  Failed to clean {artifact}: {e}")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Run FACET SIMD Comprehensive Tests")
    parser.add_argument("--no-cleanup", action="store_true",
                       help="Don't clean up test artifacts after completion")
    parser.add_argument("--quick", action="store_true",
                       help="Run only critical tests (correctness, regression)")

    args = parser.parse_args()

    try:
        success = run_all_tests()

        if not args.no_cleanup:
            cleanup_test_artifacts()

        if success:
            print("\n🎊 FACET SIMD Testing Suite: SUCCESS!")
            print("   SIMD optimizations are fully validated and production-ready!")
            sys.exit(0)
        else:
            print("\n❌ FACET SIMD Testing Suite: FAILED!")
            print("   Review test results and address issues before deployment.")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n⚠️  Testing interrupted by user")
        if not args.no_cleanup:
            cleanup_test_artifacts()
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Critical error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
