#!/usr/bin/env python3

import sys
sys.path.append('.')

from facet_lang import canonize
import json

def test_empty_lines_between_facets():
    """Test 1: Empty lines between facets should now work"""
    print("🧪 Test 1: Empty lines between facets")
    
    doc_with_empty_lines = """@vars
  name: "Alex"
  mode: "expert"

@user
  prompt: "Hello, {{name}}!"

@assistant
  response: "Hi there!"
"""
    
    try:
        result = canonize(doc_with_empty_lines, resolve_mode="all")
        print("✅ PASSED - Empty lines between facets work")
        return True
    except Exception as e:
        print(f"❌ FAILED - {e}")
        return False

def test_multiline_fence_blocks():
    """Test 2: Multiline fence blocks should now work"""
    print("\n🧪 Test 2: Multiline fence blocks")
    
    doc_with_fence = """@user
  code:
    ```python
    def hello(name):
        return f"Hello, {name}!"
    
    print(hello("World"))
    ``` |> dedent |> trim
  inline_code: ```print("test")``` |> trim
"""
    
    try:
        result = canonize(doc_with_fence)
        code_result = result["user"]["code"]
        inline_result = result["user"]["inline_code"]
        
        # Check that multiline fence was processed
        if "def hello" in code_result and "print(hello" in code_result:
            print("✅ PASSED - Multiline fence blocks work")
            print(f"   Multiline result: {repr(code_result[:50])}...")
            print(f"   Inline result: {repr(inline_result)}")
            return True
        else:
            print(f"❌ FAILED - Fence content incorrect: {repr(code_result)}")
            return False
    except Exception as e:
        print(f"❌ FAILED - {e}")
        import traceback
        traceback.print_exc()
        return False

def test_complex_conditions():
    """Test 3: Complex conditions in if attributes should now work"""
    print("\n🧪 Test 3: Complex conditions in if attributes")
    
    doc_with_complex_conditions = """@vars
  user_level: "expert" 
  environment: "production"
  features: ["advanced", "debug"]

@section(if="user_level == 'expert' and environment == 'production'")
  title: "Expert Production Settings"
  
@debug_info(if="'debug' in features")
  enabled: true
  
@simple(if="user_level == expert")
  note: "Simple comparison without quotes"
"""
    
    try:
        result = canonize(doc_with_complex_conditions, resolve_mode="all")
        
        # Check that complex conditions work
        has_section = "section" in result
        has_debug = "debug_info" in result  
        has_simple = "simple" in result
        
        if has_section and has_debug and has_simple:
            print("✅ PASSED - Complex conditions work")
            print(f"   Found facets: {list(result.keys())}")
            return True
        else:
            print(f"❌ FAILED - Expected all facets but got: {list(result.keys())}")
            return False
    except Exception as e:
        print(f"❌ FAILED - {e}")
        return False

def test_smart_imports():
    """Test 4: Smart import allowlist should auto-detect project structure"""  
    print("\n🧪 Test 4: Smart import allowlist")
    
    # First create a sample import file
    with open("samples/test_import.facet", "w") as f:
        f.write("""@shared
  common_setting: "shared_value"
  
@template
  greeting: "Hello from shared template!"
""")
    
    doc_with_import = """@import "samples/test_import.facet"

@vars
  name: "Alex"

@user
  prompt: "{{name}}: {{template.greeting}}"
"""
    
    try:
        # Test with auto-detected allowlist (should work)
        result = canonize(doc_with_import, resolve_mode="all")
        
        if "shared" in result and "user" in result:
            print("✅ PASSED - Smart import allowlist works")
            print(f"   Imported facets: {[k for k in result.keys() if k != 'user']}")
            
            # Clean up
            import os
            os.remove("samples/test_import.facet")
            return True
        else:
            print(f"❌ FAILED - Import didn't work: {list(result.keys())}")
            return False
    except Exception as e:
        print(f"❌ FAILED - {e}")
        # Clean up on failure too
        try:
            import os
            os.remove("samples/test_import.facet")
        except:
            pass
        return False

def test_all_together():
    """Test 5: All features together"""
    print("\n🧪 Test 5: All architectural fixes together")
    
    comprehensive_doc = """@vars
  name: "Alice"
  level: "expert"
  code_langs: ["python", "javascript"]

@system(if="level == 'expert'")
  role: "Advanced AI Assistant"
  
@user
  greeting: "Hello {{name}}!"
  
  code_example:
    ```python
    # Example for {{name}}
    def greet(name):
        return f"Hello, {name}!"
    
    result = greet("{{name}}")
    print(result)
    ``` |> dedent |> trim
    
  features:
    - "Advanced mode enabled" (if="level == 'expert'")
    - "Python support" (if="'python' in code_langs")
    - "Basic mode" (if="level == 'beginner'")

@output
  format: "structured"
"""
    
    try:
        result = canonize(comprehensive_doc, resolve_mode="all")
        
        # Check all features
        checks = [
            "system" in result,  # Conditional facet worked
            "user" in result,    # Main content
            "Hello Alice!" in result["user"]["greeting"],  # Interpolation
            "def greet" in result["user"]["code_example"],  # Multiline fence
            len(result["user"]["features"]) == 2,  # Conditional list items (expert + python, not beginner)
            "output" in result   # Regular facet
        ]
        
        if all(checks):
            print("✅ PASSED - All architectural fixes work together!")
            print(f"   Final facets: {list(result.keys())}")
            print(f"   User features count: {len(result['user']['features'])}")
            return True
        else:
            print(f"❌ FAILED - Some checks failed: {checks}")
            print(f"   Result: {json.dumps(result, indent=2)[:300]}...")
            return False
    except Exception as e:
        print(f"❌ FAILED - {e}")
        import traceback
        traceback.print_exc()
        return False

def run_all_tests():
    print("🚀 Running all architectural fix tests...\n")
    
    tests = [
        test_empty_lines_between_facets,
        test_multiline_fence_blocks, 
        test_complex_conditions,
        test_smart_imports,
        test_all_together
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    passed = sum(results)
    total = len(results)
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL ARCHITECTURAL FIXES WORKING PERFECTLY!")
        return True
    else:
        print("❌ Some fixes need more work")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)