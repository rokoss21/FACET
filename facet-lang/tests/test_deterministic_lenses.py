from facet_lang.lenses import choose, shuffle

def test_choose_seeded():
    xs = ["a","b","c"]
    assert choose(xs, seed=42) in xs
    assert choose(xs, seed=42) == choose(xs, seed=42)

def test_shuffle_seeded():
    xs = [1,2,3,4,5]
    a = shuffle(xs, seed=123)
    b = shuffle(xs, seed=123)
    assert a == b and sorted(a) == xs
