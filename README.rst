Brightway2 parameters
=====================

Library for storing, validating, and calculating with parameters. Designed to work with the `Brightway2 life cycle assessment framework <http://brightway2.readthedocs.org/en/latest/>`__, but should work for other use cases.

Compatible with Python 2 & 3, tested on 2.7, 3.3, and 3.4. 100% test coverage. `Source code on bitbucket <https://bitbucket.org/cmutel/brightway2-parameters>`__, documentation on `Read the Docs <http://brightway2-parameters.readthedocs.org/>`__.

Todo:

    * Show where there are circular references
    * MC needs an efficient way to insert values into various RNG output arrays
        * Do we need a new unique ID per exchange? Exchange input/output not guaranteed unique
        * Or somehow do something tricky during processing step?
        * Rewrite main MonteCarlo class to have view into PV lca?
