from facet_lang import canonize

def run(text: str, **kw):
    return canonize(text, **kw)

def test_attrs_and_item_if_and_lens_kwargs():
    doc = """@user(role="Dev", if="true")
  request: "hi" |> trim
  list:
    - "a" (if="true")
    - "b" (if="false")
"""
    out = run(doc)
    assert "user" in out
    assert out["user"]["_attrs"]["role"] == "Dev"
    assert out["user"]["request"] == "hi"
    assert out["user"]["list"] == ["a"]

def test_negative_numbers_and_dash():
    doc = """@data
  a: -1
  b:
    - 1
    - -2
"""
    out = run(doc)
    assert out["data"]["a"] == -1
    assert out["data"]["b"] == [1, -2]

def test_vars_and_interpolation_and_types():
    doc = """@vars
  name: "Alex"
  retries: 3
@var_types
  name: { type: "string" }
  retries: { type: "int", min: 0, max: 5 }
@user
  prompt: "Hello, {{name}} x{{retries}}"
"""
    out = run(doc, resolve_mode="all")
    assert out["user"]["prompt"] == "Hello, Alex x3"


