"""
Tests helper functions used to infer model effects structures
NOTE: The tests are only to test, not to make any statements about how these variables relate in the real world
"""

import tisane as ts
from tisane import graph_inference
from tisane.graph_inference import (
    cast_to_variables,
    find_common_ancestors,
    infer_main_effects,
    infer_interaction_effects,
    infer_random_effects
)
from tisane.variable import (
    AbstractVariable,
    Associates,
    Has,
    Causes,
    Moderates,
    Nests,
    NumberValue, 
    Exactly, # Subclass of NumberValue 
    AtMost, # Subclass of NumberValue 
    Repeats,
)
import unittest


class EffectsInferenceHelpersTest(unittest.TestCase):
    # def test_find_common_causal_ancestors(self):
    #     u0 = ts.Unit("Unit")
    #     m0 = u0.numeric("Measure 0")
    #     m1 = u0.numeric("Measure 1")
    #     m2 = u0.numeric("Measure 2")
    #     dv = u0.numeric("Dependent variable")

    #     # m0 is the common (causal) ancestor
    #     m0.causes(m1)
    #     m0.causes(m2)

    #     m1.causes(dv)
    #     m2.causes(dv)

    #     design = ts.Design(dv=dv, ivs=[m0, m1, m2])
    #     gr = design.graph

    #     common_ancestors = cast_to_variables(find_common_ancestors([m1, m2], gr), design.ivs)

    #     self.assertEqual(len(common_ancestors), 1)
    #     self.assertIn(m0, common_ancestors)
    
    def test_find_common_causal_ancestors_none(self):
        u0 = ts.Unit("Unit")
        m0 = u0.numeric("Measure 0")
        m1 = u0.numeric("Measure 1")
        m2 = u0.numeric("Measure 2")
        dv = u0.numeric("Dependent variable")

        # m0 is the common (causal) ancestor
        m0.causes(m1)
        m1.causes(dv)
        m2.causes(dv)

        design = ts.Design(dv=dv, ivs=[m0, m1, m2])
        gr = design.graph

        common_ancestors = cast_to_variables(find_common_ancestors([m1, m2], gr), design.ivs)

        self.assertEqual(len(common_ancestors), 0)

    def test_find_common_causal_ancestors_none_causal_chain(self):
        u0 = ts.Unit("Unit")
        m0 = u0.numeric("Measure 0")
        m1 = u0.numeric("Measure 1")
        m2 = u0.numeric("Measure 2")
        dv = u0.numeric("Dependent variable")

        # m0 is the common (causal) ancestor
        m0.causes(m1)
        m1.causes(m2)
        m1.causes(dv)
        m2.causes(dv)

        design = ts.Design(dv=dv, ivs=[m0, m1, m2])
        gr = design.graph

        common_ancestors = cast_to_variables(find_common_ancestors([m1, m2], gr), design.ivs)

        self.assertEqual(len(common_ancestors), 0)

    def test_find_variable_causal_ancestors(self):
        pass