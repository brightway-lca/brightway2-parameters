from bw2parameters import mangle_formula


def test_mangle_formula():
    given = "log(foo * bar) + 7 / baz"
    prefix = "pre"
    assert mangle_formula(given, prefix, ['bar']) == '(log((pre__foo * bar)) + (7 / pre__baz))'
