"""
Tests how model effects structures are inferred
NOTE: The tests are only to test, not to make any statements about how these variables relate in the real world
"""

import tisane as ts
from tisane import graph_inference
from tisane.graph_inference import (
    infer_main_effects_with_explanations,
    infer_interaction_effects_with_explanations,
    infer_random_effects_with_explanations,
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
from tisane.random_effects import RandomIntercept, RandomSlope
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

        (main_effects, main_explanations) = infer_main_effects_with_explanations(
            gr, design
        )

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

        (main_effects, main_explanations) = infer_main_effects_with_explanations(
            gr, design
        )

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

        (main_effects, main_explanations) = infer_main_effects_with_explanations(
            gr, design
        )

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

        (main_effects, main_explanations) = infer_main_effects_with_explanations(
            gr, design
        )

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

        (main_effects, main_explanations) = infer_main_effects_with_explanations(
            gr, design
        )

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

        (main_effects, main_explanations) = infer_main_effects_with_explanations(
            gr, design
        )

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

        (main_effects, main_explanations) = infer_main_effects_with_explanations(
            gr, design
        )

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

        (main_effects, main_explanations) = infer_main_effects_with_explanations(
            gr, design
        )

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

        (main_effects, main_explanations) = infer_main_effects_with_explanations(
            gr, design
        )

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

        design = ts.Design(dv=dv, ivs=[m0, m1])  # omit m2

        gr = design.graph

        main_effects = [m0, m1]
        (
            interaction_effects,
            interaction_explanations,
        ) = infer_interaction_effects_with_explanations(gr, design, main_effects)
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
        (
            interaction_effects,
            interaction_explanations,
        ) = infer_interaction_effects_with_explanations(gr, design, main_effects)
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

    def test_random_repeats(self):
        u0 = ts.Unit("Unit")
        s0 = ts.SetUp("Time", order=[1, 2, 3, 4, 5])
        dv = u0.numeric("Dependent variable", number_of_instances=s0)

        design = ts.Design(dv=dv, ivs=[s0])  # main effect of Time
        gr = design.graph

        main_effects = [s0]
        (random_effects, random_explanations) = infer_random_effects_with_explanations(
            gr=gr, query=design, main_effects=main_effects
        )
        self.assertEqual(len(random_effects), 2)
        has_unit_ri = False
        has_time_ri = False
        for ri in random_effects:
            self.assertIsInstance(ri, RandomIntercept)
            if isinstance(ri.groups, ts.Unit):
                self.assertIs(ri.groups, u0)
                has_unit_ri = True
            elif isinstance(ri.groups, ts.SetUp):
                self.assertIs(ri.groups, s0)
                has_time_ri = True
        self.assertTrue(has_unit_ri)
        self.assertTrue(has_time_ri)

    def test_random_nested(self):
        u0 = ts.Unit("Unit 0")
        m0 = u0.numeric("Measure 0")
        u1 = ts.Unit("Unit 1")
        dv = u0.numeric("Dependent variable")

        u0.nests_within(u1)

        design = ts.Design(dv=dv, ivs=[m0])
        gr = design.graph

        main_effects = design.ivs
        (random_effects, random_explanations) = infer_random_effects_with_explanations(
            gr=gr, query=design, main_effects=main_effects
        )
        self.assertEqual(len(random_effects), 1)
        ri = random_effects.pop()
        self.assertIsInstance(ri, RandomIntercept)
        self.assertIs(ri.groups, u1)

    # Barr et al. 2013 example
    def test_composed_measures_with_repeats(self):
        subject = ts.Unit("Subject", cardinality=12)
        word = ts.Unit("Word", cardinality=4)
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
        (random_effects, random_explanations) = infer_random_effects_with_explanations(
            gr=gr, query=design, main_effects=main_effects
        )
        self.assertEqual(
            len(random_effects), 3
        )  # two random intercepts, 1 random slope
        for re in random_effects:
            if isinstance(re, RandomSlope):
                self.assertIs(re.iv, condition)
                self.assertIs(re.groups, subject)
            else:
                self.assertIsInstance(re, RandomIntercept)
                if re.groups != subject:
                    self.assertIs(re.groups, word)

    # Barr 2013 time * group interaction example:
    # "For example, consider a design with two independent groups of subjects,
    # where there are observations at multiple time points for each subject.
    # When testing the time-by-group interaction, the model should include a
    # random slope for the continuous variable of time..."
    def test_random_effects_for_two_way_time_group_interaction(self):
        subject = ts.Unit("Unit")
        time = ts.SetUp("Time")
        condition = subject.nominal(
            "Condition", cardinality=2, number_of_instances=1
        )  # "two independent groups of subjects"
        dv = subject.numeric(
            "Dependent variable", number_of_instances=time
        )  # within-subject

        time.associates_with(dv)
        condition.causes(dv)
        time.moderates(moderator=[condition], on=dv)

        design = ts.Design(dv=dv, ivs=[time, condition])
        gr = design.graph

        main_effects = design.ivs
        (
            interaction_effects,
            interaction_explanations,
        ) = infer_interaction_effects_with_explanations(
            gr=gr, query=design, main_effects=main_effects
        )
        (random_effects, random_explanations) = infer_random_effects_with_explanations(
            gr=gr,
            query=design,
            main_effects=main_effects,
            interaction_effects=interaction_effects,
        )
        #     gr=gr, query=design, main_effects

        #     interactions=list(interaction_effects)
        # )
        self.assertEqual(len(random_effects), 1)
        rs = random_effects.pop()
        self.assertIsInstance(rs, RandomSlope)
        self.assertEqual(rs.iv.name, time.name)
        self.assertIs(rs.groups, subject)

    # def test_composed_measures_no_repeats(self):
    #     subject = ts.Unit("Subject")
    #     word = ts.Unit("Word")
    #     # Each subject has a two values for condition, which is nominal.
    #     # Verbose: Each instance of subject has two instances of a nominal variable condition.
    #     # Informally: Each subjects sees two (both) conditions.
    #     condition = subject.nominal("Word type", cardinality=2, number_of_instances=2)
    #     # Repeated measures
    #     # Each subject has a measure reaction time, which is numeric, for each instance of a word
    #     # Verbose: Each instance of subject has one instance of a numeric variable weight for each value of word.
    #     # Informally: Each subject has a reaction time for each word.
    #     reaction_time = subject.numeric("Time", number_of_instances=1) # TODO: DOES THIS EVEN MAKE SENSE!?

    #     # Each condition has/is comprised of two words.
    #     condition.has(word, number_of_instances=2)
    #     # ALTERNATIVELY, we could do something like the below (not implemented). It is a bit more complicated to calculate the number of instances, but still doable I think.
    #     # Each word has one value for condition (already defined above as a measure of subject)
    #     # word.has(condition, number_of_instances=1) # Condition has two units

    #     design = ts.Design(dv=reaction_time, ivs=[condition])
    #     gr = design.graph
    #     main_effects = design.ivs
    #     (random_effects, random_explanations) = infer_random_effects_with_explanations(gr=gr, query=design, main_effects=main_effects)
    #     self.assertEqual(len(random_effects), 3) # two random intercepts, 1 random slope
    #     # TODO: How to ask if slope and intercept are correlated?
