"""
Tests that given an output JSON file, Tisane constructs the correct statistical model object, which is used to generate code/a script for fitting a statistical model
"""
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
def get_family_link_paired_candidates(design: ts.Design) -> Dict[AbstractFamily, Set[AbstractLink]]:
    family_candidates = infer_family_functions(query=design)
    family_link_paired = dict()
    for f in family_candidates: 
        l = infer_link_functions(query=design, family=f)
        # Add Family: Link options 
        assert(f not in family_link_paired.keys())
        family_link_paired[f] = l

    return family_link_paired


class ConstructStatisticalModelTest(unittest.TestCase):
    def test_construct_main_only(self):
        u0 = ts.Unit("Unit")
        m0 = u0.numeric("Measure 0")
        m1 = u0.numeric("Measure 1")
        dv = u0.numeric("Dependent variable")

        design = ts.Design(dv=dv, ivs=[m0, m1])

        main_effects = set(design.ivs)
        interaction_effects = set()
        random_effects = set()
        family_link_paired = get_family_link_paired_candidates(design=design)

        output_filename = "main_only.json"
        output_path = os.path.join(dir, output_filename)
        sm = construct_statistical_model(output_path, query=design, main_effects_candidates=main_effects, interaction_effects_candidates=interaction_effects, random_effects_candidates=random_effects, family_link_paired_candidates=family_link_paired)
        self.assertIsNotNone(sm)
        self.Equal(main_effects, sm.main_effects)
        self.Equal(interaction_effects, sm.interaction_effects)
        self.Equal(random_effects, sm.random_effects)
        self.In(sm.family.__name__ in family_link_paired.keys())
        link_names = [l.name for l in family_link_paired[sm.family.__name__]]
        self.In(sm.link.__name__, link_names)