#!/usr/bin/env python3

import sys
sys.path.append('.')

from facet_lang import canonize
import json

# Test improved anchor handling
anchor_test = """@examples
  templates:
    - &template { name: "example", type: "demo", value: 42 }
    - *template
    - { name: "other", type: "test", value: 99 }
  referenced: *template
"""

print("Testing improved anchor handling...")
try:
    result = canonize(anchor_test)
    print("SUCCESS!")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # Check that anchors are not visible in output
    examples = result["examples"]
    assert "&" not in str(examples), "Anchors should not be visible in output"
    
    # Check that first and second items are the same (reference worked)
    assert examples["templates"][0] == examples["templates"][1], "Anchor reference failed"
    
    # Check that referenced item is the same as the template
    assert examples["templates"][0] == examples["referenced"], "Top-level reference failed"
    
    print("✅ All anchor tests passed!")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()