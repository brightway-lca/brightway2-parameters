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
