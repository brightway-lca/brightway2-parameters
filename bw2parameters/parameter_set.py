from . import get_expression, test_no_circular_references


class ParameterSet(object):
    def __init__(self, ds):
        self.ds = ds

    def validate(self):
        pass
