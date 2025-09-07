#!/usr/bin/env python3
"""
Test Runner for FACET MCP Server

Runs all test suites and provides comprehensive reporting.
"""

import subprocess
import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'server'))


def run_unit_tests():
    """Run unit tests"""
    print("🧪 Running Unit Tests...")
    print("=" * 50)

    test_files = [
        "test_server.py",
        "test_facets_engine.py",
        "test_validator.py"
    ]

    for test_file in test_files:
        print(f"\n📄 Running {test_file}...")
        result = subprocess.run([
            sys.executable, "-m", "pytest",
            f"{test_file}",
            "-v", "--tb=short"
        ], capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ PASSED"        else:
            print("❌ FAILED"            print(result.stdout)
            print(result.stderr)
            return False

    return True


def run_integration_tests():
    """Run integration tests"""
    print("\n🔗 Running Integration Tests...")
    print("=" * 50)

    result = subprocess.run([
        sys.executable, "-m", "pytest",
        "test_integration.py",
        "-v", "--tb=short"
    ], capture_output=True, text=True)

    if result.returncode == 0:
        print("✅ Integration tests PASSED")
        return True
    else:
        print("❌ Integration tests FAILED")
        print(result.stdout)
        print(result.stderr)
        return False


def run_e2e_tests():
    """Run end-to-end tests"""
    print("\n🌐 Running End-to-End Tests...")
    print("=" * 50)
    print("⚠️  Note: E2E tests require WebSocket server functionality")
    print("   Make sure no other servers are running on test ports")

    result = subprocess.run([
        sys.executable, "-m", "pytest",
        "test_e2e.py",
        "-v", "--tb=short", "-s"
    ], capture_output=True, text=True)

    if result.returncode == 0:
        print("✅ E2E tests PASSED")
        return True
    else:
        print("❌ E2E tests FAILED")
        print(result.stdout)
        print(result.stderr)
        return False


def run_all_tests():
    """Run complete test suite"""
    print("🚀 FACET MCP Server - Complete Test Suite")
    print("=" * 60)

    results = []

    # Unit tests
    unit_passed = run_unit_tests()
    results.append(("Unit Tests", unit_passed))

    # Integration tests
    integration_passed = run_integration_tests()
    results.append(("Integration Tests", integration_passed))

    # E2E tests
    e2e_passed = run_e2e_tests()
    results.append(("E2E Tests", e2e_passed))

    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)

    passed = 0
    total = len(results)

    for test_name, test_passed in results:
        status = "✅ PASSED" if test_passed else "❌ FAILED"
        print("25")
        if test_passed:
            passed += 1

    print(f"\n🎯 Overall: {passed}/{total} test suites passed")

    if passed == total:
        print("🎉 ALL TESTS PASSED! MCP Server is ready for production!")
        return 0
    else:
        print("⚠️  Some tests failed. Please review the output above.")
        return 1


def run_quick_test():
    """Run quick smoke test"""
    print("🚀 FACET MCP Server - Quick Smoke Test")
    print("=" * 50)

    try:
        from facet_mcp.server import FACETMCPServer

        # Test server initialization
        server = FACETMCPServer()
        print("✅ Server initialization: PASSED")

        # Test tool registration
        assert len(server.tools) == 3
        print("✅ Tool registration: PASSED")

        # Test FACET engine
        from facet_mcp.core.facets import FACETEngine
        engine = FACETEngine()
        print("✅ FACET engine: PASSED")

        # Test schema validator
        from facet_mcp.core.validator import SchemaValidator
        validator = SchemaValidator()
        print("✅ Schema validator: PASSED")

        print("\n🎉 Quick smoke test PASSED!")
        print("🚀 MCP Server components are working correctly!")
        return 0

    except Exception as e:
        print(f"❌ Quick smoke test FAILED: {e}")
        return 1


def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        if sys.argv[1] == "quick":
            return run_quick_test()
        elif sys.argv[1] == "unit":
            return 0 if run_unit_tests() else 1
        elif sys.argv[1] == "integration":
            return 0 if run_integration_tests() else 1
        elif sys.argv[1] == "e2e":
            return 0 if run_e2e_tests() else 1

    # Default: run all tests
    return run_all_tests()


if __name__ == "__main__":
    sys.exit(main())
