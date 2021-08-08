"""
Tests helper functions used to infer model effects structures
NOTE: The tests are only to test, not to make any statements about how these variables relate in the real world
"""

import tisane as ts
from tisane import graph_inference
from tisane.graph_inference import (
    cast_to_variables,
    filter_interactions_involving_variables,
    find_common_ancestors,
    find_variable_causal_ancestors,
    find_all_causal_ancestors,
    find_variable_associates_that_causes_or_associates_another,
    find_all_associates_that_causes_or_associates_another,
    find_variable_parent_that_causes_or_associates_another,
    find_all_parents_that_causes_or_associates_another,
    find_moderates_edges_on_variable
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


class EffectsInferenceHelpersTest(unittest.TestCase):
    def test_cast_to_variables_one(self):
        u0 = ts.Unit("Unit")
        m0 = u0.numeric("Measure 0")

        names = set()
        names.add("Measure 0")

        vars = cast_to_variables(names, [m0])
        self.assertEqual(len(vars), 1)
        self.assertIn(m0, vars)

    def test_cast_to_variables_not_found(self):
        u0 = ts.Unit("Unit")
        m0 = u0.numeric("Measure 0")
        m1 = u0.numeric("Measure 1")

        names = set()
        names.add("Measure 1")

        vars = cast_to_variables(names, [m0])
        self.assertEqual(len(vars), 0)

    def test_cast_to_variables_multiple(self):
        u0 = ts.Unit("Unit")
        m0 = u0.numeric("Measure 0")
        m1 = u0.numeric("Measure 1")
        m2 = u0.numeric("Measure 2")

        names = set()
        names.add("Measure 0")
        names.add("Measure 1")

        vars = cast_to_variables(names, [m0, m1, m2])
        self.assertEqual(len(vars), 2)
        self.assertIn(m0, vars)
        self.assertIn(m1, vars)

    def test_find_common_causal_ancestors(self):
        u0 = ts.Unit("Unit")
        m0 = u0.numeric("Measure 0")
        m1 = u0.numeric("Measure 1")
        m2 = u0.numeric("Measure 2")
        dv = u0.numeric("Dependent variable")

        # m0 is the common (causal) ancestor
        m0.causes(m1)
        m0.causes(m2)

        m1.causes(dv)
        m2.causes(dv)

        design = ts.Design(dv=dv, ivs=[m0, m1, m2])
        gr = design.graph

        common_ancestors = cast_to_variables(
            find_common_ancestors([m1, m2], gr), design.ivs
        )

        self.assertEqual(len(common_ancestors), 1)
        self.assertIn(m0, common_ancestors)

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

        common_ancestors = cast_to_variables(
            find_common_ancestors([m1, m2], gr), design.ivs
        )

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

        common_ancestors = cast_to_variables(
            find_common_ancestors([m1, m2], gr), design.ivs
        )

        self.assertEqual(len(common_ancestors), 0)

    def test_find_variable_causal_ancestors(self):
        u0 = ts.Unit("Unit")
        m0 = u0.numeric("Measure 0")
        m1 = u0.numeric("Measure 1")
        m2 = u0.numeric("Measure 2")
        dv = u0.numeric("Dependent variable")

        m0.causes(m1)
        m1.causes(m2)
        m2.causes(dv)

        design = ts.Design(dv=dv, ivs=[m0, m1, m2])
        gr = design.graph

        causal_ancestors = cast_to_variables(
            find_variable_causal_ancestors(m0, gr), design.ivs
        )
        self.assertEqual(len(causal_ancestors), 0)

        causal_ancestors = cast_to_variables(
            find_variable_causal_ancestors(m1, gr), design.ivs
        )
        self.assertEqual(len(causal_ancestors), 1)
        self.assertIn(m0, causal_ancestors)

        causal_ancestors = cast_to_variables(
            find_variable_causal_ancestors(m2, gr), design.ivs
        )
        self.assertEqual(len(causal_ancestors), 2)
        self.assertIn(m0, causal_ancestors)
        self.assertIn(m1, causal_ancestors)

    def test_find_all_causal_ancestors(self):
        u0 = ts.Unit("Unit")
        m0 = u0.numeric("Measure 0")
        m1 = u0.numeric("Measure 1")
        m2 = u0.numeric("Measure 2")
        dv = u0.numeric("Dependent variable")

        m0.causes(m1)
        m1.causes(m2)
        m2.causes(dv)

        design = ts.Design(dv=dv, ivs=[m0, m1, m2])
        gr = design.graph

        causal_ancestors = cast_to_variables(
            find_all_causal_ancestors([m2], gr), design.ivs
        )

        self.assertEqual(len(causal_ancestors), 2)
        self.assertIn(m0, causal_ancestors)
        self.assertIn(m1, causal_ancestors)

    def test_find_all_causal_ancestors_partial_graph(self):
        u0 = ts.Unit("Unit")
        m0 = u0.numeric("Measure 0")
        m1 = u0.numeric("Measure 1")
        m2 = u0.numeric("Measure 2")
        dv = u0.numeric("Dependent variable")

        m0.causes(m1)
        m1.causes(m2)
        m2.causes(dv)

        design = ts.Design(dv=dv, ivs=[m2])
        gr = design.graph

        causal_ancestors = cast_to_variables(
            find_all_causal_ancestors([m2], gr), [m0, m1, m2]
        )

        self.assertEqual(len(causal_ancestors), 1)

    def test_find_variable_associates_that_causes_dv(self):
        u0 = ts.Unit("Unit")
        m0 = u0.numeric("Measure 0")
        m1 = u0.numeric("Measure 1")
        dv = u0.numeric("Dependent variable")

        m0.causes(dv)
        m1.causes(dv)
        m1.associates_with(m0)

        design = ts.Design(dv=dv, ivs=[m0])
        gr = design.graph

        tmp = find_variable_associates_that_causes_or_associates_another(
            source=m0, sink=dv, gr=gr
        )
        self.assertEqual(len(tmp), 1)
        name = tmp.pop()
        self.assertIsInstance(name, str)
        tmp.add(name)

        associates_that_cause_dv = cast_to_variables(tmp, [m0, m1])
        self.assertEqual(len(associates_that_cause_dv), 1)
        self.assertIn(m1, associates_that_cause_dv)
        var = associates_that_cause_dv.pop()
        self.assertIsInstance(var, AbstractVariable)

    def test_find_variable_associates_that_associates_with_dv(self):
        u0 = ts.Unit("Unit")
        m0 = u0.numeric("Measure 0")
        m1 = u0.numeric("Measure 1")
        dv = u0.numeric("Dependent variable")

        m0.causes(dv)
        m1.associates_with(dv)
        m1.associates_with(m0)

        design = ts.Design(dv=dv, ivs=[m0])
        gr = design.graph

        associates_that_cause_dv = cast_to_variables(
            find_variable_associates_that_causes_or_associates_another(
                source=m0, sink=dv, gr=gr
            ),
            [m0, m1],
        )
        self.assertEqual(len(associates_that_cause_dv), 1)
        self.assertIn(m1, associates_that_cause_dv)

    def test_find_variable_causes_that_causes_dv_wrong_rule_function(self):
        u0 = ts.Unit("Unit")
        m0 = u0.numeric("Measure 0")
        m1 = u0.numeric("Measure 1")
        m2 = u0.numeric("Measure 2")
        dv = u0.numeric("Dependent variable")

        m0.causes(dv)
        m1.associates_with(dv)
        m1.causes(m0)

        design = ts.Design(dv=dv, ivs=[m0])
        gr = design.graph

        associates_that_cause_dv = cast_to_variables(
            find_variable_associates_that_causes_or_associates_another(
                source=m0, sink=dv, gr=gr
            ),
            [m0, m1],
        )
        self.assertEqual(len(associates_that_cause_dv), 0)

    def test_find_all_associates_that_causes_or_associates_with_dv(self):
        u0 = ts.Unit("Unit")
        m0 = u0.numeric("Measure 0")
        m1 = u0.numeric("Measure 1")
        m2 = u0.numeric("Measure 2")
        dv = u0.numeric("Dependent variable")

        m0.causes(dv)
        m1.associates_with(dv)
        m1.associates_with(m0)
        m2.causes(dv)
        m2.associates_with(m1)

        design = ts.Design(dv=dv, ivs=[m0, m1])
        gr = design.graph

        associates_that_cause_dv = cast_to_variables(
            find_all_associates_that_causes_or_associates_another(
                sources=[m0, m1], sink=dv, gr=gr
            ),
            [m0, m1, m2],
        )
        self.assertEqual(len(associates_that_cause_dv), 3)
        self.assertIn(m0, associates_that_cause_dv)
        self.assertIn(m1, associates_that_cause_dv)
        self.assertIn(m2, associates_that_cause_dv)

    def test_find_all_associates_that_causes_or_associates_with_dv_is_not_recursive(
        self,
    ):
        u0 = ts.Unit("Unit")
        m0 = u0.numeric("Measure 0")
        m1 = u0.numeric("Measure 1")
        m2 = u0.numeric("Measure 2")
        dv = u0.numeric("Dependent variable")

        m0.causes(dv)
        m1.associates_with(dv)
        m1.associates_with(m0)
        m2.causes(dv)
        m1.associates_with(m2)

        design = ts.Design(dv=dv, ivs=[m0])
        gr = design.graph

        associates_that_cause_dv = cast_to_variables(
            find_all_associates_that_causes_or_associates_another(
                sources=[m0, m1], sink=dv, gr=gr
            ),
            [m0, m1, m2],
        )
        self.assertEqual(len(associates_that_cause_dv), 2)
        self.assertIn(m0, associates_that_cause_dv)
        self.assertIn(m1, associates_that_cause_dv)
        self.assertNotIn(m2, associates_that_cause_dv)

    def test_find_variable_parent_that_associates_with_dv(self):
        u0 = ts.Unit("Unit")
        m0 = u0.numeric("Measure 0")
        m1 = u0.numeric("Measure 1")
        m2 = u0.numeric("Measure 2")
        dv = u0.numeric("Dependent variable")

        m0.causes(dv)
        m1.causes(m0)
        m1.associates_with(dv)

        design = ts.Design(dv=dv, ivs=[m0])
        gr = design.graph

        tmp = find_variable_parent_that_causes_or_associates_another(
            source=m0, sink=dv, gr=gr
        )
        self.assertEqual(len(tmp), 1)

        parent_associates_with_dv = cast_to_variables(
            find_variable_parent_that_causes_or_associates_another(
                source=m0, sink=dv, gr=gr
            ),
            [m0, m1],
        )
        self.assertEqual(len(parent_associates_with_dv), 1)
        self.assertIn(m1, parent_associates_with_dv)

    def test_find_variable_parent_that_causes_dv(self):
        u0 = ts.Unit("Unit")
        m0 = u0.numeric("Measure 0")
        m1 = u0.numeric("Measure 1")
        m2 = u0.numeric("Measure 2")
        dv = u0.numeric("Dependent variable")

        m0.causes(dv)
        m1.causes(m0)
        m1.causes(dv)

        design = ts.Design(dv=dv, ivs=[m0])
        gr = design.graph

        tmp = find_variable_parent_that_causes_or_associates_another(
            source=m0, sink=dv, gr=gr
        )
        self.assertEqual(len(tmp), 1)

        parent_associates_with_dv = cast_to_variables(
            find_variable_parent_that_causes_or_associates_another(
                source=m0, sink=dv, gr=gr
            ),
            [m0, m1],
        )
        self.assertEqual(len(parent_associates_with_dv), 1)
        self.assertIn(m1, parent_associates_with_dv)

    def test_find_all_parents_that_associates_or_causes_dv(self):
        u0 = ts.Unit("Unit")
        m0 = u0.numeric("Measure 0")
        m1 = u0.numeric("Measure 1")
        m2 = u0.numeric("Measure 2")
        dv = u0.numeric("Dependent variable")

        m0.causes(dv)
        m1.causes(m0)
        m2.causes(m0)
        m1.causes(dv)
        m2.associates_with(dv)

        design = ts.Design(dv=dv, ivs=[m0])
        gr = design.graph

        tmp = find_variable_parent_that_causes_or_associates_another(
            source=m0, sink=dv, gr=gr
        )
        self.assertEqual(len(tmp), 2)

        parent_associates_with_dv = cast_to_variables(
            find_all_parents_that_causes_or_associates_another(
                sources=[m0], sink=dv, gr=gr
            ),
            [m0, m1, m2],
        )
        self.assertEqual(len(parent_associates_with_dv), 2)
        self.assertIn(m1, parent_associates_with_dv)
        self.assertIn(m2, parent_associates_with_dv)

    def test_find_moderates_on_dv(self): 
        u0 = ts.Unit("Unit")
        m0 = u0.numeric("Measure 0")
        m1 = u0.numeric("Measure 1")
        m2 = u0.numeric("Measure 2")
        dv = u0.numeric("Dependent variable")

        m0.causes(dv)
        m1.moderates(moderator=[m0], on=dv) 
        
        design = ts.Design(dv=dv, ivs=[m0])
        gr = design.graph

        moderates = find_moderates_edges_on_variable(gr=gr, on=design.dv)
        self.assertEqual(len(moderates), 1)
        ixn = moderates.pop()
        self.assertIsInstance(ixn, str)
        self.assertTrue("Measure 0" in ixn)
        self.assertTrue("Measure 1" in ixn)
        self.assertTrue("*" in ixn)

    def test_find_moderates_on_dv_interaction_order_agnostic(self): 
        u0 = ts.Unit("Unit")
        m0 = u0.numeric("Measure 0")
        m1 = u0.numeric("Measure 1")
        m2 = u0.numeric("Measure 2")
        dv = u0.numeric("Dependent variable")

        m0.causes(dv)
        m0.moderates(moderator=[m1], on=dv) # Checks that ts.Design with ivs = m1 also returns same (flips above)
        
        design = ts.Design(dv=dv, ivs=[m0])
        gr = design.graph

        moderates = find_moderates_edges_on_variable(gr=gr, on=design.dv)
        self.assertEqual(len(moderates), 1)
        ixn = moderates.pop()
        self.assertIsInstance(ixn, str)
        self.assertTrue("Measure 0" in ixn)
        self.assertTrue("Measure 1" in ixn)
        self.assertTrue("*" in ixn)

    def test_filter_interactions_involving_variables_both_variables_found(self): 
        u0 = ts.Unit("Unit")
        m0 = u0.numeric("Measure 0")
        m1 = u0.numeric("Measure 1")
        m2 = u0.numeric("Measure 2")
        dv = u0.numeric("Dependent variable")

        m0.causes(dv)
        m0.moderates(moderator=[m1], on=dv) # Checks that ts.Design with ivs = m1 also returns same (flips above)
        
        design = ts.Design(dv=dv, ivs=[m0])
        gr = design.graph

        moderates = find_moderates_edges_on_variable(gr=gr, on=design.dv)
        self.assertEqual(len(moderates), 1)
        interactions = filter_interactions_involving_variables(variables=[m0, m1, m2], interaction_names=moderates)
        self.assertEqual(len(interactions), 1)

    def test_filter_interactions_involving_variables_only_one_variable_found(self): 
        u0 = ts.Unit("Unit")
        m0 = u0.numeric("Measure 0")
        m1 = u0.numeric("Measure 1")
        m2 = u0.numeric("Measure 2")
        dv = u0.numeric("Dependent variable")

        m0.causes(dv)
        m0.moderates(moderator=[m1], on=dv) # Checks that ts.Design with ivs = m1 also returns same (flips above)
        
        design = ts.Design(dv=dv, ivs=[m0])
        gr = design.graph

        moderates = find_moderates_edges_on_variable(gr=gr, on=design.dv)
        self.assertEqual(len(moderates), 1)
        interactions = filter_interactions_involving_variables(variables=[m0, m2], interaction_names=moderates)
        self.assertEqual(len(interactions), 0)
    
    def test_filter_interactions_involving_variables_none_found(self): 
        u0 = ts.Unit("Unit")
        m0 = u0.numeric("Measure 0")
        m1 = u0.numeric("Measure 1")
        m2 = u0.numeric("Measure 2")
        dv = u0.numeric("Dependent variable")

        m0.causes(dv)
        m0.moderates(moderator=[m1], on=dv) # Checks that ts.Design with ivs = m1 also returns same (flips above)
        
        design = ts.Design(dv=dv, ivs=[m0])
        gr = design.graph

        moderates = find_moderates_edges_on_variable(gr=gr, on=design.dv)
        self.assertEqual(len(moderates), 1)
        interactions = filter_interactions_involving_variables(variables=[m2], interaction_names=moderates)
        self.assertEqual(len(interactions), 0)
        
