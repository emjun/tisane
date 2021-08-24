"""
Tests that given an output JSON file, Tisane constructs the correct statistical model object, which is used to generate code/a script for fitting a statistical model
"""
from tisane.random_effects import (
    CorrelatedRandomSlopeAndIntercept,
    RandomIntercept,
    RandomSlope,
    UncorrelatedRandomSlopeAndIntercept,
)
from tisane.graph_inference import (
    infer_interaction_effects_with_explanations,
    infer_main_effects_with_explanations,
    infer_random_effects_with_explanations,
)
from tisane.family import AbstractFamily, AbstractLink
from tisane.family_link_inference import infer_family_functions, infer_link_functions
from tisane.main import construct_statistical_model

import tisane as ts
import pandas as pd
from typing import Dict, Set
import os
import unittest


test_data_repo_name = "output_json_files/"
dir = os.path.dirname(__file__)
dir = os.path.join(dir, test_data_repo_name)
# df = pd.read_csv(os.path.join(dir, "pigs.csv"))

### HELPER to reduce redundancy across test cases
def get_family_link_paired_candidates(
    design: ts.Design,
) -> Dict[AbstractFamily, Set[AbstractLink]]:
    family_candidates = infer_family_functions(query=design)
    family_link_paired = dict()
    for f in family_candidates:
        l = infer_link_functions(query=design, family=f)
        # Add Family: Link options
        assert f not in family_link_paired.keys()
        family_link_paired[f] = l

    return family_link_paired


class ConstructStatisticalModelTest(unittest.TestCase):
    def test_construct_main_only(self):
        u0 = ts.Unit("Unit")
        m0 = u0.numeric("Measure_0")
        m1 = u0.numeric("Measure_1")
        dv = u0.numeric("Dependent_variable")

        design = ts.Design(dv=dv, ivs=[m0, m1])

        main_effects = set(design.ivs)
        interaction_effects = set()
        random_effects = set()
        family_link_paired = get_family_link_paired_candidates(design=design)

        output_filename = "main_only.json"
        output_path = os.path.join(dir, output_filename)
        sm = construct_statistical_model(
            output_path,
            query=design,
            main_effects_candidates=main_effects,
            interaction_effects_candidates=interaction_effects,
            random_effects_candidates=random_effects,
            family_link_paired_candidates=family_link_paired,
        )
        self.assertIsNotNone(sm)
        self.assertEqual(design.dv, sm.dependent_variable)
        self.assertEqual(main_effects, sm.main_effects)
        self.assertEqual(interaction_effects, sm.interaction_effects)
        self.assertEqual(random_effects, sm.random_effects)
        family = sm.family_function
        self.assertIn(family, family_link_paired.keys())
        link = sm.link_function
        self.assertIn(link, family_link_paired[family])

    def test_construct_main_interaction(self):
        u0 = ts.Unit("Unit")
        m0 = u0.numeric("Measure_0")
        m1 = u0.numeric("Measure_1")
        dv = u0.numeric("Dependent_variable")

        m0.moderates(moderator=m1, on=dv)
        design = ts.Design(dv=dv, ivs=[m0, m1])
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
        random_effects = set()
        family_link_paired = get_family_link_paired_candidates(design=design)

        output_filename = "main_interaction.json"
        output_path = os.path.join(dir, output_filename)
        sm = construct_statistical_model(
            output_path,
            query=design,
            main_effects_candidates=main_effects,
            interaction_effects_candidates=interaction_effects,
            random_effects_candidates=random_effects,
            family_link_paired_candidates=family_link_paired,
        )
        self.assertIsNotNone(sm)
        self.assertEqual(design.dv, sm.dependent_variable)
        self.assertEqual(main_effects, sm.main_effects)
        self.assertEqual(interaction_effects, sm.interaction_effects)
        self.assertEqual(random_effects, sm.random_effects)
        family = sm.family_function
        self.assertIn(family, family_link_paired.keys())
        link = sm.link_function
        self.assertIn(link, family_link_paired[family])

    def test_construct_main_correlated_random_slope_intercept(self):
        subject = ts.Unit("Subject", cardinality=12)
        word = ts.Unit("Word", cardinality=4)
        condition = subject.nominal("Word_type", cardinality=2, number_of_instances=2)
        reaction_time = subject.numeric("Time", number_of_instances=word)
        condition.has(word, number_of_instances=2)

        condition.causes(reaction_time)

        design = ts.Design(dv=reaction_time, ivs=[condition])
        gr = design.graph

        main_effects = set(design.ivs)
        interaction_effects = set()
        (random_effects, random_explanations) = infer_random_effects_with_explanations(
            gr=gr,
            query=design,
            main_effects=main_effects,
            interaction_effects=interaction_effects,
        )
        family_link_paired = get_family_link_paired_candidates(design=design)

        output_filename = "main_random_slope_random_intercept_correlated.json"
        output_path = os.path.join(dir, output_filename)
        sm = construct_statistical_model(
            output_path,
            query=design,
            main_effects_candidates=main_effects,
            interaction_effects_candidates=interaction_effects,
            random_effects_candidates=random_effects,
            family_link_paired_candidates=family_link_paired,
        )
        self.assertIsNotNone(sm)
        self.assertEqual(design.dv, sm.dependent_variable)
        self.assertEqual(main_effects, sm.main_effects)
        self.assertEqual(interaction_effects, sm.interaction_effects)
        has_ri = False
        has_correlated_ri_rs = False
        for re in sm.random_effects:
            if isinstance(re, CorrelatedRandomSlopeAndIntercept):
                rs = re.random_slope
                ri = re.random_intercept
                self.assertIn(rs, random_effects)
                self.assertIn(ri, random_effects)
                has_correlated_ri_rs = True
            elif isinstance(re, UncorrelatedRandomSlopeAndIntercept):
                rs = re.random_slope
                ri = re.random_intercept
                self.assertIn(rs, random_effects)
                self.assertIn(ri, random_effects)
            elif isinstance(re, RandomSlope):
                self.assertIn(re, random_effects)
            elif isinstance(re, RandomIntercept):
                self.assertIn(re, random_effects)
                has_ri = True
        self.assertTrue(has_ri)
        self.assertTrue(has_correlated_ri_rs)
        self.assertEqual(len(sm.random_effects), 2)
        family = sm.family_function
        self.assertIn(family, family_link_paired.keys())
        link = sm.link_function
        self.assertIn(link, family_link_paired[family])
