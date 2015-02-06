from .. import ParameterSet
from ..errors import *
from ..utils import get_symbols
import unittest


class CallParameterSetTestCase(unittest.TestCase):
    def test_call_updates_exchanges(self):
        ds = {
            'name': 'Some dataset',
            'parameters': [
                {
                    'name': 'Deep_Thought',
                    'amount': 42
                },
                {
                    'name': 'East_River_Creature',
                    'formula': '2 * Deep_Thought + 16'
                },
                {
                    'name': 'Elders_of_Krikkit',
                    'formula': 'sqrt(East_River_Creature)'
                },
            ],
            'exchanges': [
                {
                   'parameter': 'Elders_of_Krikkit'
                },
                {
                    'amount': 44
                }
            ]
        }
        ds = ParameterSet(ds['parameters'])(ds)
        self.assertEqual(ds['exchanges'][0], {'amount': 10, 'parameter': 'Elders_of_Krikkit'})
        self.assertEqual(ds['exchanges'][1], {'amount': 44})

    def test_call_inserts_exchanges(self):
        ds = {
            'parameters': [
                {
                    'name': 'Deep_Thought',
                    'amount': 42
                },
                {
                    'name': 'East_River_Creature',
                    'formula': '2 * Deep_Thought + 16'
                },
                {
                    'name': 'Elders_of_Krikkit',
                    'formula': 'sqrt(East_River_Creature)'
                },
            ]
        }
        new_ds = {}
        ds = ParameterSet(ds['parameters'])(new_ds)
        self.assertTrue('parameters' in new_ds)

    def test_call_no_exchanges(self):
        ds = {
            'parameters': [
                {
                    'name': 'Deep_Thought',
                    'amount': 42
                },
                {
                    'name': 'East_River_Creature',
                    'formula': '2 * Deep_Thought + 16'
                },
                {
                    'name': 'Elders_of_Krikkit',
                    'formula': 'sqrt(East_River_Creature)'
                },
            ]
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


class EvaluationTetstCase(unittest.TestCase):
    def test_simple_evaluation(self):
        params = [
            {
                'name': 'Agrajag',
                'amount': 3.14
            },
            {
                'name': 'Constant_Mown',
                'amount': 0.001
            },
            {
                'name': 'Deep_Thought',
                'amount': 42
            },
            {
                'name': 'East_River_Creature',
                'formula': '2 * Agrajag ** 2'
            },
            {
                'name': 'Eccentrica_Gallumbits',
                'formula': '1 / sqrt(Constant_Mown)'
            },
            {
                'name': 'Elders_of_Krikkit',
                'formula': 'East_River_Creature + Eccentrica_Gallumbits'
            },
            {
                'name': 'Emily_Saunders',
                'formula': 'sin(Deep_Thought) + 7 - Elders_of_Krikkit'
            },
            {
                'name': 'Gag_Halfrunt',
                'formula': 'Deep_Thought + Constant_Mown - log10(abs(Emily_Saunders))'
            },
            {
                'name': 'Gargravarr',
                'formula': 'Agrajag + Constant_Mown + Deep_Thought + East_River_Creature + Eccentrica_Gallumbits + Elders_of_Krikkit + Emily_Saunders + Gag_Halfrunt'
            },
        ]
        ParameterSet(params).evaluate()

    def test_evaluation_values(self):
        params = [
            {
                'name': 'Deep_Thought',
                'amount': 42
            },
            {
                'name': 'East_River_Creature',
                'formula': '2 * Deep_Thought + 16'
            },
            {
                'name': 'Elders_of_Krikkit',
                'formula': 'sqrt(East_River_Creature)'
            },
        ]
        ps = ParameterSet(params)
        self.assertEqual(
            {'Deep_Thought': 42, 'Elders_of_Krikkit': 10, 'East_River_Creature': 100},
            ps.evaluate()
        )

    def test_evaluate_update_values(self):
        params = [
            {
                'name': 'Deep_Thought',
                'amount': 42
            },
            {
                'name': 'East_River_Creature',
                'formula': '2 * Deep_Thought + 16'
            },
            {
                'name': 'Elders_of_Krikkit',
                'formula': 'sqrt(East_River_Creature)'
            },
        ]
        ParameterSet(params).evaluate_and_update_params()
        self.assertEqual(params[1]['amount'], 100)
        self.assertEqual(params[2]['amount'], 10)


class ValidationTestCase(unittest.TestCase):
    def test_not_dict(self):
        with self.assertRaises(ValueError):
            ps = ParameterSet([[]])

    def test_missing_fields(self):
        with self.assertRaises(ValueError):
            ps = ParameterSet([{}])
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

    def test_missing_name(self):
        ps = ParameterSet([
            {'formula': '2 * pi', 'name': 'Deep_Thought'},
        ])
        with self.assertRaises(MissingName):
            ps = ParameterSet([
                {'formula': '2 * pi'},
            ])

    def test_space_in_name(self):
        ps = ParameterSet([
            {'amount': 42, 'name': 'Deep_Thought'},
        ])
        with self.assertRaises(ValueError):
            ps = ParameterSet([
                {'amount': 42, 'name': 'Deep Thought'},
            ])

    def test_name_in_existing_symbols(self):
        with self.assertRaises(DuplicateName):
            ps = ParameterSet([
                {'amount': 42, 'name': 'log'},
            ])

    def test_name_already_seen(self):
        with self.assertRaises(DuplicateName):
            ps = ParameterSet([
                {'amount': 42, 'name': 'Deep_Thought'},
                {'amount': 4.2, 'name': 'Deep_Thought'},
            ])

    def test_self_reference(self):
        ps = ParameterSet([
            {'formula': '2 * Elders_of_Krikkit', 'name': 'Elders_of_Krikkit'},
        ])
        with self.assertRaises(SelfReference):
            ps.validate()

    def test_missing_reference(self):
        ps = ParameterSet([
            {'formula': '2 * Ford_Prefect', 'name': 'Elders_of_Krikkit'},
        ])
        with self.assertRaises(MissingParameter):
            ps.validate()

    def test_circular_reference(self):
        ps = ParameterSet([
            {'formula': '2 * Agrajag', 'name': 'Elders_of_Krikkit'},
            {'formula': '2 * Elders_of_Krikkit', 'name': 'East_River_Creature'},
            {'formula': '2 * East_River_Creature', 'name': 'Agrajag'},
        ])
        with self.assertRaises(CircularReference):
            ps.validate()
