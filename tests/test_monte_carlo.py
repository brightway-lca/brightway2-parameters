# -*- coding: utf-8 -*-
from copy import deepcopy

import numpy as np
import pytest

from bw2parameters import ParameterSet
from bw2parameters.errors import BroadcastingError


def test_monte_carlo_evaluation():
    params = {
        "Agrajag": {"amount": 3.14},
        "Constant_Mown": {
            "amount": 0.001,
            "uncertainty_type": 3,
            "loc": 0.001,
            "scale": 0.2,
            "minimum": 0,
        },
        "Deep_Thought": {
            "amount": 42,
            "uncertainty type": 5,
            "minimum": 30,
            "maximum": 70,
        },
        "Gargravarr": {
            "amount": 10,
            "uncertainty type": 5,
            "minimum": 0,
            "maximum": 25,
        },
        "East_River_Creature": {"formula": "2 * Agrajag ** 2 + Gargravarr"},
        "Eccentrica_Gallumbits": {"formula": "1 / sqrt(Constant_Mown)"},
        "Elders_of_Krikkit": {"formula": "East_River_Creature + Eccentrica_Gallumbits"},
        "Emily_Saunders": {"formula": "sin(Deep_Thought) + 7 - Elders_of_Krikkit"},
        "Gag_Halfrunt": {
            "formula": "Deep_Thought + Constant_Mown - log10(abs(Emily_Saunders))"
        },
    }
    result = ParameterSet(deepcopy(params)).evaluate_monte_carlo(1001)
    for v in result.values():
        assert v.shape == (1001,)
    for key in params:
        if key == "Agrajag":
            continue
        assert np.unique(result[key]).shape[0] > 100
    assert np.allclose(result["Agrajag"].sum(), 1001 * 3.14)
    result = ParameterSet(params).evaluate_monte_carlo()
    for v in result.values():
        assert v.shape == (1000,)


def test_monte_carlo_evaluation_global_params():
    params = {
        "Deep_Thought": {
            "amount": 5,
            "uncertainty type": 4,  # Uniform
            "minimum": 2,
            "maximum": 8,
        },
        "Gargravarr": {
            "amount": 10,
            "uncertainty type": 4,  # Uniform
            "minimum": 0,
            "maximum": 20,
        },
        "East_River_Creature": {"formula": "Agrajag + Gargravarr"},
        "Elders_of_Krikkit": {"formula": "East_River_Creature + Deep_Thought"},
    }
    global_params = {"Agrajag": np.arange(10) + 100}
    result = ParameterSet(params, global_params=global_params).evaluate_monte_carlo(10)
    assert all(result["East_River_Creature"] > 100)
    assert all(result["Elders_of_Krikkit"] > result["East_River_Creature"])


def test_wrong_shape():
    params = {
        "Agrajag": {"amount": 3.14},
        "East_River_Creature": {"formula": "2 * Agrajag * empty((100, 1000))"},
    }
    with pytest.raises(BroadcastingError):
        ParameterSet(params).evaluate_monte_carlo()
