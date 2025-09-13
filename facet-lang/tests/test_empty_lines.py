#!/usr/bin/env python3

import sys
sys.path.append('.')

from facet_lang import canonize
import json

# Test empty lines handling - must have no empty lines between facets
empty_lines_test = """@vars
  name: "Alex"
@user
  prompt: "Hello, {{name}}"
@assistant
  response: "Hi there!"
"""

print("Testing empty lines handling...")
try:
    result = canonize(empty_lines_test, resolve_mode="all")
    print("SUCCESS!")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()