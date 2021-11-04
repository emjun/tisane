from tisane.multiverse_code_generator import construct_all_main_options

import os
import unittest
import json

test_input_repo_name = "input_json_files/"
dir = os.path.dirname(__file__)
dir = os.path.join(dir, test_input_repo_name)

class MultiverseCodeHelpers(unittest.TestCase): 
    
    def test_construct_all_formulae_main_only(self): 
        main_only_file = "main_only.json"

        input_filename = "main_only.json"
        input_path = os.path.join(dir, input_filename)
        
        # Read in JSON file as a dict
        with open(input_path, "r") as f:
            file_data = f.read()
        combined_dict = json.loads(file_data) 


    def test_construct_all_main_options(self):
        main_only_file = "main_only.json"

        input_filename = "main_only.json"
        input_path = os.path.join(dir, input_filename)
        
        # Read in JSON file as a dict
        with open(input_path, "r") as f:
            file_data = f.read()
        combined_dict = json.loads(file_data) 

        main_options = list(construct_all_main_options(combined_dict=combined_dict))
        self.assertEqual(len(main_options), 2)
        for mo in main_options: 
            self.assertLessEqual(len(mo), 1)

            if len(mo) == 1: 
                self.assertIn("Time", mo)

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
