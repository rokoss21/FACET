#!/usr/bin/env python3

import sys
sys.path.append('.')

from facet_lang import canonize
import json

# Test fence blocks with indentation
fence_test = """@user
  code:
    ```python
    def hello():
        return "world"
    ``` |> dedent |> trim
  inline_code: ```print("hello")``` |> trim
"""

print("Testing fence blocks with indentation...")
try:
    result = canonize(fence_test)
    print("SUCCESS!")
    print("Indented fence result:", repr(result["user"]["code"]))
    print("Inline fence result:", repr(result["user"]["inline_code"]))
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()