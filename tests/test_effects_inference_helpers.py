"""
Tests helper functions used to infer model effects structures
NOTE: The tests are only to test, not to make any statements about how these variables relate in the real world
"""

from tisane.random_effects import RandomIntercept, RandomSlope
import tisane as ts
from tisane import graph_inference
from tisane.graph_inference import (
    cast_to_variables,
    construct_random_effects_for_composed_measures,
    construct_random_effects_for_nests,
    construct_random_effects_for_interactions,
    create_variable_from_set_of_variables,
    filter_interactions_involving_variables,
    filter_random_candidates,
    find_common_ancestors,
    find_largest_subset_of_variables_that_vary_within_unit,
    find_variable_causal_ancestors,
    find_all_causal_ancestors,
    find_variable_associates_that_causes_or_associates_another,
    find_all_associates_that_causes_or_associates_another,
    find_variable_parent_that_causes_or_associates_another,
    find_all_parents_that_causes_or_associates_another,
    find_moderates_edges_on_variable,
    find_ordered_list_of_units,
    construct_random_effects_for_repeated_measures,
    get_variables_in_interaction_effect,
    infer_interaction_effects
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
    Nominal,
    SetUp,
    Unit
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
        selected_main_effects = [m0, m1]
        interactions = filter_interactions_involving_variables(variables=selected_main_effects, interaction_names=moderates)
        self.assertEqual(len(interactions), 1)
    
    def test_filter_interactions_involving_variables_two_variables_found(self): 
        u0 = ts.Unit("Unit")
        m0 = u0.numeric("Measure 0")
        m1 = u0.numeric("Measure 1")
        m2 = u0.numeric("Measure 2")
        dv = u0.numeric("Dependent variable")

        m0.causes(dv)
        m0.moderates(moderator=[m1, m2], on=dv) # Checks that ts.Design with ivs = m1 also returns same (flips above)
        
        design = ts.Design(dv=dv, ivs=[m0])
        gr = design.graph

        moderates = find_moderates_edges_on_variable(gr=gr, on=design.dv)
        self.assertEqual(len(moderates), 1)
        selected_main_effects = [m0, m1, m2]
        interactions = filter_interactions_involving_variables(variables=selected_main_effects, interaction_names=moderates)
        self.assertEqual(len(interactions), 1)
        ixn = interactions.pop() 
        self.assertTrue("Measure 0" in ixn)
        self.assertTrue("Measure 1" in ixn)
        self.assertTrue("Measure 2" in ixn)

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
        selected_main_effects = [m0, m2]
        interactions = filter_interactions_involving_variables(variables=selected_main_effects, interaction_names=moderates)
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
        selected_main_effects = [m2]
        interactions = filter_interactions_involving_variables(variables=selected_main_effects, interaction_names=moderates)
        self.assertEqual(len(interactions), 0)
        
    def test_filter_interactions_involving_variables_multiple_interactions_all_included(self): 
        u0 = ts.Unit("Unit")
        m0 = u0.numeric("Measure 0")
        m1 = u0.numeric("Measure 1")
        m2 = u0.numeric("Measure 2")
        m3 = u0.numeric("Measure 3")
        dv = u0.numeric("Dependent variable")

        m0.causes(dv)
        m0.moderates(moderator=[m1, m2], on=dv) # Checks that ts.Design with ivs = m1 also returns same (flips above)
        m3.moderates(moderator=[m0], on=dv)
        
        design = ts.Design(dv=dv, ivs=[m0])
        gr = design.graph

        moderates = find_moderates_edges_on_variable(gr=gr, on=design.dv)
        self.assertEqual(len(moderates), 2)
        selected_main_effects = [m0, m1, m2, m3]
        interactions = filter_interactions_involving_variables(variables=selected_main_effects, interaction_names=moderates)
        self.assertEqual(len(interactions), 2)
        self.assertIn("Measure 0*Measure 1*Measure 2", interactions)
        self.assertIn("Measure 3*Measure 0", interactions)
 
    def test_filter_interactions_involving_variables_multiple_interactions_excluded(self): 
        u0 = ts.Unit("Unit")
        m0 = u0.numeric("Measure 0")
        m1 = u0.numeric("Measure 1")
        m2 = u0.numeric("Measure 2")
        m3 = u0.numeric("Measure 3")
        dv = u0.numeric("Dependent variable")

        m0.causes(dv)
        m0.moderates(moderator=[m1, m2], on=dv) # Checks that ts.Design with ivs = m1 also returns same (flips above)
        m3.moderates(moderator=[m0], on=dv)
        
        design = ts.Design(dv=dv, ivs=[m0])
        gr = design.graph

        moderates = find_moderates_edges_on_variable(gr=gr, on=design.dv)
        self.assertEqual(len(moderates), 2)
        selected_main_effects = [m0, m1, m2]
        interactions = filter_interactions_involving_variables(variables=selected_main_effects, interaction_names=moderates)
        self.assertEqual(len(interactions), 1)

    def test_construct_random_effects_for_repeated_measures_no_nesting(self): 
        u0 = ts.Unit("Unit")
        s0 = ts.SetUp("Time", order=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]) # e.g., 10 weeks
        m0 = u0.numeric("Measure 0")
        dv = u0.numeric("Dependent variable", number_of_instances=s0) # repeated measure

        m0.causes(dv)
        
        design = ts.Design(dv=dv, ivs=[m0])
        gr = design.graph

        random_effects = construct_random_effects_for_repeated_measures(gr=gr, query=design)
        self.assertEqual(len(random_effects), 2)
        
        has_unit_ri = False 
        has_time_ri = False
        for ri in random_effects: 
            self.assertIsInstance(ri, RandomIntercept)
            if isinstance(ri.groups, Unit):
                self.assertIs(ri.groups, u0)
                has_unit_ri = True
            elif isinstance(ri.groups, SetUp): 
                self.assertIs(ri.groups, s0)
                has_time_ri = True
        self.assertTrue(has_unit_ri)
        self.assertTrue(has_time_ri)

    def test_construct_random_effects_does_not_construct(self): 
        u0 = ts.Unit("Unit")
        m0 = u0.numeric("Measure 0")
        m1 = u0.numeric("Measure 1")
        dv = u0.numeric("Dependent variable")

        m0.causes(dv)
        m1.causes(dv)
        
        design = ts.Design(dv=dv, ivs=[m0, m1])
        gr = design.graph

        random_from_repeats = construct_random_effects_for_repeated_measures(gr=gr, query=design)
        self.assertEqual(len(random_from_repeats), 0)

        # random_from_nests = construct_random_effects_for_nests(gr=gr, query=design)
    
    def test_find_ordered_list_units_one_unit(self): 
        u0 = ts.Unit("Unit 0")
        dv = u0.numeric("Dependent variable")

        u0.causes(dv)

        design = ts.Design(dv=dv, ivs=[u0])
        gr = design.graph

        ordered_units = find_ordered_list_of_units(gr=gr)
        self.assertEqual(len(ordered_units), len(design.ivs))
        self.assertIn(u0.name, ordered_units)

    def test_find_ordered_list_units_multiple_units(self): 
        u0 = ts.Unit("Unit 0")
        u1 = ts.Unit("Unit 1")
        u2 = ts.Unit("Unit 2")
        dv = u0.numeric("Dependent variable")

        u0.nests_within(u1)
        u1.nests_within(u2)

        design = ts.Design(dv=dv, ivs=[u0, u1, u2])
        gr = design.graph

        ordered_units = find_ordered_list_of_units(gr=gr)
        self.assertEqual(len(ordered_units), len(design.ivs))
        
    def test_construct_random_effects_for_nests_none_one_unit(self): 
        u0 = ts.Unit("Unit 0")
        m0 = u0.numeric("Measure 0")
        m1 = u0.numeric("Measure 1")
        dv = u0.numeric("Dependent variable")

        m0.causes(dv)
        m1.causes(dv)

        design = ts.Design(dv=dv, ivs=[m0, m1])
        gr = design.graph

        random_from_nests = construct_random_effects_for_nests(gr=gr, dv=design.dv, variables=design.ivs)
        self.assertEqual(len(random_from_nests), 0)

    def test_construct_random_effects_for_nests_for_two_units_excludes_lower_unit(self): 
        
        u0 = ts.Unit("Unit 0")
        u1 = ts.Unit("Unit 1")
        m0 = u1.numeric("Measure 0")
        m1 = u1.numeric("Measure 1")
        m2 = u1.numeric("Measure 2")
        dv = u1.numeric("Dependent variable") # because u1 has dv, this analysis effectively becomes a single unit analysis

        m0.causes(dv)
        m1.causes(dv)
        m2.causes(dv)
        u0.nests_within(u1)
        
        design = ts.Design(dv=dv, ivs=[m0, m1, m2])
        gr = design.graph

        random_effects = construct_random_effects_for_nests(gr=gr, dv=design.dv, variables=design.ivs)
        self.assertEqual(len(random_effects), 0) # There are no random effects because this analysis is focused on u0 main effects

    def test_construct_random_effects_for_nests_two_units_no_measures_for_higher_unit(self): 
        u0 = ts.Unit("Unit 0")
        u1 = ts.Unit("Unit 1")
        m0 = u0.numeric("Measure 0")
        m1 = u0.numeric("Measure 1")
        dv = u0.numeric("Dependent variable")

        m0.causes(dv)
        m1.causes(dv)
        u0.nests_within(u1)

        design = ts.Design(dv=dv, ivs=[m0, m1])
        gr = design.graph

        random_from_nests = construct_random_effects_for_nests(gr=gr, dv=design.dv, variables=design.ivs)
        self.assertEqual(len(random_from_nests), 1)
        ri = random_from_nests.pop()
        self.assertIsInstance(ri, RandomIntercept)
        self.assertIs(ri.groups, u1)

    def test_construct_random_effects_for_nests_two_units_measures_for_both(self): 
        u0 = ts.Unit("Unit 0")
        u1 = ts.Unit("Unit 1")
        m0 = u0.numeric("Measure 0")
        m1 = u0.numeric("Measure 1")
        m2 = u1.numeric("Measure 2")
        dv = u0.numeric("Dependent variable")

        m0.causes(dv)
        m1.causes(dv)
        u0.nests_within(u1)

        design = ts.Design(dv=dv, ivs=[m0, m1, m2])
        gr = design.graph

        random_from_nests = construct_random_effects_for_nests(gr=gr, dv=design.dv, variables=design.ivs)
        self.assertEqual(len(random_from_nests), 1)
        ri = random_from_nests.pop()
        self.assertIsInstance(ri, RandomIntercept)
        self.assertIs(ri.groups, u1)
        
    def test_construct_random_effects_for_nests_for_three_units_measures_for_lower_two(self): 
        # e.g., students within schools within districts
        u0 = ts.Unit("Unit 0")
        u1 = ts.Unit("Unit 1")
        u2 = ts.Unit("Unit 2")
        m0 = u0.numeric("Measure 0")
        m1 = u0.numeric("Measure 1")
        m2 = u1.numeric("Measure 2")
        dv = u0.numeric("Dependent variable")

        m0.causes(dv)
        m1.causes(dv)
        u0.nests_within(u1)
        u1.nests_within(u2)

        design = ts.Design(dv=dv, ivs=[m0, m1, m2])
        gr = design.graph

        random_from_nests = construct_random_effects_for_nests(gr=gr, dv=design.dv, variables=design.ivs)
        self.assertEqual(len(random_from_nests), 2)

    # def test_construct_random_effects_for_nests_analysis_excludes_upper_level(self): 
    #     pass
        
    #     design = ts.Design(dv=dv, ivs=[m0])
    #     gr = design.graph

    # Barr et al. 2013 example
    def test_construct_random_effects_for_composed_measures_between_items_within_participants_repeats(self):
        subject = ts.Unit("Subject")
        word = ts.Unit("Word")

        condition = subject.nominal("Word type", cardinality=2, number_of_instances=2)
        reaction_time = subject.numeric("Time", number_of_instances=word) # repeats
        condition.has(word, number_of_instances=2)
        
        design = ts.Design(dv=reaction_time, ivs=[condition])
        gr = design.graph
        main_effects = design.ivs
        random_effects = construct_random_effects_for_composed_measures(gr=gr, variables=main_effects)
        self.assertEqual(len(random_effects), 1)
        rs = random_effects.pop()
        self.assertIsInstance(rs, RandomSlope)
        self.assertIs(rs.iv, condition)
        self.assertIs(rs.groups, subject)

    # TODO: make a more generic version of this test        
    def test_construct_random_effects_for_composed_measures_between_items_within_participants_no_repeats(self):
        subject = ts.Unit("Subject")
        word = ts.Unit("Word")
        # Each subject has a two values for condition, which is nominal.
        # Verbose: Each instance of subject has two instances of a nominal variable condition. 
        # Informally: Each subjects sees two (both) conditions. 
        condition = subject.nominal("Word type", cardinality=2, number_of_instances=2)
        # Repeated measures
        # Each subject has a measure reaction time, which is numeric, for each instance of a word
        # Verbose: Each instance of subject has one instance of a numeric variable weight for each value of word. 
        # Informally: Each subject has a reaction time for each word.
        reaction_time = subject.numeric("Time", number_of_instances=word) 

        # Each condition has/is comprised of two words. 
        condition.has(word, number_of_instances=2)
        # ALTERNATIVELY, we could do something like the below (not implemented). It is a bit more complicated to calculate the number of instances, but still doable I think.
        # Each word has one value for condition (already defined above as a measure of subject)
        # word.has(condition, number_of_instances=1) # Condition has two units

        design = ts.Design(dv=reaction_time, ivs=[condition])
        gr = design.graph
        main_effects = design.ivs
        random_effects = construct_random_effects_for_composed_measures(gr=gr, variables=main_effects)
        self.assertEqual(len(random_effects), 1)
        rs = random_effects.pop()
        self.assertIsInstance(rs, RandomSlope)
        self.assertIs(rs.iv, condition)
        self.assertIs(rs.groups, subject)

    def test_find_largest_subset_of_variables_that_vary_within_unit_two_way_one_within(self):
        u = ts.Unit("Unit")
        a = u.nominal("Measure A", cardinality=2) # A is between-subjects
        b = u.nominal("Measure B", cardinality=2, number_of_instances=2) # B is within-subjects
        dv = u.numeric("Dependent variable")

        a.causes(dv)
        b.causes(dv)
        a.moderates(moderator=[b], on=dv) # AB --> get B

        design = ts.Design(dv=dv, ivs=[a, b])
        gr = design.graph

        main_effects = design.ivs
        interaction_effects = infer_interaction_effects(gr=gr, query=design, main_effects=main_effects)
        ixn = interaction_effects.pop()
        within_subset = find_largest_subset_of_variables_that_vary_within_unit(gr=gr, interaction_effect=ixn)
        self.assertEqual(len(within_subset), 1)
        self.assertIn(b, within_subset)
    
    def test_find_largest_subset_of_variables_that_vary_within_unit_two_way_two_within(self):
        u = ts.Unit("Unit")
        a = u.nominal("Measure A", cardinality=2, number_of_instances=2) # A is within-subjects
        b = u.nominal("Measure B", cardinality=2, number_of_instances=2) # B is within-subjects
        dv = u.numeric("Dependent variable")

        a.causes(dv)
        b.causes(dv)
        a.moderates(moderator=[b], on=dv) # AB --> get B

        design = ts.Design(dv=dv, ivs=[a, b])
        gr = design.graph

        main_effects = design.ivs
        interaction_effects = infer_interaction_effects(gr=gr, query=design, main_effects=main_effects)
        ixn = interaction_effects.pop()
        within_subset = find_largest_subset_of_variables_that_vary_within_unit(gr=gr, interaction_effect=ixn)
        self.assertEqual(len(within_subset), 2)
        self.assertIn(a, within_subset)
        self.assertIn(b, within_subset)
    
    def test_find_largest_subset_of_variables_that_vary_within_unit_three_way_two_within_one_between(self):
        u = ts.Unit("Unit")
        a = u.nominal("Measure A", cardinality=2) # A is between-subjects
        b = u.nominal("Measure B", cardinality=2, number_of_instances=2) # B is within-subjects
        c = u.nominal("Measure C", cardinality=2, number_of_instances=2) # B is within-subjects
        dv = u.numeric("Dependent variable")

        a.causes(dv)
        b.causes(dv)
        c.causes(dv)
        a.moderates(moderator=[b, c], on=dv) # BC --> get BC

        design = ts.Design(dv=dv, ivs=[a, b, c])
        gr = design.graph
        
        main_effects = design.ivs
        interaction_effects = infer_interaction_effects(gr=gr, query=design, main_effects=main_effects)
        ixn = interaction_effects.pop()
        within_subset = find_largest_subset_of_variables_that_vary_within_unit(gr=gr, interaction_effect=ixn)
        self.assertEqual(len(within_subset), 2)
        self.assertIn(b, within_subset)
        self.assertIn(c, within_subset)

    def test_get_variables_in_interaction_effect_two_way(self):
        u = ts.Unit("Unit")
        a = u.nominal("Measure A", cardinality=2) # A is between-subjects
        b = u.nominal("Measure B", cardinality=2, number_of_instances=2) # B is within-subjects
        dv = u.numeric("Dependent variable")

        a.causes(dv)
        b.causes(dv)
        a.moderates(moderator=[b], on=dv) 

        design = ts.Design(dv=dv, ivs=[a, b])
        gr = design.graph
        
        main_effects = design.ivs
        interaction_effects = infer_interaction_effects(gr=gr, query=design, main_effects=main_effects)
        self.assertEqual(len(interaction_effects), 1)
        ixn = interaction_effects.pop()
        variables = get_variables_in_interaction_effect(gr=gr, interaction_effect=ixn)
        self.assertEqual(len(variables), 2)
        self.assertIn(a, variables)
        self.assertIn(b, variables)

    def test_get_variables_in_interaction_effect_three_way(self):
        u = ts.Unit("Unit")
        a = u.nominal("Measure A", cardinality=2) # A is between-subjects
        b = u.nominal("Measure B", cardinality=2, number_of_instances=2) # B is within-subjects
        c = u.nominal("Measure C", cardinality=2, number_of_instances=2) # B is within-subjects
        dv = u.numeric("Dependent variable")

        a.causes(dv)
        b.causes(dv)
        c.causes(dv)
        a.moderates(moderator=[b, c], on=dv) 

        design = ts.Design(dv=dv, ivs=[a, b])
        gr = design.graph
        
        main_effects = design.ivs
        interaction_effects = infer_interaction_effects(gr=gr, query=design, main_effects=main_effects)
        ixn = interaction_effects.pop()
        variables = get_variables_in_interaction_effect(gr=gr, interaction_effect=ixn)
        self.assertEqual(len(variables), 3)
        self.assertIn(a, variables)
        self.assertIn(b, variables)
        self.assertIn(c, variables)

    def test_create_variable_from_set_of_variables_length_1(self):
        u = ts.Unit("Unit")
        a = u.nominal("Measure A", cardinality=2) # A is between-subjects
        
        variables = set()
        variables.add(a)

        var = create_variable_from_set_of_variables(variables=variables)
        self.assertIsInstance(var, Nominal)
        self.assertEqual(var.name, a.name)
        
    def test_create_variable_from_set_of_variables_length_2(self):
        u = ts.Unit("Unit")
        a = u.nominal("Measure A", cardinality=2) # A is between-subjects
        b = u.nominal("Measure B", cardinality=2, number_of_instances=2) # B is within-subjects
        
        variables = set()
        variables.add(a)
        variables.add(b)

        var = create_variable_from_set_of_variables(variables=variables)
        self.assertIsInstance(var, Nominal)
        self.assertTrue(a.name in var.name)
        self.assertTrue(b.name in var.name)

    def test_create_variable_from_set_of_variables_length_3(self):
        u = ts.Unit("Unit")
        a = u.nominal("Measure A", cardinality=2) # A is between-subjects
        b = u.nominal("Measure B", cardinality=2, number_of_instances=2) # B is within-subjects
        c = u.nominal("Measure C", cardinality=2, number_of_instances=2) # B is within-subjects

        variables = set()
        variables.add(a)
        variables.add(b)
        variables.add(c)

        var = create_variable_from_set_of_variables(variables=variables)
        self.assertIsInstance(var, Nominal)
        self.assertTrue(a.name in var.name)
        self.assertTrue(b.name in var.name)
        self.assertTrue(c.name in var.name)
        
    # Barr 2013 AB example
    def test_random_effects_for_two_way_interaction_one_between_one_within(self):
        u = ts.Unit("Unit")
        a = u.nominal("Measure A", cardinality=2, number_of_instances=2) # A is within-subjects
        b = u.nominal("Measure B", cardinality=2) # B is between-subjects
        dv = u.numeric("Dependent variable")

        a.causes(dv)
        b.causes(dv)
        a.moderates(moderator=[b], on=dv)

        design = ts.Design(dv=dv, ivs=[a, b])
        gr = design.graph
        
        main_effects = design.ivs
        interaction_effects = infer_interaction_effects(gr=gr, query=design, main_effects=main_effects)
        random_effects = construct_random_effects_for_interactions(gr=gr, interactions=interaction_effects)
        self.assertEqual(len(random_effects), 1)
        rs = random_effects.pop()
        self.assertIsInstance(rs, RandomSlope)
        self.assertEqual(rs.iv.name, a.name) # Should get A
        self.assertIs(rs.groups, u)

    def test_random_effects_for_two_way_interaction_two_between(self):
        u = ts.Unit("Unit")
        a = u.nominal("Measure A", cardinality=2) # A is between-subjects
        b = u.nominal("Measure B", cardinality=2) # B is between-subjects
        dv = u.numeric("Dependent variable")

        a.causes(dv)
        b.causes(dv)
        a.moderates(moderator=[b], on=dv)

        design = ts.Design(dv=dv, ivs=[a, b])
        gr = design.graph
        
        main_effects = design.ivs
        interaction_effects = infer_interaction_effects(gr=gr, query=design, main_effects=main_effects)
        random_effects = construct_random_effects_for_interactions(gr=gr, interactions=list(interaction_effects)) 
        self.assertEqual(len(random_effects), 0) # Should get no random effects!
    
    def test_random_effects_for_two_way_interaction_two_within(self):
        u = ts.Unit("Unit")
        a = u.nominal("Measure A", cardinality=2, number_of_instances=2) # A is within-subjects
        b = u.nominal("Measure B", cardinality=2, number_of_instances=2) # B is within-subjects
        dv = u.numeric("Dependent variable")

        a.causes(dv)
        b.causes(dv)
        a.moderates(moderator=[b], on=dv)

        design = ts.Design(dv=dv, ivs=[a, b])
        gr = design.graph
        
        main_effects = design.ivs
        interaction_effects = infer_interaction_effects(gr=gr, query=design, main_effects=main_effects)
        random_effects = construct_random_effects_for_interactions(gr=gr, interactions=list(interaction_effects)) 
        # Should get AB combo!
        # self.assertEqual(len(random_effects), 1)
        ixn = interaction_effects.pop()
        rs = random_effects.pop()
        self.assertIsInstance(rs, RandomSlope)
        self.assertEqual(rs.iv.name, ixn.name) # Should get A
        self.assertIs(rs.groups, u)


    # Barr 2013 time * group interaction example
    def test_random_effects_for_two_way_time_group_interaction(self):
        u = ts.Unit("Unit")
        time = ts.SetUp("Time")
        group = u.numeric("Group", number_of_instances=2) # TODO: A is within-subjects
        dv = u.numeric("Dependent variable", number_of_instances=time)

        time.associates_with(dv)
        group.causes(dv)
        time.moderates(moderator=[group], on=dv)

        design = ts.Design(dv=dv, ivs=[time, group])
        gr = design.graph
        
        main_effects = design.ivs
        interaction_effects = infer_interaction_effects(gr=gr, query=design, main_effects=main_effects)
        random_effects = construct_random_effects_for_interactions(gr=gr, interactions=list(interaction_effects)) 
        # TODO: 

    # Barr 2013 B, C, and BC example
    def test_random_effects_for_three_way_interaction_one_between_two_within(self):
        u = ts.Unit("Unit")
        a = u.nominal("Measure A", cardinality=2) # A is between-subjects
        b = u.nominal("Measure B", cardinality=2, number_of_instances=2) # B is within-subjects
        c = u.nominal("Measure C", cardinality=2, number_of_instances=2) # C is within-subjects
        dv = u.numeric("Dependent variable")

        a.causes(dv)
        b.causes(dv)
        c.causes(dv)
        a.moderates(moderator=[b, c], on=dv)

        design = ts.Design(dv=dv, ivs=[a, b, c])
        gr = design.graph
        
        main_effects = design.ivs
        interaction_effects = infer_interaction_effects(gr=gr, query=design, main_effects=main_effects)
        random_effects = construct_random_effects_for_interactions(gr=gr, interactions=interaction_effects) 
        # Should get BC!
        self.assertEqual(len(random_effects), 1)
        rs = random_effects.pop()
        self.assertIsInstance(rs, RandomSlope)
        self.assertIn(b.name, rs.iv.name)
        self.assertIn(c.name, rs.iv.name)
        self.assertNotIn(a.name, rs.iv.name)
        self.assertEqual(u.name, rs.groups.name)

    def test_random_effects_for_three_way_interaction_two_between_one_within(self):
        u = ts.Unit("Unit")
        a = u.nominal("Measure A", cardinality=2) # A is between-subjects
        b = u.nominal("Measure B", cardinality=2) # B is between-subjects
        c = u.nominal("Measure C", cardinality=2, number_of_instances=2) # B is within-subjects
        dv = u.numeric("Dependent variable")

        a.causes(dv)
        b.causes(dv)
        c.causes(dv)
        a.moderates(moderator=[b, c], on=dv)

        design = ts.Design(dv=dv, ivs=[a, b])
        gr = design.graph
        
        main_effects = [a, b, c]
        interaction_effects = infer_interaction_effects(gr=gr, query=design, main_effects=main_effects)
        random_effects = construct_random_effects_for_interactions(gr=gr, interactions=interaction_effects) 
        # Should get C!
        self.assertEqual(len(random_effects), 1)
        rs = random_effects.pop()
        self.assertIsInstance(rs, RandomSlope)
        self.assertIn(c.name, rs.iv.name)
        self.assertNotIn(a.name, rs.iv.name)
        self.assertNotIn(b.name, rs.iv.name)
        self.assertEqual(u.name, rs.groups.name)
    
    def test_random_effects_for_three_way_interaction_three_between(self):
        # Should get no random effects!
        u = ts.Unit("Unit")
        a = u.nominal("Measure A", cardinality=2) # A is between-subjects
        b = u.nominal("Measure B", cardinality=2) # B is between-subjects
        c = u.nominal("Measure C", cardinality=2) # B is between-subjects
        dv = u.numeric("Dependent variable")

        a.causes(dv)
        b.causes(dv)
        c.causes(dv)
        a.moderates(moderator=[b, c], on=dv)

        design = ts.Design(dv=dv, ivs=[a, b])
        gr = design.graph
        
        main_effects = design.ivs
        interaction_effects = infer_interaction_effects(gr=gr, query=design, main_effects=main_effects)
        random_effects = construct_random_effects_for_interactions(gr=gr, interactions=interaction_effects)
        # Should get none!
        self.assertEqual(len(random_effects), 0)

    # Combines all interactions for three-way
    def test_random_effects_for_all_two_way_three_way_interaction_one_between_two_within(self):
        u = ts.Unit("Unit")
        a = u.nominal("Measure A", cardinality=2) # A is between-subjects
        b = u.nominal("Measure B", cardinality=2, number_of_instances=2) # B is within-subjects
        c = u.nominal("Measure C", cardinality=2, number_of_instances=2) # B is within-subjects
        dv = u.numeric("Dependent variable")

        a.causes(dv)
        b.causes(dv)
        c.causes(dv)
        a.moderates(moderator=[b], on=dv) # AB --> get B
        a.moderates(moderator=[c], on=dv) # AC --> get C
        b.moderates(moderator=[c], on=dv) # BC --> get BC
        a.moderates(moderator=[b, c], on=dv) # BC --> get BC

        design = ts.Design(dv=dv, ivs=[a, b])
        gr = design.graph
        
        main_effects = [a, b, c]
        interaction_effects = infer_interaction_effects(gr=gr, query=design, main_effects=main_effects)
        random_effects = construct_random_effects_for_interactions(gr=gr, interactions=interaction_effects)
        self.assertEqual(len(random_effects), 4)
    
        count_bc_rs = 0
        has_bc_rs = False
        has_b_rs = False
        has_c_rs = False
        for re in random_effects:
            self.assertIsInstance(re, RandomSlope)
            if b.name in re.iv.name and c.name in re.iv.name: 
                self.assertNotIn(a.name, re.iv.name)
                self.assertIn(b.name, re.iv.name)
                self.assertIn(c.name, re.iv.name)
                self.assertEqual(u.name, re.groups.name)
                has_bc_rs = True
                count_bc_rs += 1
            elif b.name in re.iv.name: # and c.name not in re.iv.name
                self.assertIn(b.name, re.iv.name)
                self.assertNotIn(a.name, re.iv.name)
                self.assertNotIn(c.name, re.iv.name)
                self.assertEqual(u.name, re.groups.name)
                has_b_rs = True
            else: 
                self.assertIn(c.name, re.iv.name)
                self.assertIn(c.name, re.iv.name)
                self.assertNotIn(a.name, re.iv.name)
                self.assertNotIn(b.name, re.iv.name)
                self.assertEqual(u.name, re.groups.name)
                has_c_rs = True
        self.assertTrue(has_bc_rs)
        self.assertEqual(count_bc_rs, 2)
        self.assertTrue(has_b_rs)
        self.assertTrue(has_c_rs)

    # TODO
    def test_get_identifier_for_subset_interaction(self): 
        pass