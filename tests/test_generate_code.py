"""
Tests that the constructed statistical model generates a Python script correctly. 
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
from tisane.main import construct_statistical_model, write_to_script
from tisane.code_generator import generate_code

import tisane as ts
import pandas as pd
from typing import Dict, Set
import os
import unittest


test_data_repo_name = "output_json_files/"
test_script_repo_name = "output_scripts/"
test_generated_script_repo_name = "generated_scripts/"
dir = os.path.dirname(__file__)
data_dir = os.path.join(dir, test_data_repo_name)
script_dir = os.path.join(dir, test_script_repo_name)
generated_script_dir = os.path.join(dir, test_generated_script_repo_name)
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


class GenerateCodeTest(unittest.TestCase):
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

        code = generate_code(statistical_model=sm, target="python")
        output_filename = "main_only.py"
        reference_script_path = os.path.join(script_dir, output_filename)
        # generated_path = os.path.join(generated_script_dir, output_filename)
        
        path = write_to_script(code, generated_script_dir, output_filename)
        # Check that the generated script is the same as the target script
        
        
    def test_generate_code_from_GUI_output_pigs_with_no_data(self):

        ## Initialize variables with data
        # Bind measures to units at the time of declaration
        week = ts.SetUp("Time", cardinality=12)
        pig = ts.Unit("Pig", cardinality=82)  # 82 pigs
        litter = ts.Unit("Litter", cardinality=22)  # 22 litters
        # Each pig has 1 instance of an ordinal Evit measure
        vitamin_e = pig.ordinal(
            "Evit", order=["Evit000", "Evit100", "Evit200"], number_of_instances=1
        )
        # Each pig has 1 instance of an ordinal Cu measure
        copper = pig.ordinal("Cu", order=["Cu000", "Cu035", "Cu175"], number_of_instances=1)
        # Each pig has for each value of week 1 instance of a numeric Weight measure
        # Also: Each pig has 1 instance of a Weight measure corresponding to each week
        weight = pig.numeric("Weight", number_of_instances=week)
        # Each pig has for each value of week 1 instance of a numeric Feed consumption measure
        feed = pig.numeric("Feed consumption", number_of_instances=week)

        ## Conceptual relationships
        week.causes(weight)

        ## Data measurement relationships
        # Pigs are nested within litters
        pig.nests_within(litter)

        ## Specify and execute query
        design = ts.Design(dv=weight, ivs=[week])
        gr = design.graph

        (main_effects_candidates, main_explanations) = infer_main_effects_with_explanations(
            gr=gr, query=design
        )
        (
            interaction_effects_candidates,
            interaction_explanations,
        ) = infer_interaction_effects_with_explanations(
            gr=gr, query=design, main_effects=main_effects_candidates
        )
        (
            random_effects_candidates,
            random_explanations,
        ) = infer_random_effects_with_explanations(
            gr=gr,
            query=design,
            main_effects=main_effects_candidates,
            interaction_effects=interaction_effects_candidates,
        )
        family_candidates = infer_family_functions(query=design)
        link_candidates = set()
        family_link_paired = dict()
        for f in family_candidates:
            l = infer_link_functions(query=design, family=f)
            # Add Family: Link options
            assert f not in family_link_paired.keys()
            family_link_paired[f] = l

        # Output from GUI 
        output_filename = "examples/Animal_Science/tisane_generated_files/model_spec.json"
        "examples/Animal_Science/tisane_generated_files/model_spec.json"
        
        sm = construct_statistical_model(
        filename=output_filename,
        query=design,
        main_effects_candidates=main_effects_candidates,
        interaction_effects_candidates=interaction_effects_candidates,
        random_effects_candidates=random_effects_candidates,
        family_link_paired_candidates=family_link_paired,
        )
        if design.has_data(): 
            # Assign statistical model data from @parm design
            sm.assign_data(design.dataset)
        # Generate code from SM
        code = generate_code(sm)
        # Write generated code out
        path = write_to_script(code, "examples/Animal_Science/", "model_no_data.py")


    def test_generate_code_from_GUI_output_pigs_with_data_frame(self):
        dir = os.path.dirname(__file__)
        df = pd.read_csv(os.path.join("examples/Animal_Science/", "pigs.csv"))

        ## Initialize variables with data
        # Bind measures to units at the time of declaration
        week = ts.SetUp("Time", cardinality=12)
        pig = ts.Unit("Pig", cardinality=82)  # 82 pigs
        litter = ts.Unit("Litter", cardinality=22)  # 22 litters
        # Each pig has 1 instance of an ordinal Evit measure
        vitamin_e = pig.ordinal(
            "Evit", order=["Evit000", "Evit100", "Evit200"], number_of_instances=1
        )
        # Each pig has 1 instance of an ordinal Cu measure
        copper = pig.ordinal("Cu", order=["Cu000", "Cu035", "Cu175"], number_of_instances=1)
        # Each pig has for each value of week 1 instance of a numeric Weight measure
        # Also: Each pig has 1 instance of a Weight measure corresponding to each week
        weight = pig.numeric("Weight", number_of_instances=week)
        # Each pig has for each value of week 1 instance of a numeric Feed consumption measure
        feed = pig.numeric("Feed consumption", number_of_instances=week)

        ## Conceptual relationships
        week.causes(weight)

        ## Data measurement relationships
        # Pigs are nested within litters
        pig.nests_within(litter)

        ## Specify and execute query
        design = ts.Design(dv=weight, ivs=[week]).assign_data(df)
        gr = design.graph

        (main_effects_candidates, main_explanations) = infer_main_effects_with_explanations(
            gr=gr, query=design
        )
        (
            interaction_effects_candidates,
            interaction_explanations,
        ) = infer_interaction_effects_with_explanations(
            gr=gr, query=design, main_effects=main_effects_candidates
        )
        (
            random_effects_candidates,
            random_explanations,
        ) = infer_random_effects_with_explanations(
            gr=gr,
            query=design,
            main_effects=main_effects_candidates,
            interaction_effects=interaction_effects_candidates,
        )
        family_candidates = infer_family_functions(query=design)
        link_candidates = set()
        family_link_paired = dict()
        for f in family_candidates:
            l = infer_link_functions(query=design, family=f)
            # Add Family: Link options
            assert f not in family_link_paired.keys()
            family_link_paired[f] = l

        # Output from GUI 
        output_filename = "examples/Animal_Science/tisane_generated_files/model_spec.json"
        
        sm = construct_statistical_model(
        filename=output_filename,
        query=design,
        main_effects_candidates=main_effects_candidates,
        interaction_effects_candidates=interaction_effects_candidates,
        random_effects_candidates=random_effects_candidates,
        family_link_paired_candidates=family_link_paired,
        )
        # Assign statistical model data from @parm design
        sm.assign_data(design.dataset)
        # Generate code from SM
        code = generate_code(sm)
        # Write generated code out
        path = write_to_script(code, "examples/Animal_Science/", "model_df.py")


    def test_generate_code_from_GUI_output_pigs_with_data_path(self):
        path = os.path.join("examples/Animal_Science/", "pigs.csv")

        ## Initialize variables with data
        # Bind measures to units at the time of declaration
        week = ts.SetUp("Time", cardinality=12)
        pig = ts.Unit("Pig", cardinality=82)  # 82 pigs
        litter = ts.Unit("Litter", cardinality=22)  # 22 litters
        # Each pig has 1 instance of an ordinal Evit measure
        vitamin_e = pig.ordinal(
            "Evit", order=["Evit000", "Evit100", "Evit200"], number_of_instances=1
        )
        # Each pig has 1 instance of an ordinal Cu measure
        copper = pig.ordinal("Cu", order=["Cu000", "Cu035", "Cu175"], number_of_instances=1)
        # Each pig has for each value of week 1 instance of a numeric Weight measure
        # Also: Each pig has 1 instance of a Weight measure corresponding to each week
        weight = pig.numeric("Weight", number_of_instances=week)
        # Each pig has for each value of week 1 instance of a numeric Feed consumption measure
        feed = pig.numeric("Feed consumption", number_of_instances=week)

        ## Conceptual relationships
        week.causes(weight)

        ## Data measurement relationships
        # Pigs are nested within litters
        pig.nests_within(litter)

        ## Specify and execute query
        design = ts.Design(dv=weight, ivs=[week]).assign_data(path)
        gr = design.graph

        (main_effects_candidates, main_explanations) = infer_main_effects_with_explanations(
            gr=gr, query=design
        )
        (
            interaction_effects_candidates,
            interaction_explanations,
        ) = infer_interaction_effects_with_explanations(
            gr=gr, query=design, main_effects=main_effects_candidates
        )
        (
            random_effects_candidates,
            random_explanations,
        ) = infer_random_effects_with_explanations(
            gr=gr,
            query=design,
            main_effects=main_effects_candidates,
            interaction_effects=interaction_effects_candidates,
        )
        family_candidates = infer_family_functions(query=design)
        link_candidates = set()
        family_link_paired = dict()
        for f in family_candidates:
            l = infer_link_functions(query=design, family=f)
            # Add Family: Link options
            assert f not in family_link_paired.keys()
            family_link_paired[f] = l

        # Output from GUI 
        output_filename = "examples/Animal_Science/tisane_generated_files/model_spec.json"
        
        sm = construct_statistical_model(
        filename=output_filename,
        query=design,
        main_effects_candidates=main_effects_candidates,
        interaction_effects_candidates=interaction_effects_candidates,
        random_effects_candidates=random_effects_candidates,
        family_link_paired_candidates=family_link_paired,
        )
        # Assign statistical model data from @parm design
        sm.assign_data(design.dataset)
        # Generate code from SM
        code = generate_code(sm)
        # Write generated code out
        path = write_to_script(code, "examples/Animal_Science/", "model_data_path.py")
        

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

    def test_construct_main_random_slope(self):
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
        for re in sm.random_effects:
            if isinstance(re, CorrelatedRandomSlopeAndIntercept):
                rs = re.random_slope
                ri = re.random_intercept
                self.assertIn(rs, random_effects)
                self.assertIn(ri, random_effects)
            elif isinstance(re, UncorrelatedRandomSlopeAndIntercept):
                rs = re.random_slope
                ri = re.random_intercept
                self.assertIn(rs, random_effects)
                self.assertIn(ri, random_effects)
            elif isinstance(re, RandomSlope):
                self.assertIn(re, random_effects)
            elif isinstance(re, RandomIntercept):
                self.assertIn(re, random_effects)
        family = sm.family_function
        self.assertIn(family, family_link_paired.keys())
        link = sm.link_function
        self.assertIn(link, family_link_paired[family])
