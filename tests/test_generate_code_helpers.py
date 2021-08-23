"""
Tests methods called to generate code from a statistical model
"""
from tisane.family import AbstractFamily, AbstractLink
from tisane.main import construct_statistical_model, infer_family_functions, infer_link_functions, infer_main_effects_with_explanations, infer_interaction_effects_with_explanations
from tisane.code_generator import generate_statsmodels_formula, generate_statsmodels_family, generate_statsmodels_link, generate_statsmodels_model
import tisane as ts
from typing import Dict, Set
import os
import unittest

test_data_repo_name = "output_json_files/"
test_script_repo_name = "output_scripts/"
dir = os.path.dirname(__file__)
data_dir = os.path.join(dir, test_data_repo_name)
script_dir = os.path.join(dir, test_script_repo_name)

### HELPER to reduce redundancy across test cases
model_template =  """
model = smf.glm(formula={formula}, data=df, family=sm.families.{family_name}({link_obj})).fit()
print(model)
"""

def get_family_link_paired_candidates(design: ts.Design) -> Dict[AbstractFamily, Set[AbstractLink]]:
    family_candidates = infer_family_functions(query=design)
    family_link_paired = dict()
    for f in family_candidates: 
        l = infer_link_functions(query=design, family=f)
        # Add Family: Link options 
        assert(f not in family_link_paired.keys())
        family_link_paired[f] = l

    return family_link_paired

