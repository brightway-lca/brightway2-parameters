Brightway2-parameters: Use and evaluate parameters in Brightway2
================================================================

Use and data formats are most easily explained in an example:

.. code-block:: python

    In [1]: from bw2parameters import ParameterSet

    In [2]: ds = {
       ...:     'name': 'Some dataset',
       ...:     'parameters': [
       ...:         {
       ...:             'name': 'Deep_Thought',
       ...:             'amount': 42
       ...:         },
       ...:         {
       ...:             'name': 'East_River_Creature',
       ...:             'formula': '2 * Deep_Thought + 16'
       ...:         },
       ...:         {
       ...:             'name': 'Elders_of_Krikkit',
       ...:             'formula': 'sqrt(East_River_Creature)'
       ...:         },
       ...:     ],
       ...:     'exchanges': [
       ...:         {
       ...:            'parameter': 'Elders_of_Krikkit'
       ...:         },
       ...:         {
       ...:             'amount': 44
       ...:         }
       ...:     ]
       ...: }

    In [3]: ps = ParameterSet(ds['parameters'])

    In [4]: ps.evaluate()
    Out[4]: {'Deep_Thought': 42, 'East_River_Creature': 100, 'Elders_of_Krikkit': 10.0}

    In [5]: ps.evaluate_and_update_params()  # Updates the ``amount`` field in each parameter

    In [6]: ds['parameters']
    Out[6]:
        [
         {
            'amount': 42,
            'name': 'Deep_Thought'
         },
         {
            'amount': 100,
            'formula': '2 * Deep_Thought + 16',
            'name': 'East_River_Creature'
         },
         {
            'amount': 10.0,
            'formula': 'sqrt(East_River_Creature)',
            'name': 'Elders_of_Krikkit'
         }
        ]

    In [7]: ignored_value = ps(ds)  # Calling a ParameterSet object with a dataset will update exchanges

    In [8]: ds  # ``ds`` is changed even if you don't capture the returned value from ``ps(ds)``
    Out[8]:
        {'exchanges': [
            {
                'amount': 10.0,  # ``amount`` field added, value from parameter name
                'parameter': 'Elders_of_Krikkit'
            },
            {
                'amount': 44  # No parameter reference, so not touched
            }
         ],
         'name': 'Some dataset',
         'parameters': [
            {
                'amount': 42,
                'name': 'Deep_Thought'
            },
            {
                'amount': 100,
                'formula': '2 * Deep_Thought + 16',
                'name': 'East_River_Creature'
            },
            {
                'amount': 10.0,
                'formula': 'sqrt(East_River_Creature)',
                'name': 'Elders_of_Krikkit'
            }
         ]
        }

Note the following:

* Variables and formulas must be defined with unique names.
* Variable and formula names can't contradict the existing built-in functions. Available functions are documented in the `asteval documentation <http://newville.github.io/asteval/basics.html#built-in-functions>`__.
* Formulas should not include the equals sign; instead of ``{'formula': 'a = b + c', 'name': 'a'}`` do ``{'formula': 'b + c', 'name': 'a'}``.
* Formulas can only reference defined variables.
* Parameter sets are specific to a dataset - there is no inheritance across datasets, or global parameters.
* Monte Carlo is not yet implemented.
* If you call a ``ParameterSet`` with a different dataset than the initialization parameters, i.e. ``ParameterSet(some_parameters)(my_new_dataset)``, the parameters will be inserted into that dataset.

Brightway2-parameters is Python 2 & 3 compatible, has 100% test coverage, and is 2-clause BSD licensed and free. Source code `on bitbucket <https://bitbucket.org/cmutel/brightway2-parameters>`__.
