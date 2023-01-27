# -*- coding: utf-8 -*-
import sys

import numpy as np
import pytest

from bw2parameters import ParameterSet
from bw2parameters.errors import (
    CapitalizationError,
    DuplicateName,
    ParameterError,
    SelfReference,
)
from bw2parameters.utils import get_symbols, isidentifier


class TestParameterSet:
    ParameterSet = ParameterSet

    def test_call_updates_exchanges(self):
        ds = {
            'name': 'Some dataset',
            'parameters': {
                'Deep_Thought': {'amount': 42},
                'East_River_Creature': {'formula': '2 * Deep_Thought + 16'},
                'Elders_of_Krikkit': {'formula': 'sqrt(East_River_Creature)'},
            },
            'exchanges': [
                {'formula': 'Elders_of_Krikkit'},
                {'amount': 44}
            ]
        }
        self.ParameterSet(ds['parameters'])(ds['exchanges'])
        assert ds['parameters']['East_River_Creature'] == {'amount': 100, 'formula': '2 * Deep_Thought + 16'}
        assert ds['exchanges'][0] == {'amount': 10, 'formula': 'Elders_of_Krikkit'}
        assert ds['exchanges'][1] == {'amount': 44}

    def test_call_no_exchanges(self):
        ds = {
            'parameters': {
                'Deep_Thought': {'amount': 42},
                'East_River_Creature': {'formula': '2 * Deep_Thought + 16'},
                'Elders_of_Krikkit': {'formula': 'sqrt(East_River_Creature)'},
            }
        }
        ds = self.ParameterSet(ds['parameters'])(ds)
        assert 'exchanges' not in ds

    def test_find_symbols(self):
        assert {'a', 'b', 'c'} == get_symbols('a * b + c')
        assert {'a', 'b', 'c'} == get_symbols('a * 4 + 2.4 + sqrt(b) + log(a * c)')

    def test_isidentifier(self):
        assert isidentifier('foo')
        assert isidentifier('foo1_23')
        assert not isidentifier('pass')  # syntactically correct keyword
        assert not isidentifier('foo ')  # trailing whitespace
        assert not isidentifier(' foo')  # leading whitespace
        assert not isidentifier('1234')  # number
        assert not isidentifier('1234abc')  # number and letters
        assert not isidentifier(u'👻')  # Unicode not from allowed range
        assert not isidentifier('')  # empty string
        assert not isidentifier('   ')  # whitespace only
        assert not isidentifier('foo bar')  # several tokens
        assert not isidentifier('no-dashed-names-for-you')  # no such thing in Python

        if sys.version_info < (3, 0):
            # Unicode identifiers are only allowed in Python 3:
            assert not isidentifier(u'℘᧚')
        else:
            # Unicode identifiers are only allowed in Python 3:
            assert isidentifier(u'℘᧚')

        with pytest.raises(TypeError):
            isidentifier(3)

    def test_simple_evaluation(self):
        params = {
            'Agrajag': {'amount': 3.14},
            'Constant_Mown': {'amount': 0.001},
            'Deep_Thought': {'amount': 42},
            'East_River_Creature': {'formula': '2 * Agrajag ** 2'},
            'Eccentrica_Gallumbits': {'formula': '1 / sqrt(Constant_Mown)'},
            'Elders_of_Krikkit': {
                'formula': 'East_River_Creature + Eccentrica_Gallumbits'
            },
            'Emily_Saunders': {'formula': 'sin(Deep_Thought) + 7 - Elders_of_Krikkit'},
            'Gag_Halfrunt': {
                'formula': 'Deep_Thought + Constant_Mown - log10(abs(Emily_Saunders))'
            },
            'Gargravarr': {
                'formula': ('Agrajag + Constant_Mown + Deep_Thought + '
                            'East_River_Creature + Eccentrica_Gallumbits + '
                            'Elders_of_Krikkit + Emily_Saunders + Gag_Halfrunt')}
        }
        self.ParameterSet(params).evaluate()

    def test_evaluation_values(self):
        params = {
            'Deep_Thought': {'amount': 42},
            'East_River_Creature': {'formula': '2 * Deep_Thought + 16'},
            'Elders_of_Krikkit': {'formula': 'sqrt(East_River_Creature)'},
        }
        ps = self.ParameterSet(params)
        assert ps.evaluate() == {'Deep_Thought': 42, 'Elders_of_Krikkit': 10, 'East_River_Creature': 100}

    def test_evaluate_update_values(self):
        params = {
            'Deep_Thought': {'amount': 42},
            'East_River_Creature': {'formula': '2 * Deep_Thought + 16'},
            'Elders_of_Krikkit': {'formula': 'sqrt(East_River_Creature)'},
        }
        self.ParameterSet(params).evaluate_and_set_amount_field()
        assert params['East_River_Creature']['amount'] == 100
        assert params['Elders_of_Krikkit']['amount'] == 10

    def test_not_dict(self):
        with pytest.raises(ValueError):
            self.ParameterSet([])
        with pytest.raises(ValueError):
            self.ParameterSet({'Deep Thought': 42})

    def test_missing_fields(self):
        with pytest.raises(ValueError):
            self.ParameterSet({'': {}})
        with pytest.raises(ValueError):
            self.ParameterSet([
                {'amount': 1, 'name': 'Gag_Halfrunt'},
                {'name': 'Emily_Saunders'}
            ])
        with pytest.raises(ValueError):
            self.ParameterSet([
                {'formula': 'foo', 'name': 'Deep_Thought'},
                {'name': 'Constant_Mown'}
            ])

    def test_space_in_name(self):
        self.ParameterSet({'Deep_Thought': {'amount': 42}})
        with pytest.raises(ValueError):
            self.ParameterSet({'Deep Thought': {'amount': 42}})

    def test_name_in_existing_symbols(self):
        with pytest.raises(DuplicateName):
            self.ParameterSet({'log': {'amount': 1}})

    def test_self_reference(self):
        with pytest.raises(SelfReference):
            self.ParameterSet({'Elders_of_Krikkit': {'formula': '2 * Elders_of_Krikkit'}})

    def test_missing_reference(self):
        with pytest.raises(ParameterError):
            self.ParameterSet({'Elders_of_Krikkit': {'formula': '2 * Ford_Prefect'}})

    def test_circular_reference(self):
        with pytest.raises(ParameterError):
            self.ParameterSet({
                'Elders_of_Krikkit': {'formula': '2 * Agrajag'},
                'East_River_Creature': {'formula': '2 * Elders_of_Krikkit'},
                'Agrajag': {'formula': '2 * East_River_Creature'},
            })

    def test_capitaliation_error(self):
        with pytest.raises(CapitalizationError):
            self.ParameterSet({
                'Elders_of_Krikkit': {'formula': '2 * Agrajag'},
                'agrajag': {'amount': 2},
            })

    def test_non_numeric(self):
        with pytest.raises(ValueError):
            self.ParameterSet({
                'East_River_Creature': {'formula': '2 * Deep_Thought + 16'},
                'Elders_of_Krikkit': {'formula': 'sqrt(East_River_Creature)'},
            }, {'Deep Thought': 'Thought'})

    def test_local_params_arrays_allowed(self):
        self.ParameterSet({
            'East_River_Creature': {'formula': '2 * Deep_Thought + 16'},
            'Elders_of_Krikkit': {'amount': np.arange(5)},
        }, {'Deep_Thought': 5})

    def test_global_params_arrays_allowed(self):
        self.ParameterSet({
            'East_River_Creature': {'formula': '2 * Deep_Thought + 16'},
            'Elders_of_Krikkit': {'formula': 'sqrt(East_River_Creature)'},
        }, {'Deep_Thought': np.arange(5)})

    def test_nonidentifier(self):
        with pytest.raises(ValueError):
            self.ParameterSet({
                'East_River_Creature': {'formula': '2 * Deep_Thought + 16'},
                'Elders_of_Krikkit': {'formula': 'sqrt(East_River_Creature)'},
            }, {'Deep Thought': 2.4})

    def test_evaluate(self):
        ps = self.ParameterSet({
            'East_River_Creature': {'formula': '2 * Deep_Thought + 16'},
            'Elders_of_Krikkit': {'formula': 'sqrt(East_River_Creature)'},
        }, {'Deep_Thought': 42})
        assert ps.evaluate() == {
            'East_River_Creature': 100,
            'Elders_of_Krikkit': 10,
            'Deep_Thought': 42,
        }
