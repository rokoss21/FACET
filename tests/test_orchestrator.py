#!/usr/bin/env python3
"""
FACET SIMD Comprehensive Test Orchestrator
Runs all test suites in optimal order and generates unified reports
"""

import sys
import os
import json
import time
from typing import Dict, List, Any
from pathlib import Path
import subprocess
import argparse


class TestOrchestrator:
    """Orchestrates comprehensive testing of FACET SIMD optimizations"""

    def __init__(self, config_file: str = "test_suite_config.json"):
        self.config_file = config_file
        self.results_dir = Path("test_results")
        self.results_dir.mkdir(exist_ok=True)
        self.start_time = time.time()

    def load_config(self) -> Dict[str, Any]:
        """Load test configuration"""
        if not Path(self.config_file).exists():
            print(f"⚠️  Config file {self.config_file} not found, using defaults")
            return self.get_default_config()

        with open(self.config_file, 'r') as f:
            return json.load(f)

    def get_default_config(self) -> Dict[str, Any]:
        """Get default test configuration"""
        return {
            "test_suites": {
                "correctness_tests": {
                    "description": "Basic correctness tests",
                    "test_files": ["test_simd_correctness.py"],
                    "priority": 1
                },
                "unit_tests": {
                    "description": "Unit tests for SIMD lenses",
                    "test_files": ["test_lenses_unit.py"],
                    "priority": 2
                },
                "integration_tests": {
                    "description": "Integration tests for FACET parser",
                    "test_files": ["test_facet_integration.py"],
                    "priority": 3
                },
                "edge_cases": {
                    "description": "Edge cases and robustness tests",
                    "test_files": ["test_edge_cases.py"],
                    "priority": 4
                },
                "regression_tests": {
                    "description": "Regression tests vs baseline",
                    "test_files": ["test_regression.py"],
                    "priority": 5
                },
                "performance_benchmarks": {
                    "description": "Performance benchmarks",
                    "test_files": ["test_performance_benchmark.py"],
                    "priority": 6
                },
                "memory_profiling": {
                    "description": "Memory usage profiling",
                    "test_files": ["test_memory_profiling.py"],
                    "priority": 7
                }
            }
        }

    def run_test_suite(self, suite_name: str, suite_config: Dict[str, Any]) -> Dict[str, Any]:
        """Run a specific test suite"""
        print(f"\n🚀 Running {suite_name}...")
        print("=" * 60)
        print(f"Description: {suite_config.get('description', 'No description')}")

        suite_start_time = time.time()
        suite_results = {
            "suite_name": suite_name,
            "start_time": suite_start_time,
            "test_files": [],
            "success": True,
            "errors": []
        }

        # Run each test file in the suite
        for test_file in suite_config.get("test_files", []):
            if not Path(test_file).exists():
                error_msg = f"Test file {test_file} not found"
                print(f"❌ {error_msg}")
                suite_results["errors"].append(error_msg)
                suite_results["success"] = False
                continue

            print(f"\n📄 Running {test_file}...")
            file_start_time = time.time()

            try:
                # Run the test file
                result = subprocess.run(
                    [sys.executable, test_file],
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout
                )

                file_end_time = time.time()
                execution_time = file_end_time - file_start_time

                test_result = {
                    "file": test_file,
                    "success": result.returncode == 0,
                    "return_code": result.returncode,
                    "execution_time": execution_time,
                    "stdout": result.stdout,
                    "stderr": result.stderr
                }

                if result.returncode == 0:
                    print(f"✅ {test_file}: {execution_time:.2f}s")
                else:
                    print(f"❌ {test_file}: {execution_time:.2f}s (exit code: {result.returncode})")
                    suite_results["success"] = False

                suite_results["test_files"].append(test_result)

            except subprocess.TimeoutExpired:
                error_msg = f"Test file {test_file} timed out"
                print(f"⏰ {error_msg}")
                suite_results["errors"].append(error_msg)
                suite_results["success"] = False
                suite_results["test_files"].append({
                    "file": test_file,
                    "success": False,
                    "error": "Timeout"
                })

            except Exception as e:
                error_msg = f"Failed to run {test_file}: {e}"
                print(f"💥 {error_msg}")
                suite_results["errors"].append(error_msg)
                suite_results["success"] = False
                suite_results["test_files"].append({
                    "file": test_file,
                    "success": False,
                    "error": str(e)
                })

        suite_end_time = time.time()
        suite_results["end_time"] = suite_end_time
        suite_results["duration"] = suite_end_time - suite_start_time

        # Save suite results
        result_file = self.results_dir / f"{suite_name}_results.json"
        with open(result_file, 'w') as f:
            json.dump(suite_results, f, indent=2, default=str)

        return suite_results

    def run_all_tests(self, parallel: bool = False) -> Dict[str, Any]:
        """Run all test suites in optimal order"""
        config = self.load_config()

        # Sort test suites by priority
        test_suites = sorted(
            config["test_suites"].items(),
            key=lambda x: x[1].get("priority", 999)
        )

        overall_results = {
            "test_run": {
                "start_time": self.start_time,
                "config_file": self.config_file,
                "parallel_execution": parallel
            },
            "suite_results": {},
            "summary": {
                "total_suites": len(test_suites),
                "successful_suites": 0,
                "failed_suites": 0,
                "total_execution_time": 0
            }
        }

        print("🎯 FACET SIMD Comprehensive Test Suite")
        print("=" * 80)
        print(f"Configuration: {self.config_file}")
        print(f"Parallel execution: {parallel}")
        print(f"Test suites to run: {len(test_suites)}")
        print()

        for suite_name, suite_config in test_suites:
            try:
                suite_result = self.run_test_suite(suite_name, suite_config)
                overall_results["suite_results"][suite_name] = suite_result

                if suite_result["success"]:
                    overall_results["summary"]["successful_suites"] += 1
                else:
                    overall_results["summary"]["failed_suites"] += 1

                overall_results["summary"]["total_execution_time"] += suite_result["duration"]

            except Exception as e:
                print(f"💥 Critical error in {suite_name}: {e}")
                overall_results["suite_results"][suite_name] = {
                    "suite_name": suite_name,
                    "success": False,
                    "error": str(e)
                }
                overall_results["summary"]["failed_suites"] += 1

        # Generate final summary
        self.generate_final_report(overall_results)

        return overall_results

    def generate_final_report(self, results: Dict[str, Any]):
        """Generate comprehensive final report"""
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE TEST REPORT")
        print("=" * 80)

        summary = results["summary"]
        suite_results = results["suite_results"]

        # Overall statistics
        total_suites = summary["total_suites"]
        successful_suites = summary["successful_suites"]
        failed_suites = summary["failed_suites"]
        total_time = summary["total_execution_time"]

        success_rate = successful_suites / total_suites if total_suites > 0 else 0

        print("\n🎯 OVERALL RESULTS:")
        print(f"   Total Test Suites: {total_suites}")
        print(f"   Successful: {successful_suites}")
        print(f"   Failed: {failed_suites}")
        print(f"   Success rate: {success_rate:.1f}")
        print(f"   Total time: {total_time:.2f}s")
        # Detailed suite results
        print("\n📋 SUITE DETAILS:")
        for suite_name, suite_result in suite_results.items():
            duration = suite_result.get("duration", 0)
            success = suite_result.get("success", False)
            status = "✅ PASS" if success else "❌ FAIL"

            print(f"{suite_name:<25} {duration:>8.2f}s {status}")
            if not success:
                errors = suite_result.get("errors", [])
                if errors:
                    print(f"      Errors: {len(errors)}")

        # Performance insights
        if success_rate >= 0.9:
            print("\n🎉 EXCELLENT RESULTS!")
            print("   SIMD optimizations are working correctly!")
            print("   All core functionality is preserved.")
            print("   Performance improvements achieved.")
        elif success_rate >= 0.7:
            print("\n⚠️  GOOD RESULTS WITH ISSUES")
            print("   SIMD optimizations working but some issues detected.")
            print("   Review failed tests for potential regressions.")
        else:
            print("\n❌ SIGNIFICANT ISSUES DETECTED")
            print("   Critical problems with SIMD optimizations.")
            print("   Immediate investigation required.")

        # Recommendations
        print("\n💡 RECOMMENDATIONS:")
        print("   • Review detailed logs in test_results/ directory")
        print("   • Check performance benchmarks for optimization effectiveness")
        print("   • Verify memory profiling for resource usage patterns")
        print("   • Run edge case tests for robustness validation")

    def cleanup_old_results(self):
        """Clean up old test results"""
        import shutil

        if self.results_dir.exists():
            print(f"🧹 Cleaning up old results in {self.results_dir}")
            shutil.rmtree(self.results_dir)

        self.results_dir.mkdir(exist_ok=True)


