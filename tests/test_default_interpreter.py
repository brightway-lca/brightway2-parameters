import pytest

from bw2parameters import DefaultInterpreter, MissingName


class TestInterpreter:
    Interpreter = DefaultInterpreter

    def test_init(self):
        i = self.Interpreter()
        assert "sqrt" in i.BUILTIN_SYMBOLS
        assert "log" in i.BUILTIN_SYMBOLS

    def test_add_symbols(self):
        i = self.Interpreter()
        i.add_symbols({"a": 1, "b": 2})
        assert i.user_defined_symbols() == {"a", "b"}

    def test_get_symbols(self):
        i = self.Interpreter()
        assert {'a', 'b', 'c'} == i.get_symbols('a * b + c')
        assert {'a', 'b', 'c', 'sqrt', 'log'} == i.get_symbols('a * 4 + 2.4 + sqrt(b) + log(a * c)')
        assert set() == i.get_symbols(None)

    def test_get_unknown_symbols(self, **kwargs):
        i = self.Interpreter()
        assert {'a', 'b', 'c'} == i.get_unknown_symbols('a * b + c', **kwargs)
        assert {'a', 'b', 'c'} == i.get_unknown_symbols('a * 4 + 2.4 + sqrt(b) + log(a * c)', **kwargs)
        assert {'a', 'b', 'c', 'sqrt', 'log'} == i.get_unknown_symbols('a * 4 + 2.4 + sqrt(b) + log(a * c)',
                                                                       ignore_symtable=True, **kwargs)
        assert {'a', 'b'} == i.get_unknown_symbols('a * b + c', known_symbols={'c'}, **kwargs)
        assert {'a', 'b'} == i.get_unknown_symbols('a * b + c', known_symbols={'c': 1}, **kwargs)
        assert {'a', 'b'} == i.get_unknown_symbols('a * b + c', known_symbols=['c'], **kwargs)
        assert {'a', 'b'} == i.get_unknown_symbols('a * b + c', known_symbols=('c',), **kwargs)
        assert set() == i.get_unknown_symbols(None, **kwargs)

    def test_eval(self):
        i = self.Interpreter()
        assert i.eval("1 + 1") == 2
        assert i("1 + 1") == 2
        with pytest.raises(MissingName):
            i("1 + a")
        # assert known_symbols added temporarily
        assert i("1 + a", known_symbols={"a": 2}) == 3
        with pytest.raises(MissingName):
            i("1 + a")
        # assert add_symbols added permanently
        i.add_symbols({"b": 3})
        with pytest.raises(MissingName):
            i("1 + a + b")
        assert i("1 + b") == 4
        assert i("1 + a + b", known_symbols={"a": 2}) == 6
