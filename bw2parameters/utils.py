import asteval


def get_symbols(expression):
    interpreter = asteval.Interpreter()
    nf = asteval.NameFinder()
    nf.generic_visit(interpreter.parse(expression))
    return nf.names
