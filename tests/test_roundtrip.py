import json, glob, os, pytest
from facet import parser

EXAMPLES = glob.glob(os.path.join(os.path.dirname(__file__), "..", "examples", "*.facet"))

@pytest.mark.parametrize("path", EXAMPLES)
def test_roundtrip(path):
    text = open(path, encoding="utf-8").read()
    js = parser.to_json(text)
    data = json.loads(js)
    assert isinstance(data, dict)
