# parameters Changelog

## 1.1.0 (2023-04-17)

- Require `pint` dependency
- Fix regression: `DefaultParameterSet` -> `ParameterSet`
- New packaging based on Brightway

## 1.0.0 (2023-01-27)

- BREAKING CHANGE: Dropping Python 2.7 support
- Introduce new class PintParameterSet for solving formulas with units

## 0.7.1 (2023-01-25)

- Fix tests: must set loc in all monte carlo runs
- minor (black) reformatting and isorting
- introduce github workflow for automated testing

## 0.7 (2021-12-25)

- Improve handling of errors in `ParameterSet.evaluate_monte_carlo` so that an array is returned even when the interpreter fails.

## 0.6.6 (2018-11-11)

Return global parameters from `evaluate`, to be consistent with `evaluate_monte_carlo`

## 0.6.5 (2018-4-19)

Allow Numpy arrays in local amount values

## 0.6.4 (2018-02-16)

- Add some extra functionality for presamples

## 0.6.3 (2018-02-14)

- Allow `global_params` to be Numpy arrays

### 0.6.2.1 (2018-02-13)

- Removed extraneous print statement

## 0.6.2 (2018-02-12)

- Add `prefix_parameter_dict` and `substitute_in_formulas` for better symbol name mangling

### 0.6.1.2 (2017-10-19)

- Packaging fix

## 0.6 (2017-10-19)

- Add Monte Carlo sampling to parameter sets
- Add Windows and Linux CI
- Add Coveralls test coverage

### 0.5.3 (2017-04-17)

- Fix license text

### 0.5.2 (2016-08-17)

- Remove scipy dependency

### 0.5.1 (2016-04-12)

- Correct asteval dependency version

## 0.5 (2016-04-12)

- Correct when CapitalizationError is raised, and make error messages more useful

## 0.4 (2015-05-20)

- Global parameters

## 0.3 (2015-04-10)

- Fix adding amount to list of exchanges
- More informative error messages
- Improve validity checks

## 0.2 (2015-02-06)

- Complete tests coverage
- Improved docs

## 0.1 (2015-02-02)

Initial checkin
