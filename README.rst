Brightway2 parameters
=====================

Library for storing, validating, and calculating with parameters.

Approach:

- Parameters are defined in a dataset: ds['parameters']
- No global parameters
- No inheritance between datasets

Data format:
- ds['parameters'] is a list of parameters
- 'name' field (must be unique)
    - 'name' can be generated automatically on import
    - 'name' can't copy function names (long list)
- optional 'formula' field
- 'formula' must use numpy (i.e. array) compatible functions
- Parameters have normal uncertainty fields
- An exchange can reference a parameter name (but not a formula)
    - No uncertainty if referencing a parameter

Processing:

- ParameterSet object
    - New asteval instance for each parameter set
- Need to get order of parameters to be processed
- MC needs an efficient way to insert values into various RNG output arrays
    - Do we need a new unique ID per exchange? Exchange input/output not guaranteed unique
    - Or somehow do something tricky during processing step?
    - Rewrite main MonteCarlo class to have view into PV lca?
