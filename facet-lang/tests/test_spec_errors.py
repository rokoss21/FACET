import pytest
from facet_lang import canonize
from facet_lang.errors import FacetError

def _canon(txt: str, **kw):
    return canonize(txt, **kw)

def test_F304_attr_interpolation_forbidden():
    doc = """@user(role="{{x}}")
  prompt: "ok"
"""
    with pytest.raises(FacetError) as e:
        _canon(doc)
    assert e.value.code == "F304"

def test_F704_if_must_be_quoted():
    doc = """@user(if=true)
  prompt: "ok"
"""
    with pytest.raises(FacetError) as e:
        _canon(doc)
    assert e.value.code == "F704"

def test_F404_forward_ref_in_vars():
    doc = """@vars
  a: $b
"""
    with pytest.raises(FacetError) as e:
        _canon(doc, resolve_mode="all")
    assert e.value.code == "F404"

def test_F601_import_not_allowed():
    doc = """@import(path="/etc/passwd")
"""
    with pytest.raises(FacetError) as e:
        _canon(doc, import_roots=["samples"]) 
    assert e.value.code == "F601"

