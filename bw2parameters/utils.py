import asteval


def _get_existing_symbols():
    interpreter = asteval.Interpreter()
    return set(interpreter.symtable)

EXISTING_SYMBOLS = _get_existing_symbols()


def get_symbols(expression):
    interpreter = asteval.Interpreter()
    nf = asteval.NameFinder()
    nf.generic_visit(interpreter.parse(expression))
    return set(nf.names).difference(EXISTING_SYMBOLS)


try:
    # Python 2
    basestring
    def isstr(s):
        return isinstance(s, basestring)
except NameError:
    # Python 3
    def isstr(s):
        return isinstance(s, str)
