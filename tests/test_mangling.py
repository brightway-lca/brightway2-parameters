from bw2parameters import *


def test_mangle_formula():
    given = "log(foo * bar) + 7 / baz"
    prefix = "pre"
    assert (
        mangle_formula(given, prefix, ["bar"])
        == "(log((pre__foo * bar)) + (7 / pre__baz))"
    )


def test_prefix_parameter_dict():
    given = {
        "a": {"formula": "a + b / c", "foo": True},
        "b": {"formula": "2 * a - exp(7 - b)"},
        "catch": {},
    }
    expected = {
        "t_a": {"formula": "(t_a + (t_b / c))", "foo": True, "original": "a"},
        "t_b": {"formula": "((2 * t_a) - exp((7 - t_b)))", "original": "b"},
        "t_catch": {"original": "catch"},
    }
    substitutions = {"a": "t_a", "b": "t_b", "catch": "t_catch"}
    assert prefix_parameter_dict(given, "t_") == (expected, substitutions)


def test_chain_prefix_parameter_dict():
    given = {"a": {"formula": "a + b / c"}}
    g_copy = {"a": {"formula": "a + b / c"}}
    expected = {
        "t_a": {"formula": "(t_a + (b / c))", "original": "a"},
    }
    substitutions = {"a": "t_a"}
    assert prefix_parameter_dict(given, "t_") == (expected, substitutions)
    assert given == g_copy
    given, _ = prefix_parameter_dict(given, "t_")
    s1 = {"b": "dog"}
    r1 = substitute_in_formulas(given, s1)
    expected = {"t_a": {"formula": "(t_a + (dog / c))", "original": "a"}}
    assert r1 == expected

    s2 = {"c": "cat"}
    r2 = substitute_in_formulas(r1, s2)
    expected = {"t_a": {"formula": "(t_a + (dog / cat))", "original": "a"}}
    assert r2 == expected