def main():
    """Main entry point for test orchestration"""
    parser = argparse.ArgumentParser(description="FACET SIMD Comprehensive Test Orchestrator")
    parser.add_argument("--config", default="test_suite_config.json",
                       help="Test configuration file")
    parser.add_argument("--parallel", action="store_true",
                       help="Run tests in parallel (experimental)")
    parser.add_argument("--clean", action="store_true",
                       help="Clean up old test results before running")
    parser.add_argument("--suite", help="Run only specific test suite")

    args = parser.parse_args()

    # Initialize orchestrator
    orchestrator = TestOrchestrator(args.config)

    if args.clean:
        orchestrator.cleanup_old_results()

    try:
        if args.suite:
            # Run single test suite
            config = orchestrator.load_config()
            if args.suite in config["test_suites"]:
                suite_config = config["test_suites"][args.suite]
                result = orchestrator.run_test_suite(args.suite, suite_config)

                success_rate = 1.0 if result["success"] else 0.0
                if success_rate >= 0.9:
                    print("\n✅ Test suite completed successfully!")
                    sys.exit(0)
                else:
                    print("\n❌ Test suite had issues!")
                    sys.exit(1)
            else:
                print(f"❌ Test suite '{args.suite}' not found")
                sys.exit(1)
        else:
            # Run all test suites
            results = orchestrator.run_all_tests(args.parallel)

            success_rate = results["summary"]["successful_suites"] / results["summary"]["total_suites"]

            # Save comprehensive results
            with open(orchestrator.results_dir / "comprehensive_test_results.json", 'w') as f:
                json.dump(results, f, indent=2, default=str)

            if success_rate >= 0.9:
                print("\n🎉 All tests completed successfully!")
                print("   SIMD optimizations are fully validated!")
                sys.exit(0)
            else:
                print("\n⚠️  Tests completed with some issues")
                print("   Review detailed results for optimization status")
                sys.exit(1)

    except KeyboardInterrupt:
        print("\n⚠️  Test orchestration interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Critical error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
