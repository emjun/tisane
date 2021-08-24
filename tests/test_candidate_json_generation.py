from tisane.random_effects import RandomIntercept, RandomSlope
from unittest import main
from tisane.variable import Measure
import tisane as ts
from tisane.main import collect_model_candidates, collect_model_candidates
from tisane.graph_inference import (
    infer_interaction_effects_with_explanations,
    infer_random_effects_with_explanations,
    infer_main_effects_with_explanations,
    infer_interaction_effects_with_explanations,
    infer_random_effects_with_explanations,
)
from tisane.family_link_inference import infer_family_functions, infer_link_functions

import unittest


class CandidateJSONGenerationTest(unittest.TestCase):
    def test_main_effects_only(self):
        u0 = ts.Unit("Unit")
        m0 = u0.numeric("Measure_0")
        m1 = u0.numeric("Measure_1")
        dv = u0.numeric("Dependent_variable")

        design = ts.Design(dv=dv, ivs=[m0, m1])

        main_effects = set()
        main_effects.add(m0)
        main_effects.add(m1)

        interaction_effects = set()
        random_effects = set()
        family_candidates = infer_family_functions(query=design)
        link_candidates = set()
        family_link_paired = dict()
        for f in family_candidates:
            l = infer_link_functions(query=design, family=f)
            # Add Family: Link options
            assert f not in family_link_paired.keys()
            family_link_paired[f] = l

        combined_dict = collect_model_candidates(
            query=design,
            main_effects_candidates=main_effects,
            interaction_effects_candidates=interaction_effects,
            random_effects_candidates=random_effects,
            family_link_paired_candidates=family_link_paired,
        )
        self.assertEqual(len(combined_dict.keys()), 1)  # "input"
        input = combined_dict["input"]
        input_keys = input.keys()
        self.assertIsInstance(input, dict)
        self.assertEqual(len(input_keys), 6)
        self.assertIn("query", input_keys)
        self.assertIn("generated main effects", input_keys)
        self.assertIn("generated interaction effects", input_keys)
        self.assertIn("generated random effects", input_keys)
        self.assertIn("generated family, link functions", input_keys)
        self.assertIn("measures to units", input_keys)
        self.assertIsInstance(input["query"], dict)
        self.assertIsInstance(input["generated main effects"], list)
        self.assertIsInstance(input["generated interaction effects"], list)
        self.assertIsInstance(input["generated random effects"], dict)
        self.assertIsInstance(input["generated family, link functions"], dict)
        self.assertIsInstance(input["measures to units"], dict)
        gr = design.graph
        variables = gr.get_variables()
        measures = [v for v in variables if isinstance(v, Measure)]
        self.assertEqual(len(input["measures to units"].keys()), len(measures))

    def test_main_interaction(self):
        u0 = ts.Unit("Unit")
        m0 = u0.numeric("Measure_0")
        m1 = u0.numeric("Measure_1")
        m2 = u0.numeric("Measure_2")
        dv = u0.numeric("Dependent_variable")

        m0.causes(dv)
        m1.causes(dv)
        m2.moderates(moderator=m1, on=dv)

        design = ts.Design(dv=dv, ivs=[m0, m1, m2])
        gr = design.graph

        main_effects = set()
        main_effects.add(m0)
        main_effects.add(m1)
        main_effects.add(m2)

        (
            interaction_effects,
            interaction_explanations,
        ) = infer_interaction_effects_with_explanations(gr, design, main_effects)
        random_effects = set()
        family_candidates = infer_family_functions(query=design)
        link_candidates = set()
        family_link_paired = dict()
        for f in family_candidates:
            l = infer_link_functions(query=design, family=f)
            # Add Family: Link options
            assert f not in family_link_paired.keys()
            family_link_paired[f] = l

        combined_dict = collect_model_candidates(
            query=design,
            main_effects_candidates=main_effects,
            interaction_effects_candidates=interaction_effects,
            random_effects_candidates=random_effects,
            family_link_paired_candidates=family_link_paired,
        )
        self.assertEqual(len(combined_dict.keys()), 1)  # "input"
        input = combined_dict["input"]
        input_keys = input.keys()
        self.assertIsInstance(input, dict)
        self.assertEqual(len(input_keys), 6)
        self.assertIn("query", input_keys)
        self.assertIn("generated main effects", input_keys)
        self.assertIn("generated interaction effects", input_keys)
        self.assertIn("generated random effects", input_keys)
        self.assertIn("generated family, link functions", input_keys)
        self.assertIn("measures to units", input_keys)
        self.assertIsInstance(input["query"], dict)
        self.assertIsInstance(input["generated main effects"], list)
        self.assertIsInstance(input["generated interaction effects"], list)
        self.assertEqual(len(input["generated interaction effects"]), 1)
        self.assertIsInstance(input["generated random effects"], dict)
        self.assertIsInstance(input["generated family, link functions"], dict)
        self.assertIsInstance(input["measures to units"], dict)
        gr = design.graph
        variables = gr.get_variables()
        measures = [v for v in variables if isinstance(v, Measure)]
        self.assertEqual(len(input["measures to units"].keys()), len(measures))

    def test_main_interaction_random_intercept(self):
        u0 = ts.Unit("Unit")
        s0 = ts.SetUp("Time", order=[1, 2, 3, 4, 5])
        m0 = u0.numeric("Measure_0")
        m1 = u0.numeric("Measure_1")
        m2 = u0.numeric("Measure_2")
        dv = u0.numeric("Dependent_variable", number_of_instances=s0)

        m0.causes(dv)
        m1.causes(dv)
        m2.moderates(moderator=m1, on=dv)

        design = ts.Design(dv=dv, ivs=[m0, m1, m2, s0])  # main effect of Time
        gr = design.graph

        main_effects = set()
        main_effects.add(s0)
        main_effects.add(m0)
        main_effects.add(m1)
        main_effects.add(m2)

        (
            interaction_effects,
            interaction_explanations,
        ) = infer_interaction_effects_with_explanations(gr, design, main_effects)
        (random_effects, random_explanations) = infer_random_effects_with_explanations(
            gr=gr, query=design, main_effects=main_effects
        )
        family_candidates = infer_family_functions(query=design)
        link_candidates = set()
        family_link_paired = dict()
        for f in family_candidates:
            l = infer_link_functions(query=design, family=f)
            # Add Family: Link options
            assert f not in family_link_paired.keys()
            family_link_paired[f] = l

        combined_dict = collect_model_candidates(
            query=design,
            main_effects_candidates=main_effects,
            interaction_effects_candidates=interaction_effects,
            random_effects_candidates=random_effects,
            family_link_paired_candidates=family_link_paired,
        )
        self.assertEqual(len(combined_dict.keys()), 1)  # "input"
        input = combined_dict["input"]
        input_keys = input.keys()
        self.assertIsInstance(input, dict)
        self.assertEqual(len(input_keys), 6)
        self.assertIn("query", input_keys)
        self.assertIn("generated main effects", input_keys)
        self.assertIn("generated interaction effects", input_keys)
        self.assertIn("generated random effects", input_keys)
        self.assertIn("generated family, link functions", input_keys)
        self.assertIn("measures to units", input_keys)
        self.assertIsInstance(input["query"], dict)
        self.assertIsInstance(input["generated main effects"], list)
        self.assertIsInstance(input["generated interaction effects"], list)
        self.assertEqual(len(input["generated interaction effects"]), 1)
        self.assertIsInstance(input["generated random effects"], dict)
        self.assertEqual(len(input["generated random effects"]), 2)
        self.assertIsInstance(input["generated family, link functions"], dict)
        self.assertIsInstance(input["measures to units"], dict)
        gr = design.graph
        variables = gr.get_variables()
        measures = [v for v in variables if isinstance(v, Measure)]
        self.assertEqual(len(input["measures to units"].keys()), len(measures))

    def test_main_interaction_random_slope_from_interaction_one_variable(self):
        u = ts.Unit("Unit")
        a = u.nominal(
            "Measure A", cardinality=2, number_of_instances=2
        )  # A is within-subjects
        b = u.nominal("Measure B", cardinality=2)  # B is between-subjects
        dv = u.numeric("Dependent_variable")

        a.causes(dv)
        b.causes(dv)
        a.moderates(moderator=[b], on=dv)

        design = ts.Design(dv=dv, ivs=[a, b])
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
        family_candidates = infer_family_functions(query=design)
        link_candidates = set()
        family_link_paired = dict()
        for f in family_candidates:
            l = infer_link_functions(query=design, family=f)
            # Add Family: Link options
            assert f not in family_link_paired.keys()
            family_link_paired[f] = l

        combined_dict = collect_model_candidates(
            query=design,
            main_effects_candidates=main_effects,
            interaction_effects_candidates=interaction_effects,
            random_effects_candidates=random_effects,
            family_link_paired_candidates=family_link_paired,
        )
        self.assertEqual(len(random_effects), 1)
        input = combined_dict["input"]
        input_keys = input.keys()
        self.assertIsInstance(input, dict)
        self.assertEqual(len(input_keys), 6)
        self.assertIn("query", input_keys)
        self.assertIn("generated main effects", input_keys)
        self.assertIn("generated interaction effects", input_keys)
        self.assertIn("generated random effects", input_keys)
        self.assertIn("generated family, link functions", input_keys)
        self.assertIn("measures to units", input_keys)
        self.assertIsInstance(input["query"], dict)
        self.assertIsInstance(input["generated main effects"], list)
        self.assertIsInstance(input["generated interaction effects"], list)
        self.assertEqual(len(input["generated interaction effects"]), 1)
        self.assertIsInstance(input["generated random effects"], dict)
        self.assertEqual(len(input["generated random effects"]), 1)
        self.assertIn(u.name, input["generated random effects"].keys())
        self.assertEqual(len(input["generated random effects"][u.name]), 1)
        rs_dict = input["generated random effects"][u.name]
        self.assertIsInstance(rs_dict, dict)
        self.assertIn("random slope", rs_dict.keys())
        random_slope = rs_dict["random slope"][0]
        self.assertEqual(u.name, random_slope["groups"])
        self.assertEqual(a.name, random_slope["iv"])
        self.assertIsInstance(input["generated family, link functions"], dict)
        self.assertIsInstance(input["measures to units"], dict)
        gr = design.graph
        variables = gr.get_variables()
        measures = [v for v in variables if isinstance(v, Measure)]
        self.assertEqual(len(input["measures to units"].keys()), len(measures))

    def test_main_interaction_random_slope_from_interaction_two_variables(self):
        u = ts.Unit("Unit")
        a = u.nominal(
            "Measure A", cardinality=2, number_of_instances=2
        )  # A is within-subjects
        b = u.nominal(
            "Measure B", cardinality=2, number_of_instances=2
        )  # B is within-subjects
        dv = u.numeric("Dependent_variable")

        a.causes(dv)
        b.causes(dv)
        a.moderates(moderator=[b], on=dv)

        design = ts.Design(dv=dv, ivs=[a, b])
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
        family_candidates = infer_family_functions(query=design)
        link_candidates = set()
        family_link_paired = dict()
        for f in family_candidates:
            l = infer_link_functions(query=design, family=f)
            # Add Family: Link options
            assert f not in family_link_paired.keys()
            family_link_paired[f] = l

        combined_dict = collect_model_candidates(
            query=design,
            main_effects_candidates=main_effects,
            interaction_effects_candidates=interaction_effects,
            random_effects_candidates=random_effects,
            family_link_paired_candidates=family_link_paired,
        )
        self.assertEqual(len(random_effects), 1)
        input = combined_dict["input"]
        input_keys = input.keys()
        self.assertIsInstance(input, dict)
        self.assertEqual(len(input_keys), 6)
        self.assertIn("query", input_keys)
        self.assertIn("generated main effects", input_keys)
        self.assertIn("generated interaction effects", input_keys)
        self.assertIn("generated random effects", input_keys)
        self.assertIn("generated family, link functions", input_keys)
        self.assertIn("measures to units", input_keys)
        self.assertIsInstance(input["query"], dict)
        self.assertIsInstance(input["generated main effects"], list)
        self.assertIsInstance(input["generated interaction effects"], list)
        self.assertEqual(len(input["generated interaction effects"]), 1)
        self.assertIsInstance(input["generated random effects"], dict)
        self.assertEqual(len(input["generated random effects"]), 1)
        self.assertIn(u.name, input["generated random effects"].keys())
        self.assertEqual(len(input["generated random effects"][u.name]), 1)
        self.assertIsInstance(input["generated random effects"][u.name], dict)
        rs_dict = input["generated random effects"][u.name]
        self.assertIsInstance(rs_dict, dict)
        self.assertIn("random slope", rs_dict.keys())
        random_slope = rs_dict["random slope"][0]
        self.assertIsInstance(random_slope, dict)
        self.assertEqual(u.name, random_slope["groups"])
        ixn = interaction_effects.pop()
        self.assertEqual(ixn.name, random_slope["iv"])
        self.assertIsInstance(input["generated family, link functions"], dict)
        self.assertIsInstance(input["measures to units"], dict)
        gr = design.graph
        variables = gr.get_variables()
        measures = [v for v in variables if isinstance(v, Measure)]
        self.assertEqual(len(input["measures to units"].keys()), len(measures))

    def test_main_interaction_random_intercept_slope_correlated(self):
        subject = ts.Unit("Subject", cardinality=12)
        word = ts.Unit("Word", cardinality=4)
        condition = subject.nominal("Word_type", cardinality=2, number_of_instances=2)
        reaction_time = subject.numeric("Time", number_of_instances=word)  # repeats
        condition.has(word, number_of_instances=2)

        condition.causes(reaction_time)

        design = ts.Design(dv=reaction_time, ivs=[condition])
        gr = design.graph

        main_effects = design.ivs
        (
            interaction_effects,
            interaction_explanations,
        ) = infer_interaction_effects_with_explanations(gr, design, main_effects)
        (random_effects, random_explanations) = infer_random_effects_with_explanations(
            gr=gr,
            query=design,
            main_effects=main_effects,
            interaction_effects=interaction_effects,
        )
        self.assertEqual(len(random_effects), 3)  # Collapsed into 2 according to groups
        family_candidates = infer_family_functions(query=design)
        link_candidates = set()
        family_link_paired = dict()
        for f in family_candidates:
            l = infer_link_functions(query=design, family=f)
            # Add Family: Link options
            assert f not in family_link_paired.keys()
            family_link_paired[f] = l

        combined_dict = collect_model_candidates(
            query=design,
            main_effects_candidates=main_effects,
            interaction_effects_candidates=interaction_effects,
            random_effects_candidates=random_effects,
            family_link_paired_candidates=family_link_paired,
        )
        self.assertEqual(len(combined_dict.keys()), 1)  # "input"
        input = combined_dict["input"]
        input_keys = input.keys()
        self.assertIsInstance(input, dict)
        self.assertEqual(len(input_keys), 6)
        self.assertIn("query", input_keys)
        self.assertIn("generated main effects", input_keys)
        self.assertIn("generated interaction effects", input_keys)
        self.assertIn("generated random effects", input_keys)
        self.assertIn("generated family, link functions", input_keys)
        self.assertIn("measures to units", input_keys)
        self.assertIsInstance(input["query"], dict)
        self.assertIsInstance(input["generated main effects"], list)
        self.assertIsInstance(input["generated interaction effects"], list)
        self.assertEqual(len(input["generated interaction effects"]), 0)
        self.assertIsInstance(input["generated random effects"], dict)
        self.assertEqual(len(input["generated random effects"]), 2)
        self.assertIn(subject.name, input["generated random effects"].keys())
        self.assertIn(word.name, input["generated random effects"].keys())
        re_dict = input["generated random effects"][subject.name]
        self.assertEqual(len(re_dict), 3)
        has_subject_rs = False
        has_subject_ri = False
        has_correlated = False
        for k, v in re_dict.items():
            if k == "random slope":
                rs_list = v
                self.assertIsInstance(rs_list, list)
                self.assertEqual(len(rs_list), 1)
                rs = rs_list[0]
                self.assertIsInstance(rs, dict)
                self.assertEqual(rs["groups"], subject.name)
                self.assertEqual(rs["iv"], condition.name)
                has_subject_rs = True
            elif k == "random intercept":
                ri = v
                self.assertIsInstance(ri, dict)
                self.assertEqual(ri["groups"], subject.name)
                has_subject_ri = True
            elif k == "correlated":
                self.assertTrue(v)
                has_correlated = True
        self.assertTrue(has_subject_rs)
        self.assertTrue(has_subject_ri)
        self.assertTrue(has_correlated)
        self.assertEqual(len(input["generated random effects"][word.name]), 1)
        has_word_ri = False
        re_dict = input["generated random effects"][word.name]
        self.assertEqual(len(re_dict), 1)
        ri_dict = re_dict["random intercept"]
        self.assertEqual(ri_dict["groups"], word.name)
        self.assertIsInstance(input["generated family, link functions"], dict)
        self.assertIsInstance(input["measures to units"], dict)
        gr = design.graph
        variables = gr.get_variables()
        measures = [v for v in variables if isinstance(v, Measure)]
        self.assertEqual(len(input["measures to units"].keys()), len(measures))

    def test_random_effects_for_all_two_way_three_way_interaction_one_between_two_within(
        self,
    ):
        u = ts.Unit("Unit")
        a = u.nominal("Measure A", cardinality=2)  # A is between-subjects
        b = u.nominal(
            "Measure B", cardinality=2, number_of_instances=2
        )  # B is within-subjects
        c = u.nominal(
            "Measure C", cardinality=2, number_of_instances=2
        )  # B is within-subjects
        dv = u.numeric("Dependent_variable")

        a.causes(dv)
        b.causes(dv)
        c.causes(dv)
        a.moderates(moderator=[b], on=dv)  # AB --> get B
        a.moderates(moderator=[c], on=dv)  # AC --> get C
        b.moderates(moderator=[c], on=dv)  # BC --> get BC
        a.moderates(moderator=[b, c], on=dv)  # BC --> get BC

        design = ts.Design(dv=dv, ivs=[a, b])
        gr = design.graph

        main_effects = [a, b, c]
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
        self.assertEqual(len(random_effects), 3)
        family_candidates = infer_family_functions(query=design)
        link_candidates = set()
        family_link_paired = dict()
        for f in family_candidates:
            l = infer_link_functions(query=design, family=f)
            # Add Family: Link options
            assert f not in family_link_paired.keys()
            family_link_paired[f] = l
        combined_dict = collect_model_candidates(
            query=design,
            main_effects_candidates=main_effects,
            interaction_effects_candidates=interaction_effects,
            random_effects_candidates=random_effects,
            family_link_paired_candidates=family_link_paired,
        )
        self.assertEqual(len(combined_dict.keys()), 1)  # "input"
        input = combined_dict["input"]
        input_keys = input.keys()
        self.assertIsInstance(input, dict)
        self.assertEqual(len(input_keys), 6)
        self.assertIn("query", input_keys)
        self.assertIn("generated main effects", input_keys)
        self.assertIn("generated interaction effects", input_keys)
        self.assertIn("generated random effects", input_keys)
        self.assertIn("generated family, link functions", input_keys)
        self.assertIn("measures to units", input_keys)
        self.assertIsInstance(input["query"], dict)
        self.assertIsInstance(input["generated main effects"], list)
        self.assertIsInstance(input["generated interaction effects"], list)
        self.assertEqual(len(input["generated interaction effects"]), 4)
        self.assertIsInstance(input["generated random effects"], dict)
        self.assertEqual(len(input["generated random effects"]), 1)
        self.assertIn(u.name, input["generated random effects"].keys())
        random_slopes = input["generated random effects"][u.name]["random slope"]
        self.assertEqual(len(random_slopes), 3)
        has_b_rs = False
        has_c_rs = False
        has_bc_rs = False
        for re in random_slopes:
            if b.name == re["iv"]:
                has_b_rs = True
            elif c.name == re["iv"]:
                has_c_rs = True
            elif b.name in re["iv"] and c.name in re["iv"]:
                self.assertEqual(re["iv"], f"{b.name}*{c.name}")
                has_bc_rs = True
        self.assertTrue(has_b_rs)
        self.assertTrue(has_c_rs)
        self.assertTrue(has_bc_rs)

    def test_collect_main_candidates_and_explanations(self):
        u0 = ts.Unit("Unit")
        m0 = u0.numeric("Measure_0")
        m1 = u0.numeric("Measure_1")
        m2 = u0.numeric("Measure_2")
        dv = u0.numeric("Dependent_variable")

        # m0 is the common (causal) ancestor
        m0.causes(m1)
        m0.causes(m2)

        m1.causes(dv)
        m2.causes(dv)

        design = ts.Design(dv=dv, ivs=[m1, m2])
        gr = design.graph

        (main_effects, main_explanations) = infer_main_effects_with_explanations(
            gr=gr, query=design
        )
        self.assertIsInstance(main_effects, set)
        self.assertIsInstance(main_explanations, dict)

    def test_collect_infer_candidates_and_explanations(self):
        u0 = ts.Unit("Unit")
        m0 = u0.numeric("Measure_0")
        m1 = u0.numeric("Measure_1")
        m2 = u0.numeric("Measure_2")
        dv = u0.numeric("Dependent_variable")

        m0.causes(dv)
        m1.causes(dv)
        m2.moderates(moderator=m1, on=dv)

        design = ts.Design(dv=dv, ivs=[m0, m1])  # omit m2
        gr = design.graph

        (main_effects, main_explanations) = infer_main_effects_with_explanations(
            gr=gr, query=design
        )
        (
            interaction_effects,
            interaction_explanations,
        ) = infer_interaction_effects_with_explanations(gr, design, main_effects)
        self.assertIsInstance(interaction_effects, set)
        self.assertIsInstance(interaction_explanations, dict)

    def test_collect_random_candidates_and_explanations(self):
        u = ts.Unit("Unit")
        a = u.nominal("Measure A", cardinality=2)  # A is between-subjects
        b = u.nominal(
            "Measure B", cardinality=2, number_of_instances=2
        )  # B is within-subjects
        c = u.nominal(
            "Measure C", cardinality=2, number_of_instances=2
        )  # B is within-subjects
        dv = u.numeric("Dependent_variable")

        a.causes(dv)
        b.causes(dv)
        b.associates_with(c)
        c.causes(dv)
        a.moderates(moderator=[b], on=dv)  # AB --> get B
        a.moderates(moderator=[c], on=dv)  # AC --> get C
        b.moderates(moderator=[c], on=dv)  # BC --> get BC
        a.moderates(moderator=[b, c], on=dv)  # ABC --> get BC

        design = ts.Design(dv=dv, ivs=[a, b])
        gr = design.graph

        (main_effects, main_explanations) = infer_main_effects_with_explanations(
            gr=gr, query=design
        )
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
        self.assertIsInstance(random_effects, set)
        self.assertIsInstance(random_explanations, dict)
        self.assertEqual(len(random_effects), len(random_explanations))
        for k, v in random_explanations.items():
            k_elements = k.split(", ")
            # Is this a random slope?
            if len(k_elements) == 3:
                groups, iv, random_class_name = k_elements
                self.assertEqual(random_class_name, RandomSlope.__name__)
            else:
                # This is a random intercept
                assert len(k_elements) == 2
                groups, random_class_name = k_elements
                self.assertEqual(random_class_name, RandomIntercept.__name__)

        for re in random_effects:
            if isinstance(re, RandomIntercept):
                name_key = f"{re.groups.name}, {type(re).__name__}"
            else:
                assert isinstance(re, RandomSlope)
                name_key = f"{re.groups.name}, {re.iv.name}, {type(re).__name__}"
            self.assertIn(name_key, random_explanations.keys())

    # TODO: Check that the explanations are correct
    # TODO: Add tests from effects infrence helpers that put all these together
