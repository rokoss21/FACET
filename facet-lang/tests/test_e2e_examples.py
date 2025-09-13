from facet_lang import canonize

def test_e2e_vars_types_if_list_and_lenses():
    doc = """@vars
  username: "Alex"
  retries: 3
  env: "prod"
  greeting_choices: ["hi","hello","hey"]
@var_types
  username: { type: "string" }
  retries:  { type: "int", min: 0, max: 5 }
  env:      { type: "string", enum: ["dev","staging","prod"] }
@user
  prompt: "Hello, {{username}}! Env={{env}}. Retries={{retries}}."
  list:
    - "hi" (if="true")
    - "x" (if="false")
"""
    out = canonize(doc, resolve_mode="all")
    assert out["user"]["prompt"].startswith("Hello, Alex!")
    assert out["user"]["list"] == ["hi"]

