import json
from facet_lang import canonize

def test_smoke_canonize_runs():
    out = canonize("""@user\n  request: \"Hello\"\n""")
    assert isinstance(out, dict)
