## TODO: Check that the Family - link pairs make sense (this might be covered earlier in the pipeline)

from tisane.multiverse_code_generator import construct_all_main_options, construct_all_interaction_options, construct_all_random_options, construct_all_family_link_options, generate_multiverse_decisions, generate_template_code

import os
import unittest
import json

test_input_repo_name = "input_json_files/"
test_output_decision_repo_name = "output_decision_json_files/"
test_output_template_repo_name = "output_template_files/"
dir = os.path.dirname(__file__)
input_dir = os.path.join(dir, test_input_repo_name)
output_decision_dir = os.path.join(dir, test_output_decision_repo_name)
output_template_dir = os.path.join(dir, test_output_template_repo_name)

class MultiverseCodeHelpers(unittest.TestCase): 
    
    def test_construct_all_formulae_main_only(self): 
        main_only_file = "main_only.json"

        input_filename = "main_only.json"
        input_path = os.path.join(input_dir, input_filename)
        
        # Read in JSON file as a dict
        with open(input_path, "r") as f:
            file_data = f.read()
        combined_dict = json.loads(file_data) 


    def test_construct_all_main_options_main_only(self):
        input_filename = "main_only.json"
        input_path = os.path.join(input_dir, input_filename)
        
        # Read in JSON file as a dict
        with open(input_path, "r") as f:
            file_data = f.read()
        combined_dict = json.loads(file_data) 

        main_options = list(construct_all_main_options(combined_dict=combined_dict))
        self.assertEqual(len(main_options), 2)
        for o in main_options: 
            self.assertLessEqual(len(o), 1)

            if len(o) == 1: 
                self.assertIn("Time", o)

    def test_construct_all_interaction_options_main_only(self):
        input_filename = "main_only.json"
        input_path = os.path.join(input_dir, input_filename)
        
        # Read in JSON file as a dict
        with open(input_path, "r") as f:
            file_data = f.read()
        combined_dict = json.loads(file_data) 

        interaction_options = list(construct_all_interaction_options(combined_dict=combined_dict))
        self.assertEqual(len(interaction_options), 1)
        for o in interaction_options: 
            self.assertLessEqual(len(o), 0)

    def test_construct_all_random_options_main_only(self):
        input_filename = "main_only.json"
        input_path = os.path.join(input_dir, input_filename)
        
        # Read in JSON file as a dict
        with open(input_path, "r") as f:
            file_data = f.read()
        combined_dict = json.loads(file_data) 

        random_options = list(construct_all_random_options(combined_dict=combined_dict))
        self.assertEqual(len(random_options), 1)
        for o in random_options: 
            self.assertLessEqual(len(o), 0)
    
    def test_construct_family_link_pairs(self):
        input_filename = "main_only.json"
        input_path = os.path.join(input_dir, input_filename)
        
        # Read in JSON file as a dict
        with open(input_path, "r") as f:
            file_data = f.read()
        combined_dict = json.loads(file_data) 

        family_link_options = list(construct_all_family_link_options(combined_dict=combined_dict))
        for o in family_link_options:
            self.assertEqual(len(o), 2)

            family = o[0]
            link = o[1]
            self.assertIn(family, DataForTests.possible_families)

    def test_generate_multiverse_decisions_main_only(self):
        input_filename = "main_only.json"
        input_path = os.path.join(input_dir, input_filename)
        
        # Read in JSON file as a dict
        with open(input_path, "r") as f:
            file_data = f.read()
        input_dict = json.loads(file_data) 

        output_filename = "decisions_main_only.json"
        output_path = generate_multiverse_decisions(combined_dict=input_dict, decisions_path=output_decision_dir, decisions_file=output_filename)

        # Read in JSON file as a dict
        with open(output_path, "r") as f:
            file_data = f.read()
        output_dict = json.loads(file_data) 
        decisions = output_dict["decisions"]

        # Do we need a more extensive test here?
        # for dec in decisions: 
        #     var = dec["var"]
        #     if var == "main_effects":
        #         options = dec["options"]
        #         input_dict["input"]["generated main effects"]
        #     elif var == "interaction_effects":
        #         pass
        #     elif var == "random_effects":
        #         pass
        #     elif var == "family, link pairs":
        #         pass
            
    # TODO: Add more tests for interaction_only, main_interaction, ....

    def test_generate_multiverse_template_main_only(self):
        decisions_filename = "decisions_main_only.json"
        decisions_path = os.path.join(output_decision_dir, decisions_filename)
        
        template_filename = "template_main_only.py"
        output_path = os.path.join(output_template_dir, template_filename)
        output_path = generate_template_code(template_path=output_path, decisions_path=decisions_path, data_path="data.csv", target="PYTHON", has_random_effects=False)

        # Open output template file
        # START HERE: Check template generation... 
        # First, run to see if tests fail?
        # IDEA: maybe have a reference and then compare that the generated and reference are identical/equal?



    def test_construct_all_formulae_interaction_only(self): 
        combined_dict = dict()
        pass

    def test_construct_all_formulae_main_interaction(self): 
        combined_dict = dict()
        pass

    def test_construct_all_formulae_main_random(self): 
        combined_dict = dict()
        pass
    
    def test_construct_all_formulae_main_interaction_random(self): 
        combined_dict = dict()
        pass

    def test_construct_all_family(self): 
        pass
    
    def test_construct_all_link(self): 
        pass

    def test_generate_multiverse_decisions(self): 
        pass 

class DataForTests:
    possible_families = ["Gaussian", "InverseGaussian", "Gamma", "Tweedie", "Poisson", "Binomial", "NegativeBinomial"]