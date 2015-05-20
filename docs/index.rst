Brightway2-parameters: Use and evaluate parameters in Brightway2
================================================================

The simplest case is to evaluate a system of variables and formulas:

.. code-block:: python

    In [1]: from bw2parameters import ParameterSet

    In [2]: parameters = {
       ...:        'Deep_Thought': {'amount': 42},
       ...:        'East_River_Creature': {'formula': '2 * Deep_Thought + 16'},
       ...:        'Elders_of_Krikkit': {'formula': 'sqrt(East_River_Creature)'},
       ...: }

    In [3]: ParameterSet(parameters).evaluate()
    Out[3]: {'Deep_Thought': 42, 'East_River_Creature': 100, 'Elders_of_Krikkit': 10.0}

You can also use and reference global constants. This is useful when sharing some values across several sets of formulas:

.. code-block:: python

    In [4]: parameters = {
       ...:        'East_River_Creature': {'formula': '2 * Deep_Thought + 16'},
       ...:        'Elders_of_Krikkit': {'formula': 'sqrt(East_River_Creature)'},
       ...: }

    In [5]: global_parameters = {'Deep_Thought': 42}

    In [6]: ParameterSet(parameters, global_parameters).evaluate()
    Out[6]: {'East_River_Creature': 100, 'Elders_of_Krikkit': 10.0}

You can call a ``ParameterSet`` with a list of new variables and formulas. Note that this new list cannot have reference to itself, only to the parameter set defined earlier. Calling set the ``amount`` field in the new list:

.. code-block:: python

    In [7]: another_parameter_list = [
       ...:     {'formula': 'East_River_Creature + Elders_of_Krikkit'},
       ...:     {'formula': '42 - Elders_of_Krikkit'},
       ...:     {'something else': "won't change"}
       ...: ]

    In [8]: ps = ParameterSet(parameters, global_parameters)

    In [9]: ps(another_parameter_list)
    Out[9]:
    [{u'amount': 110.0, 'formula': 'East_River_Creature + Elders_of_Krikkit'},
     {u'amount': 32.0, 'formula': '42 - Elders_of_Krikkit'},
     {'something else': "won't change"}]

Finally, you can modify the parameters dictionary by adding an ``amount`` field to all formula parameters:

.. code-block:: python

    In [10]: ParameterSet(parameters, global_parameters).evaluate_and_set_amount_field()
    Out[10]: {'East_River_Creature': 100, 'Elders_of_Krikkit': 10.0}

    In [11]: parameters
    Out[11]:
    {'East_River_Creature': {u'amount': 100, 'formula': '2 * Deep_Thought + 16'},
     'Elders_of_Krikkit': {u'amount': 10.0, 'formula': 'sqrt(East_River_Creature)'}}

Note the following:

* Variables and formulas must be defined with unique names.
* Variable and formula names can't contradict the existing built-in functions. Available functions are documented in the `asteval documentation <http://newville.github.io/asteval/basics.html#built-in-functions>`__.
* Formulas should not include the equals sign; instead of ``{'formula': 'a = b + c', 'name': 'a'}`` do ``{'formula': 'b + c', 'name': 'a'}``.
* Formulas can only reference defined variables.

Brightway2-parameters is Python 2.7 & 3.3/3.4 compatible, has 100% test coverage, and is 2-clause BSD licensed and free. Source code `on bitbucket <https://bitbucket.org/cmutel/brightway2-parameters>`__.
