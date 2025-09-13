#!/usr/bin/env python3

import sys
sys.path.append('.')

from facet_lang import canonize
import json

complex_doc = """@vars
  seed: 42
  mode: "expert"
  username: "Alex"
  greeting_choices: ["hi","hello","hey"]
  greeting: $greeting_choices |> choose(seed=42)
@user
  prompt: "Hello, {{username}}! Mode={{mode}}. Greeting={{greeting}}."
  examples:
    - &ex { q: "What is recursion?", a: "Recursion is calling itself." }
    - *ex
  code: ```
def f(x):
  return x*x
``` |> dedent |> trim
  list:
    - "alpha" (if="true")
    - "beta" (if="false")
@plan(role=Architect, if="true")
  steps:
    - "Intro"
    - "Deep dive" |> upper
"""

print("Testing complex document without import...")
try:
    result = canonize(complex_doc, resolve_mode='all')
    print("SUCCESS!")
    print(json.dumps(result, indent=2, ensure_ascii=False))
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()