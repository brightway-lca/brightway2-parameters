# -*- coding: utf-8 -*-
from .. import ParameterSet
from ..errors import *
from ..utils import get_symbols, isidentifier
import sys
import unittest


class CallParameterSetTestCase(unittest.TestCase):
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
        ParameterSet(ds['parameters'])(ds['exchanges'])
        self.assertEqual(
            ds['parameters']['East_River_Creature'],
            {'amount': 100, 'formula': '2 * Deep_Thought + 16'}
        )
        self.assertEqual(ds['exchanges'][0], {'amount': 10, 'formula': 'Elders_of_Krikkit'})
        self.assertEqual(ds['exchanges'][1], {'amount': 44})

    def test_call_no_exchanges(self):
        ds = {
            'parameters': {
                'Deep_Thought': {'amount': 42},
                'East_River_Creature': {'formula': '2 * Deep_Thought + 16'},
                'Elders_of_Krikkit': {'formula': 'sqrt(East_River_Creature)'},
            }
        }
        ds = ParameterSet(ds['parameters'])(ds)
        self.assertFalse('exchanges' in ds)


class UtilTestCase(unittest.TestCase):
    def test_find_symbols(self):
        self.assertEqual(
            {'a', 'b', 'c'},
            get_symbols('a * b + c')
        )
        self.assertEqual(
            {'a', 'b', 'c'},
            get_symbols('a * 4 + 2.4 + sqrt(b) + log(a * c)')
        )

    def test_isidentifier(self):
        self.assertTrue(isidentifier('foo'))
        self.assertTrue(isidentifier('foo1_23'))
        self.assertFalse(isidentifier('pass'))    # syntactically correct keyword
        self.assertFalse(isidentifier('foo '))    # trailing whitespace
        self.assertFalse(isidentifier(' foo'))    # leading whitespace
        self.assertFalse(isidentifier('1234'))    # number
        self.assertFalse(isidentifier('1234abc')) # number and letters
        self.assertFalse(isidentifier(u'👻'))      # Unicode not from allowed range
        self.assertFalse(isidentifier(''))        # empty string
        self.assertFalse(isidentifier('   '))     # whitespace only
        self.assertFalse(isidentifier('foo bar')) # several tokens
        self.assertFalse(isidentifier('no-dashed-names-for-you')) # no such thing in Python

        if sys.version_info < (3, 0):
            # Unicode identifiers are only allowed in Python 3:
            self.assertFalse(isidentifier(u'℘᧚'))
        else:
            # Unicode identifiers are only allowed in Python 3:
            self.assertTrue(isidentifier(u'℘᧚'))

        with self.assertRaises(TypeError):
            isidentifier(3)


class EvaluationTestCase(unittest.TestCase):
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
        ParameterSet(params).evaluate()

    def test_evaluation_values(self):
        params = {
            'Deep_Thought': {'amount': 42},
            'East_River_Creature': {'formula': '2 * Deep_Thought + 16'},
            'Elders_of_Krikkit': {'formula': 'sqrt(East_River_Creature)'},
        }
        ps = ParameterSet(params)
        self.assertEqual(
            {'Deep_Thought': 42, 'Elders_of_Krikkit': 10, 'East_River_Creature': 100},
            ps.evaluate()
        )

    def test_evaluate_update_values(self):
        params = {
            'Deep_Thought': {'amount': 42},
            'East_River_Creature': {'formula': '2 * Deep_Thought + 16'},
            'Elders_of_Krikkit': {'formula': 'sqrt(East_River_Creature)'},
        }
        ParameterSet(params).evaluate_and_set_amount_field()
        self.assertEqual(params['East_River_Creature']['amount'], 100)
        self.assertEqual(params['Elders_of_Krikkit']['amount'], 10)


class BasicValidationTestCase(unittest.TestCase):
    def test_not_dict(self):
        with self.assertRaises(ValueError):
            ps = ParameterSet([])

    def test_missing_fields(self):
        with self.assertRaises(ValueError):
            ps = ParameterSet({'': {}})
        with self.assertRaises(ValueError):
            ps = ParameterSet([
                {'amount': 1, 'name': 'Gag_Halfrunt'},
                {'name': 'Emily_Saunders'}
            ])
        with self.assertRaises(ValueError):
            ps = ParameterSet([
                {'formula': 'foo', 'name': 'Deep_Thought'},
                {'name': 'Constant_Mown'}
            ])

    def test_not_dict(self):
        with self.assertRaises(ValueError):
            ps = ParameterSet({'Deep Thought': 42})

    def test_space_in_name(self):
        ps = ParameterSet({'Deep_Thought': {'amount': 42}})
        with self.assertRaises(ValueError):
            ps = ParameterSet({'Deep Thought': {'amount': 42}})

    def test_name_in_existing_symbols(self):
        with self.assertRaises(DuplicateName):
            ps = ParameterSet({'log': {'amount': 1}})

    def test_self_reference(self):
        with self.assertRaises(SelfReference):
            ParameterSet({'Elders_of_Krikkit': {'formula': '2 * Elders_of_Krikkit'}})

    def test_missing_reference(self):
        with self.assertRaises(ParameterError):
            ps = ParameterSet({'Elders_of_Krikkit': {'formula': '2 * Ford_Prefect'}})

    def test_circular_reference(self):
        with self.assertRaises(ParameterError):
            ps = ParameterSet({
                'Elders_of_Krikkit': {'formula': '2 * Agrajag'},
                'East_River_Creature': {'formula': '2 * Elders_of_Krikkit'},
                'Agrajag': {'formula': '2 * East_River_Creature'},
            })

    def test_capitaliation_error(self):
        with self.assertRaises(CapitalizationError):
            ps = ParameterSet({
                'Elders_of_Krikkit': {'formula': '2 * Agrajag'},
                'agrajag': {'amount': 2},
            })


class GlobalParametersTestCase(unittest.TestCase):
    def test_non_numeric(self):
        with self.assertRaises(ValueError):
            ps = ParameterSet({
                'East_River_Creature': {'formula': '2 * Deep_Thought + 16'},
                'Elders_of_Krikkit': {'formula': 'sqrt(East_River_Creature)'},
            }, {'Deep': 'Thought'})

    def test_nonidentifier(self):
        with self.assertRaises(ValueError):
            ps = ParameterSet({
                'East_River_Creature': {'formula': '2 * Deep_Thought + 16'},
                'Elders_of_Krikkit': {'formula': 'sqrt(East_River_Creature)'},
            }, {'Deep Thought': 2.4})

    def test_evaluate(self):
        ps = ParameterSet({
            'East_River_Creature': {'formula': '2 * Deep_Thought + 16'},
            'Elders_of_Krikkit': {'formula': 'sqrt(East_River_Creature)'},
        }, {'Deep_Thought': 42})
        self.assertEqual(
            ps.evaluate(),
            {'East_River_Creature': 100, 'Elders_of_Krikkit': 10}
        )
