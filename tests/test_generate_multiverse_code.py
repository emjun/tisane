"""
Tests methods called to generate multiverse code
"""
from tisane.family import AbstractFamily, AbstractLink
from tisane.main import (
    check_design_ivs,
    check_design_dv,
    construct_statistical_model,
    infer_family_functions,
    infer_link_functions,
    infer_main_effects_with_explanations,
    infer_interaction_effects_with_explanations,
    infer_random_effects_with_explanations,
)
from tisane.code_generator import (
    generate_statsmodels_formula,
    generate_statsmodels_family,
    generate_statsmodels_link,
    generate_statsmodels_model,
    generate_pymer4_formula,
)
import tisane as ts
import pandas as pd
from typing import Dict, Set
from pathlib import Path
import os
import unittest

test_data_repo_name = "output_json_files/"
test_script_repo_name = "output_scripts/"
dir = os.path.dirname(__file__)
data_dir = os.path.join(dir, test_data_repo_name)
script_dir = os.path.join(dir, test_script_repo_name)

### HELPERS to reduce redundancy across test cases
model_template = """
    model = smf.glm(formula={formula}, data=df, family=sm.families.{family_name}(sm.families.links.{link_obj}))
    res = model.fit()
    print(res.summary())
    return model
"""


def absolute_path(p: str) -> str:
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), p)


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


class GenerateMultiverseCodeHelpersTest(unittest.TestCase):
    def test_generate_statsmodels_formula_template(self):
        u0 = ts.Unit("Unit")