Brightway2 parameters
=====================

|Coverage Status| |Build status| |Documentation Status|

Library for storing, validating, and calculating with parameters.
Designed to work with the `Brightway2 life cycle assessment
framework <https://brightwaylca.org>`__, but is generic enough to work
in other use cases.

::

    In [1]: from bw2parameters import ParameterSet

    In [2]: parameters = {
       ...:        'Deep_Thought': {'amount': 42},
       ...:        'East_River_Creature': {'formula': '2 * Deep_Thought + 16'},
       ...:        'Elders_of_Krikkit': {'formula': 'sqrt(East_River_Creature)'},
       ...: }

    In [3]: ParameterSet(parameters).evaluate()
    Out[3]: {'Deep_Thought': 42, 'East_River_Creature': 100, 'Elders_of_Krikkit': 10.0}

Compatible with Python 2.7, 3.3, and 3.4. 100% test coverage. `Source
code on
bitbucket <https://bitbucket.org/cmutel/brightway2-parameters>`__,
documentation on `Read the
Docs <https://brightway2-parameters.readthedocs.io/>`__.

.. |Coverage Status| image:: https://coveralls.io/repos/bitbucket/cmutel/brightway2-parameters/badge.svg?branch=master
   :target: https://coveralls.io/bitbucket/cmutel/brightway2-parameters?branch=master
.. |Build status| image:: https://ci.appveyor.com/api/projects/status/9ynu6gd9nk26mx2i?svg=true
   :target: https://ci.appveyor.com/project/cmutel/brightway2-parameters
.. |Documentation Status| image:: https://readthedocs.org/projects/brightway2-parameters/badge/?version=latest
   :target: http://brightway2-parameters.readthedocs.io/?badge=latest
