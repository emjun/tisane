"""
Tests how model effects structures are inferred
NOTE: The tests are only to test, not to make any statements about how these variables relate in the real world
"""

import tisane as ts
from tisane import graph_inference
from tisane.graph_inference import (
    infer_main_effects,
    infer_interaction_effects,
    infer_random_effects,
)
from tisane.variable import (
    AbstractVariable,
    Associates,
    Has,
    Causes,
    Moderates,
    Nests,
    NumberValue,
    Exactly,  # Subclass of NumberValue
    AtMost,  # Subclass of NumberValue
    Repeats,
)
import unittest


class EffectsInferenceTest(unittest.TestCase):
    def test_main_included_causes(self):
        u0 = ts.Unit("Unit")
        m0 = u0.numeric("Measure 0")
        m1 = u0.numeric("Measure 1")
        dv = u0.numeric("Dependent variable")

        m0.causes(dv)
        m1.causes(dv)

        design = ts.Design(dv=dv, ivs=[m0, m1])

        gr = design.graph

        main_effects = infer_main_effects(gr, design)

        self.assertEqual(len(main_effects), 2)
        self.assertIn(m0, main_effects)
        self.assertIn(m1, main_effects)

    def test_main_included_associates(self):
        u0 = ts.Unit("Unit")
        m0 = u0.numeric("Measure 0")
        m1 = u0.numeric("Measure 1")
        dv = u0.numeric("Dependent variable")

        m0.associates_with(dv)
        m1.associates_with(dv)

        design = ts.Design(dv=dv, ivs=[m0, m1])

        gr = design.graph

        main_effects = infer_main_effects(gr, design)

        self.assertEqual(len(main_effects), 2)
        self.assertIn(m0, main_effects)
        self.assertIn(m1, main_effects)

    def test_main_excluded_causes(self):
        u0 = ts.Unit("Unit")
        m0 = u0.numeric("Measure 0")
        m1 = u0.numeric("Measure 1")
        m2 = u0.numeric("Measure 2")
        dv = u0.numeric("Dependent variable")

        m0.causes(dv)
        m1.causes(dv)

        design = ts.Design(dv=dv, ivs=[m0, m1])

        gr = design.graph

        main_effects = infer_main_effects(gr, design)

        self.assertEqual(len(main_effects), 2)
        self.assertIn(m0, main_effects)
        self.assertIn(m1, main_effects)
        self.assertNotIn(m2, main_effects)

    def test_main_excluded_associates(self):
        u0 = ts.Unit("Unit")
        m0 = u0.numeric("Measure 0")
        m1 = u0.numeric("Measure 1")
        m2 = u0.numeric("Measure 2")
        dv = u0.numeric("Dependent variable")

        m0.associates_with(dv)
        m1.associates_with(dv)

        design = ts.Design(dv=dv, ivs=[m0, m1])

        gr = design.graph

        main_effects = infer_main_effects(gr, design)

        self.assertEqual(len(main_effects), 2)
        self.assertIn(m0, main_effects)
        self.assertIn(m1, main_effects)
        self.assertNotIn(m2, main_effects)

    def test_main_conceptual_parent_causes(self):
        u0 = ts.Unit("Unit")
        m0 = u0.numeric("Measure 0")
        m1 = u0.numeric("Measure 1")
        m2 = u0.numeric("Measure 2")
        dv = u0.numeric("Dependent variable")

        m0.causes(dv)
        m1.causes(dv)
        m2.causes(m0)  # conceptual parent

        design = ts.Design(dv=dv, ivs=[m0, m1])

        gr = design.graph

        main_effects = infer_main_effects(gr, design)

        self.assertEqual(len(main_effects), 3)
        self.assertIn(m0, main_effects)
        self.assertIn(m1, main_effects)
        self.assertIn(m2, main_effects)

    def test_main_shared_ancestor_causes(self):
        u0 = ts.Unit("Unit")
        m0 = u0.numeric("Measure 0")
        m1 = u0.numeric("Measure 1")
        m2 = u0.numeric("Measure 2")
        dv = u0.numeric("Dependent variable")

        m0.causes(dv)
        m1.causes(dv)
        m2.causes(m0)  # shared ancestor
        m2.causes(m1)  # shared ancestor

        design = ts.Design(dv=dv, ivs=[m0, m1])

        gr = design.graph

        main_effects = infer_main_effects(gr, design)

        self.assertEqual(len(main_effects), 3)
        self.assertIn(m0, main_effects)
        self.assertIn(m1, main_effects)
        self.assertIn(m2, main_effects)

    def test_main_ivs_associated_and_causes_dv(self):
        u0 = ts.Unit("Unit")
        m0 = u0.numeric("Measure 0")
        m1 = u0.numeric("Measure 1")
        dv = u0.numeric("Dependent variable")

        m0.causes(dv)
        m1.causes(dv)
        m1.associates_with(m0)

        design = ts.Design(dv=dv, ivs=[m0])

        gr = design.graph

        main_effects = infer_main_effects(gr, design)

        self.assertEqual(len(main_effects), 2)
        self.assertIn(m0, main_effects)
        self.assertIn(m1, main_effects)

    def test_main_ivs_associated_and_associates_with_dv(self):
        u0 = ts.Unit("Unit")
        m0 = u0.numeric("Measure 0")
        m1 = u0.numeric("Measure 1")
        dv = u0.numeric("Dependent variable")

        m0.associates_with(dv)
        m1.associates_with(dv)
        m1.associates_with(m0)

        design = ts.Design(dv=dv, ivs=[m0])

        gr = design.graph

        main_effects = infer_main_effects(gr, design)

        self.assertEqual(len(main_effects), 2)
        self.assertIn(m0, main_effects)
        self.assertIn(m1, main_effects)

    def test_main_ivs_cause(self):
        u0 = ts.Unit("Unit")
        m0 = u0.numeric("Measure 0")
        m1 = u0.numeric("Measure 1")
        dv = u0.numeric("Dependent variable")

        m0.causes(dv)
        m1.causes(dv)
        m1.causes(m0)

        design = ts.Design(dv=dv, ivs=[m0])

        gr = design.graph

        main_effects = infer_main_effects(gr, design)

        self.assertEqual(len(main_effects), 2)
        self.assertIn(m0, main_effects)
        self.assertIn(m1, main_effects)

    def test_interaction_moderates_one_variable(self):
        u0 = ts.Unit("Unit")
        m0 = u0.numeric("Measure 0")
        m1 = u0.numeric("Measure 1")
        m2 = u0.numeric("Measure 2")
        dv = u0.numeric("Dependent variable")

        m0.causes(dv)
        m1.causes(dv)
        m2.moderates(moderator=m1, on=dv)

        design = ts.Design(dv=dv, ivs=[m0, m1]) # omit m2

        gr = design.graph

        main_effects = [m0, m1]
        interaction_effects = infer_interaction_effects(gr, design, main_effects)
        self.assertEqual(len(interaction_effects), 0)

        self.assertEqual(len(m2.relationships), 2)
        ixn = None
        for r in m2.relationships:
            if isinstance(r, Moderates):
                ixn = r
        self.assertIsNotNone(ixn)

    def test_interaction_moderates_two_variables(self):
        u0 = ts.Unit("Unit")
        m0 = u0.numeric("Measure 0")
        m1 = u0.numeric("Measure 1")
        m2 = u0.numeric("Measure 2")
        dv = u0.numeric("Dependent variable")

        m0.causes(dv)
        m1.causes(dv)
        m2.moderates(moderator=m1, on=dv)

        design = ts.Design(dv=dv, ivs=[m0, m1, m2])

        gr = design.graph

        main_effects = [m0, m1, m2]
        interaction_effects = infer_interaction_effects(gr, design, main_effects)
        self.assertEqual(len(interaction_effects), 1)
        var = interaction_effects.pop()

        self.assertEqual(len(m2.relationships), 2)
        ixn = None
        for r in m2.relationships:
            if isinstance(r, Moderates):
                ixn = r
        self.assertIsNotNone(ixn)
        for x in ixn.moderator: 
            self.assertIn(x.name, var.name)

    # def test_random_repeats(self):
    #     u0 = ts.Unit("Unit")
    #     s0 = ts.SetUp("Time")
    #     dv = u0.numeric("Dependent variable", number_of_instances=s0)

    #     design = ts.Design(dv=dv, ivs=[s0]) # main effect of Time

    #     gr = design.graph

    #     random_effects = infer_random_effects(gr, design)
    #     self.assertEqual(len(random_effects), 1)
    #     # TODO: assert that it's some kind of random slope?
    #     rs = random_effects[0]
    #     self.assertIsInstance(rs, RandomIntercept)
    #     self.assertIsInstance(rs.unit, u0)

    # def test_random_nested(self):
    #     u0 = ts.Unit("Unit 0")
    #     m0 = u0.numeric("Measure 0")
    #     u1 = ts.Unit("Unit 1")

    #     u0.nests_within(u1)

    #     design = ts.Design(dv=dv, ivs=[m0])

    #     gr = design.graph

    #     random_effects = infer_random_effects(gr, design)
    #     self.assertEqual(len(random_effects), 1)
    #     # TODO: assert that it's some kind of random intercept?
    #     ri = random_effects[0]
    #     self.assertIsInstance(ri, RandomIntercept)
    #     self.assertIsInstance(ri.unit, u1)
