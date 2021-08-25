"""
Tests methods called to generate code from a statistical model
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
model = smf.glm(formula={formula}, data=df, family=sm.families.{family_name}({link_obj}))
print(model.fit())
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
        sm = construct_statistical_model(
            output_path,
            query=design,
            main_effects_candidates=main_effects,
            interaction_effects_candidates=interaction_effects,
            random_effects_candidates=random_effects,
            family_link_paired_candidates=family_link_paired,
        )
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

        m0.causes(dv)
        m1.causes(dv)
        m0.moderates(moderator=m1, on=dv)

        design = ts.Design(dv=dv, ivs=[m0, m1])
        gr = design.graph

        assert(check_design_ivs(design=design))
        assert(check_design_dv(design=design))

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
        output_path = os.path.join(data_dir, output_filename)
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

        code = generate_statsmodels_formula(statistical_model=sm)
        reference_code = (
            "'Dependent_variable ~ Measure_0 + Measure_1 + Measure_0*Measure_1'"
        )
        self.assertEqual(code, reference_code)

    def test_generate_statsmodels_formula_main_multiple_random_intercepts(self):
        # Point to data in examples folder
        dir = os.path.dirname(__file__)
        dir_name = os.path.dirname(dir)
        dir_path = Path(dir_name)
        data_path = Path("examples/Animal_Science/pigs.csv")
        path = os.path.join(dir_path, data_path)
        df = pd.read_csv(path)

        week = ts.SetUp("Time", cardinality=12)
        pig = ts.Unit("Pig", cardinality=82)  # 82 pigs
        litter = ts.Unit("Litter", cardinality=22)  # 22 litters
        weight = pig.numeric("Weight", number_of_instances=week)

        ## Conceptual relationships
        week.causes(weight)

        ## Data measurement relationships
        pig.nests_within(litter)

        ## Specify and execute query
        design = ts.Design(dv=weight, ivs=[week]).assign_data(df)
        gr = design.graph

        assert(check_design_ivs(design=design))
        assert(check_design_dv(design=design))

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
        family_link_paired = get_family_link_paired_candidates(design=design)

        output_filename = "main_multiple_random_intercepts.json"
        output_path = os.path.join(data_dir, output_filename)
        sm = construct_statistical_model(
            output_path,
            query=design,
            main_effects_candidates=main_effects,
            interaction_effects_candidates=interaction_effects,
            random_effects_candidates=random_effects,
            family_link_paired_candidates=family_link_paired,
        )

        code = generate_pymer4_formula(statistical_model=sm)
        code = code.replace("'", "")  # get rid of single quotes
        code = code.replace("~", " ")
        code = code.replace("+", " ")
        code_elements = code.split()  # split string up at " "
        self.assertEqual(len(code_elements), 5)
        code_dv = code_elements[0]
        self.assertEqual(code_dv, design.dv.name)
        self.assertIn(design.dv.name, code_elements)
        self.assertIn("Time", code_elements)
        self.assertIn("(1|Time)", code_elements)
        self.assertIn("(1|Pig)", code_elements)
        self.assertIn("(1|Litter)", code_elements)

    def test_generate_statsmodels_formula_main_interaction_random_slope(self):
        subject = ts.Unit("Unit")
        time = ts.SetUp("Time")
        condition = subject.nominal(
            "Condition", cardinality=2, number_of_instances=1
        )  # "two independent groups of subjects"
        dv = subject.numeric(
            "Dependent_variable", number_of_instances=time
        )  # within-subject

        time.associates_with(dv)
        condition.causes(dv)
        time.moderates(moderator=[condition], on=dv)

        design = ts.Design(dv=dv, ivs=[time, condition])
        gr = design.graph

        assert(check_design_ivs(design=design))
        assert(check_design_dv(design=design))

        main_effects = set(design.ivs)
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
        family_link_paired = get_family_link_paired_candidates(design=design)

        output_filename = "main_interaction_random_slope.json"
        output_path = os.path.join(data_dir, output_filename)
        sm = construct_statistical_model(
            output_path,
            query=design,
            main_effects_candidates=main_effects,
            interaction_effects_candidates=interaction_effects,
            random_effects_candidates=random_effects,
            family_link_paired_candidates=family_link_paired,
        )
        self.assertEqual(sm.random_effects, random_effects)

        code = generate_pymer4_formula(statistical_model=sm)
        reference_code = (
            "'Dependent_variable ~ Condition + Time + Time*Condition + (0+Time|Unit)'"
        )
        self.assertEqual(code, reference_code)

    def test_generate_statsmodels_formula_main_correlated_random_slope_intercept(self):
        subject = ts.Unit("Subject", cardinality=12)
        word = ts.Unit("Word", cardinality=4)
        condition = subject.nominal("Word_type", cardinality=2, number_of_instances=2)
        reaction_time = subject.numeric("Time", number_of_instances=word)
        condition.has(word, number_of_instances=2)

        condition.causes(reaction_time)

        design = ts.Design(dv=reaction_time, ivs=[condition])
        gr = design.graph

        assert(check_design_ivs(design=design))
        assert(check_design_dv(design=design))

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
        output_path = os.path.join(data_dir, output_filename)
        sm = construct_statistical_model(
            output_path,
            query=design,
            main_effects_candidates=main_effects,
            interaction_effects_candidates=interaction_effects,
            random_effects_candidates=random_effects,
            family_link_paired_candidates=family_link_paired,
        )

        code = generate_pymer4_formula(statistical_model=sm)
        code = code.replace("'", "")  # get rid of single quotes
        code_elements = code.split("~")
        code_dv = code_elements[0].strip()
        code_ivs = code_elements[1]
        code_elements = code_ivs.split()  # split string up at " "
        code_ivs = [v for v in code_elements if v != "+"]  # filter for only IVs
        self.assertEqual(len(code_ivs), 3)  # + DV = 4 variables in the equation total
        self.assertEqual(code_dv, design.dv.name)
        self.assertIn(condition.name, code_ivs)
        self.assertIn("(1+Word_type|Subject)", code_ivs)
        self.assertIn("(1|Word)", code_ivs)

    def test_generate_statsmodels_formula_main_uncorrelated_random_slope_intercept(
        self,
    ):
        subject = ts.Unit("Subject", cardinality=12)
        word = ts.Unit("Word", cardinality=4)
        condition = subject.nominal("Word_type", cardinality=2, number_of_instances=2)
        reaction_time = subject.numeric("Time", number_of_instances=word)
        condition.has(word, number_of_instances=2)

        condition.causes(reaction_time)

        design = ts.Design(dv=reaction_time, ivs=[condition])
        gr = design.graph

        assert(check_design_ivs(design=design))
        assert(check_design_dv(design=design))

        main_effects = set(design.ivs)
        interaction_effects = set()
        (random_effects, random_explanations) = infer_random_effects_with_explanations(
            gr=gr,
            query=design,
            main_effects=main_effects,
            interaction_effects=interaction_effects,
        )
        family_link_paired = get_family_link_paired_candidates(design=design)

        output_filename = "main_random_slope_random_intercept_uncorrelated.json"
        output_path = os.path.join(data_dir, output_filename)
        sm = construct_statistical_model(
            output_path,
            query=design,
            main_effects_candidates=main_effects,
            interaction_effects_candidates=interaction_effects,
            random_effects_candidates=random_effects,
            family_link_paired_candidates=family_link_paired,
        )

        code = generate_pymer4_formula(statistical_model=sm)
        code = code.replace("'", "")  # get rid of single quotes
        code_elements = code.split("~")
        code_dv = code_elements[0].strip()
        code_ivs = code_elements[1]
        code_elements = code_ivs.split()  # split string up at " "
        code_ivs = [v for v in code_elements if v != "+"]  # filter for only IVs
        self.assertEqual(len(code_ivs), 4)  # + DV = 4 variables in the equation total
        self.assertEqual(code_dv, design.dv.name)
        self.assertIn(condition.name, code_ivs)
        self.assertIn("(1|Subject)", code_ivs)
        self.assertIn("(0+Word_type|Subject)", code_ivs)
        self.assertIn("(1|Word)", code_ivs)

    def test_generate_statsmodels_family_Gaussian(self):
        u0 = ts.Unit("Unit")
        m0 = u0.numeric("Measure_0")
        m1 = u0.numeric("Measure_1")
        dv = u0.numeric("Dependent_variable")

        m0.causes(dv)
        m1.associates_with(dv)

        design = ts.Design(dv=dv, ivs=[m0, m1])

        assert(check_design_ivs(design=design))
        assert(check_design_dv(design=design))

        main_effects = set(design.ivs)
        interaction_effects = set()
        random_effects = set()
        family_link_paired = get_family_link_paired_candidates(design=design)

        output_filename = "main_only.json"
        output_path = os.path.join(data_dir, output_filename)
        sm = construct_statistical_model(
            output_path,
            query=design,
            main_effects_candidates=main_effects,
            interaction_effects_candidates=interaction_effects,
            random_effects_candidates=random_effects,
            family_link_paired_candidates=family_link_paired,
        )
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

        m0.associates_with(dv)
        m1.associates_with(dv)

        m0.moderates(moderator=m1, on=dv)
        design = ts.Design(dv=dv, ivs=[m0, m1])
        gr = design.graph

        assert(check_design_ivs(design=design))
        assert(check_design_dv(design=design))

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
        output_path = os.path.join(data_dir, output_filename)
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

        code = generate_statsmodels_family(statistical_model=sm)
        reference_code = "Poisson"
        self.assertEqual(code, reference_code)

    def test_generate_statsmodels_link_Identity(self):
        u0 = ts.Unit("Unit")
        m0 = u0.numeric("Measure_0")
        m1 = u0.numeric("Measure_1")
        dv = u0.numeric("Dependent_variable")

        m0.associates_with(dv)
        m1.associates_with(dv)

        design = ts.Design(dv=dv, ivs=[m0, m1])

        assert(check_design_ivs(design=design))
        assert(check_design_dv(design=design))

        main_effects = set(design.ivs)
        interaction_effects = set()
        random_effects = set()
        family_link_paired = get_family_link_paired_candidates(design=design)

        output_filename = "main_only.json"
        output_path = os.path.join(data_dir, output_filename)
        sm = construct_statistical_model(
            output_path,
            query=design,
            main_effects_candidates=main_effects,
            interaction_effects_candidates=interaction_effects,
            random_effects_candidates=random_effects,
            family_link_paired_candidates=family_link_paired,
        )
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

        m0.associates_with(dv)
        m1.associates_with(dv)
        m0.moderates(moderator=m1, on=dv)

        design = ts.Design(dv=dv, ivs=[m0, m1])
        gr = design.graph

        assert(check_design_ivs(design=design))
        assert(check_design_dv(design=design))

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
        output_path = os.path.join(data_dir, output_filename)
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

        code = generate_statsmodels_link(statistical_model=sm)
        reference_code = "Power(power=.5)"
        self.assertEqual(code, reference_code)

    # def test_generate_statsmodels_model(self):
    #     u0 = ts.Unit("Unit")
    #     m0 = u0.numeric("Measure_0")
    #     m1 = u0.numeric("Measure_1")
    #     dv = u0.numeric("Dependent_variable")

    #     m0.moderates(moderator=m1, on=dv)
    #     design = ts.Design(dv=dv, ivs=[m0, m1])
    #     gr = design.graph

    #     (main_effects, main_explanations) = infer_main_effects_with_explanations(
    #         gr=gr, query=design
    #     )
    #     (
    #         interaction_effects,
    #         interaction_explanations,
    #     ) = infer_interaction_effects_with_explanations(
    #         gr=gr, query=design, main_effects=main_effects
    #     )
    #     random_effects = set()
    #     family_link_paired = get_family_link_paired_candidates(design=design)

    #     output_filename = "main_interaction.json"
    #     output_path = os.path.join(data_dir, output_filename)
    #     sm = construct_statistical_model(
    #         output_path,
    #         query=design,
    #         main_effects_candidates=main_effects,
    #         interaction_effects_candidates=interaction_effects,
    #         random_effects_candidates=random_effects,
    #         family_link_paired_candidates=family_link_paired,
    #     )
    #     self.assertIsNotNone(sm)
    #     self.assertEqual(design.dv, sm.dependent_variable)
    #     self.assertEqual(main_effects, sm.main_effects)
    #     self.assertEqual(interaction_effects, sm.interaction_effects)
    #     self.assertEqual(random_effects, sm.random_effects)
    #     family = sm.family_function
    #     self.assertIn(family, family_link_paired.keys())
    #     link = sm.link_function
    #     self.assertIn(link, family_link_paired[family])

    #     code = generate_statsmodels_model(statistical_model=sm)
    #     formula = "'Dependent_variable ~ Measure_0 + Measure_1 + Measure_0*Measure_1'"
    #     family_name = "Poisson"
    #     link_obj = "Power(power=.5)"
    #     reference_code = model_template.format(
    #         formula=formula, family_name=family_name, link_obj=link_obj
    #     )
    #     self.assertEqual(code, reference_code)

    # def test_generate_statsmodels_code(self): 
    #     pass

    # def test_generate_pymer4_code(self): 
    #     pass