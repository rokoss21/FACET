#!/usr/bin/env python3
"""
Test correctness of SIMD optimizations for FACET lenses
"""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_normalize_newlines():
    """Test normalize_newlines correctness"""
    from facet.lenses import normalize_newlines

    test_cases = [
        ("Hello\r\nWorld", "Hello\nWorld"),
        ("Line 1\r\nLine 2\r\nLine 3", "Line 1\nLine 2\nLine 3"),
        ("No changes", "No changes"),
        ("", ""),
        ("\r\n\r\n", "\n\n"),
    ]

    print("🧪 Testing normalize_newlines...")
    for input_text, expected in test_cases:
        result = normalize_newlines(input_text)
        if result == expected:
            print(f"  ✅ '{input_text}' -> '{result}'")
        else:
            print(f"  ❌ '{input_text}' -> '{result}' (expected '{expected}')")
            return False
    return True

def test_dedent():
    """Test dedent correctness"""
    from facet.lenses import dedent

    test_cases = [
        ("    Hello\n    World", "Hello\nWorld"),
        ("  Line 1\n    Line 2\nLine 3", "  Line 1\n    Line 2\nLine 3"),
        ("No indent", "No indent"),
        ("", ""),
        ("    ", ""),
    ]

    print("🧪 Testing dedent...")
    for input_text, expected in test_cases:
        result = dedent(input_text)
        if result == expected:
            print(f"  ✅ '{repr(input_text)}' -> '{repr(result)}'")
        else:
            print(f"  ❌ '{repr(input_text)}' -> '{repr(result)}' (expected '{repr(expected)}')")
            return False
    return True

def test_squeeze_spaces():
    """Test squeeze_spaces correctness"""
    from facet.lenses import squeeze_spaces

    test_cases = [
        ("Hello    World", "Hello World"),
        ("Line 1\nLine    2\t\t\tLine 3", "Line 1\nLine 2 Line 3"),
        ("No    changes", "No changes"),
        ("", ""),
    ]

    print("🧪 Testing squeeze_spaces...")
    for input_text, expected in test_cases:
        result = squeeze_spaces(input_text)
        if result == expected:
            print(f"  ✅ '{input_text}' -> '{result}'")
        else:
            print(f"  ❌ '{input_text}' -> '{result}' (expected '{expected}')")
            return False
    return True

def test_trim():
    """Test trim correctness"""
    from facet.lenses import trim

    test_cases = [
        ("  Hello World  ", "Hello World"),
        ("\t\tHello\t\t", "Hello"),
        ("No trim needed", "No trim needed"),
        ("   ", ""),
        ("", ""),
        ("\n\nHello\n\n", "Hello"),
    ]

    print("🧪 Testing trim...")
    for input_text, expected in test_cases:
        result = trim(input_text)
        if result == expected:
            print(f"  ✅ '{repr(input_text)}' -> '{repr(result)}'")
        else:
            print(f"  ❌ '{repr(input_text)}' -> '{repr(result)}' (expected '{repr(expected)}')")
            return False
    return True

def run_correctness_tests():
    """Run all correctness tests"""
    print("🚀 FACET SIMD Correctness Tests")
    print("=" * 40)

    tests = [
        test_normalize_newlines,
        test_dedent,
        test_squeeze_spaces,
        test_trim,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if test():
                passed += 1
                print("  ✅ PASSED\n")
            else:
                print("  ❌ FAILED\n")
        except Exception as e:
            print(f"  💥 ERROR: {e}\n")
            import traceback
            traceback.print_exc()

    print("=" * 40)
    print(f"📊 Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! SIMD optimizations are working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the implementations.")
        return False

if __name__ == "__main__":
    try:
        success = run_correctness_tests()
        sys.exit(0 if success else 1)
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("Install required packages:")
        print("pip install numba numpy")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