class GenerateCodeHelpersTest(unittest.TestCase):
    def test_generate_statsmodels_formula_main_only(self):
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
        output_path = os.path.join(data_dir, output_filename)
        sm = construct_statistical_model(output_path, query=design, main_effects_candidates=main_effects, interaction_effects_candidates=interaction_effects, random_effects_candidates=random_effects, family_link_paired_candidates=family_link_paired)
        self.assertIsNotNone(sm)
        self.assertEqual(main_effects, sm.main_effects)
        self.assertEqual(interaction_effects, sm.interaction_effects)
        self.assertEqual(random_effects, sm.random_effects)
        family = sm.family_function
        self.assertIn(family, family_link_paired.keys())
        link = sm.link_function
        self.assertIn(link, family_link_paired[family])

        code = generate_statsmodels_formula(statistical_model=sm)
        reference_code = "'Dependent_variable ~ Measure_0 + Measure_1'"
        self.assertEqual(code, reference_code)

    def test_generate_statsmodels_formula_main_interaction(self):
        u0 = ts.Unit("Unit")
        m0 = u0.numeric("Measure_0")
        m1 = u0.numeric("Measure_1")
        dv = u0.numeric("Dependent_variable")

        m0.moderates(moderator=m1, on=dv)
        design = ts.Design(dv=dv, ivs=[m0, m1])
        gr = design.graph

        (main_effects, main_explanations) = infer_main_effects_with_explanations(gr=gr, query=design)
        (interaction_effects, interaction_explanations) = infer_interaction_effects_with_explanations(gr=gr, query=design, main_effects=main_effects)
        random_effects = set()
        family_link_paired = get_family_link_paired_candidates(design=design)

        output_filename = "main_interaction.json"
        output_path = os.path.join(data_dir, output_filename)
        sm = construct_statistical_model(output_path, query=design, main_effects_candidates=main_effects, interaction_effects_candidates=interaction_effects, random_effects_candidates=random_effects, family_link_paired_candidates=family_link_paired)
        self.assertIsNotNone(sm)
        self.assertEqual(design.dv, sm.dependent_variable)
        self.assertEqual(main_effects, sm.main_effects)
        self.assertEqual(interaction_effects, sm.interaction_effects)
        self.assertEqual(random_effects, sm.random_effects)
        family = sm.family_function
        self.assertIn(family, family_link_paired.keys())
        link = sm.link_function
        self.assertIn(link, family_link_paired[family])

        code = generate_statsmodels_formula(statistical_model=sm)
        reference_code = "'Dependent_variable ~ Measure_0 + Measure_1 + Measure_0*Measure_1'"
        self.assertEqual(code, reference_code)

    # def test_generate_statsmodels_formula_main_interaction_random_intercept(self):
    #     pass

    # def test_generate_statsmodels_formula_main_interaction_random_slope(self):
    #     pass

    def test_generate_statsmodels_family_Gaussian(self):
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
        output_path = os.path.join(data_dir, output_filename)
        sm = construct_statistical_model(output_path, query=design, main_effects_candidates=main_effects, interaction_effects_candidates=interaction_effects, random_effects_candidates=random_effects, family_link_paired_candidates=family_link_paired)
        self.assertIsNotNone(sm)
        self.assertEqual(main_effects, sm.main_effects)
        self.assertEqual(interaction_effects, sm.interaction_effects)
        self.assertEqual(random_effects, sm.random_effects)
        family = sm.family_function
        self.assertIn(family, family_link_paired.keys())
        link = sm.link_function
        self.assertIn(link, family_link_paired[family])

        code = generate_statsmodels_family(statistical_model=sm)
        reference_code = "Gaussian"
        self.assertEqual(code, reference_code)

    def test_generate_statsmodels_family_Poisson(self):
        u0 = ts.Unit("Unit")
        m0 = u0.numeric("Measure_0")
        m1 = u0.numeric("Measure_1")
        dv = u0.numeric("Dependent_variable")

        m0.moderates(moderator=m1, on=dv)
        design = ts.Design(dv=dv, ivs=[m0, m1])
        gr = design.graph

        (main_effects, main_explanations) = infer_main_effects_with_explanations(gr=gr, query=design)
        (interaction_effects, interaction_explanations) = infer_interaction_effects_with_explanations(gr=gr, query=design, main_effects=main_effects)
        random_effects = set()
        family_link_paired = get_family_link_paired_candidates(design=design)

        output_filename = "main_interaction.json"
        output_path = os.path.join(data_dir, output_filename)
        sm = construct_statistical_model(output_path, query=design, main_effects_candidates=main_effects, interaction_effects_candidates=interaction_effects, random_effects_candidates=random_effects, family_link_paired_candidates=family_link_paired)
        self.assertIsNotNone(sm)
        self.assertEqual(design.dv, sm.dependent_variable)
        self.assertEqual(main_effects, sm.main_effects)
        self.assertEqual(interaction_effects, sm.interaction_effects)
        self.assertEqual(random_effects, sm.random_effects)
        family = sm.family_function
        self.assertIn(family, family_link_paired.keys())
        link = sm.link_function
        self.assertIn(link, family_link_paired[family])

        code = generate_statsmodels_family(statistical_model=sm)
        reference_code = "Poisson"
        self.assertEqual(code, reference_code)

    # TODO: Add family for Multinomial?

    def test_generate_statsmodels_link_Identity(self):
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
        output_path = os.path.join(data_dir, output_filename)
        sm = construct_statistical_model(output_path, query=design, main_effects_candidates=main_effects, interaction_effects_candidates=interaction_effects, random_effects_candidates=random_effects, family_link_paired_candidates=family_link_paired)
        self.assertIsNotNone(sm)
        self.assertEqual(main_effects, sm.main_effects)
        self.assertEqual(interaction_effects, sm.interaction_effects)
        self.assertEqual(random_effects, sm.random_effects)
        family = sm.family_function
        self.assertIn(family, family_link_paired.keys())
        link = sm.link_function
        self.assertIn(link, family_link_paired[family])

        code = generate_statsmodels_link(statistical_model=sm)
        reference_code = "identity()"
        self.assertEqual(code, reference_code)

    def test_generate_statsmodels_link_Squareroot(self):
        u0 = ts.Unit("Unit")
        m0 = u0.numeric("Measure_0")
        m1 = u0.numeric("Measure_1")
        dv = u0.numeric("Dependent_variable")

        m0.moderates(moderator=m1, on=dv)
        design = ts.Design(dv=dv, ivs=[m0, m1])
        gr = design.graph

        (main_effects, main_explanations) = infer_main_effects_with_explanations(gr=gr, query=design)
        (interaction_effects, interaction_explanations) = infer_interaction_effects_with_explanations(gr=gr, query=design, main_effects=main_effects)
        random_effects = set()
        family_link_paired = get_family_link_paired_candidates(design=design)

        output_filename = "main_interaction.json"
        output_path = os.path.join(data_dir, output_filename)
        sm = construct_statistical_model(output_path, query=design, main_effects_candidates=main_effects, interaction_effects_candidates=interaction_effects, random_effects_candidates=random_effects, family_link_paired_candidates=family_link_paired)
        self.assertIsNotNone(sm)
        self.assertEqual(design.dv, sm.dependent_variable)
        self.assertEqual(main_effects, sm.main_effects)
        self.assertEqual(interaction_effects, sm.interaction_effects)
        self.assertEqual(random_effects, sm.random_effects)
        family = sm.family_function
        self.assertIn(family, family_link_paired.keys())
        link = sm.link_function
        self.assertIn(link, family_link_paired[family])

        code = generate_statsmodels_link(statistical_model=sm)
        reference_code = "Power(power=.5)"
        self.assertEqual(code, reference_code)

    def test_generate_statsmodels_model(self): 
        u0 = ts.Unit("Unit")
        m0 = u0.numeric("Measure_0")
        m1 = u0.numeric("Measure_1")
        dv = u0.numeric("Dependent_variable")

        m0.moderates(moderator=m1, on=dv)
        design = ts.Design(dv=dv, ivs=[m0, m1])
        gr = design.graph

        (main_effects, main_explanations) = infer_main_effects_with_explanations(gr=gr, query=design)
        (interaction_effects, interaction_explanations) = infer_interaction_effects_with_explanations(gr=gr, query=design, main_effects=main_effects)
        random_effects = set()
        family_link_paired = get_family_link_paired_candidates(design=design)

        output_filename = "main_interaction.json"
        output_path = os.path.join(data_dir, output_filename)
        sm = construct_statistical_model(output_path, query=design, main_effects_candidates=main_effects, interaction_effects_candidates=interaction_effects, random_effects_candidates=random_effects, family_link_paired_candidates=family_link_paired)
        self.assertIsNotNone(sm)
        self.assertEqual(design.dv, sm.dependent_variable)
        self.assertEqual(main_effects, sm.main_effects)
        self.assertEqual(interaction_effects, sm.interaction_effects)
        self.assertEqual(random_effects, sm.random_effects)
        family = sm.family_function
        self.assertIn(family, family_link_paired.keys())
        link = sm.link_function
        self.assertIn(link, family_link_paired[family])

        code = generate_statsmodels_model(statistical_model=sm)
        formula = "'Dependent_variable ~ Measure_0 + Measure_1 + Measure_0*Measure_1'"
        family_name = "Poisson"
        link_obj = "Power(power=.5)"
        reference_code = model_template.format(formula=formula, family_name=family_name, link_obj=link_obj)
        self.assertEqual(code, reference_code)