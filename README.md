# Brightway2 parameters

Library for storing, validating, and calculating with parameters. Designed to work with the [Brightway2 life cycle assessment framework](https://brightwaylca.org), but is generic enough to work in other use cases.

    In [1]: from bw2parameters import ParameterSet

    In [2]: parameters = {
       ...:        'Deep_Thought': {'amount': 42},
       ...:        'East_River_Creature': {'formula': '2 * Deep_Thought + 16'},
       ...:        'Elders_of_Krikkit': {'formula': 'sqrt(East_River_Creature)'},
       ...: }

    In [3]: ParameterSet(parameters).evaluate()
    Out[3]: {'Deep_Thought': 42, 'East_River_Creature': 100, 'Elders_of_Krikkit': 10.0}

Compatible with Python 2.7 and 3.3+. 100% test coverage. [Source code on Github](https://github.com/brightway-lca/brightway2-parameters), documentation on [Read the Docs](https://brightway2-parameters.readthedocs.io/).
