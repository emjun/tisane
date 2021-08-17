import tisane as ts
from tisane.main import collect_model_candidates
from tisane.family_link_inference import infer_family_functions, infer_link_functions

import unittest 

class CandidateJSONGenerationTest(unittest.TestCase): 
    def test_main_effects_only(self): 
        u0 = ts.Unit("Unit")
        m0 = u0.numeric("Measure 0")
        m1 = u0.numeric("Measure 1")
        dv = u0.numeric("Dependent variable")

        query = ts.Design(dv=dv, ivs=[m0, m1])

        main_effects = set()
        main_effects.add(m0)
        main_effects.add(m1)

        interaction_effects = set()
        random_effects = set()
        family_candidates = infer_family_functions(query=query)
        link_candidates = set()
        family_link_paired = dict()
        for f in family_candidates: 
            l = infer_link_functions(query=query, family=f)
            # Add Family: Link options 
            assert(f.__class__ not in family_link_paired.keys())
            family_link_paired[f.__class__] = l

        combined_dict = collect_model_candidates(query=query, main_effects_candidates=main_effects, interaction_effects_candidates=interaction_effects, random_effects_candidates=random_effects, family_link_paired_candidates=family_link_paired)
        self.assertEqual(len(combined_dict.keys()), 1) # "input"
        input = combined_dict["input"]
        input_keys = input.keys()
        self.assertIsInstance(input, dict)
        self.assertEqual(len(input_keys), 5)
        self.assertIn("query", input_keys)
        self.assertIn("generated main effects", input_keys)
        self.assertIn("generated interaction effects", input_keys)
        self.assertIn("generated random effects", input_keys)
        self.assertIn("generated family, link functions", input_keys)
        self.assertIsInstance(input["query"], dict)
        self.assertIsInstance(input["generated main effects"], list)
        self.assertIsInstance(input["generated interaction effects"], list)
        self.assertIsInstance(input["generated random effects"], dict)
        self.assertIsInstance(input["generated family, link functions"], dict)

    def test_main_interaction(self): 
        u0 = ts.Unit("Unit")
        m0 = u0.numeric("Measure 0")
        m1 = u0.numeric("Measure 1")
        dv = u0.numeric("Dependent variable")

        query = ts.Design(dv=dv, ivs=[m0, m1])

        main_effects = set()
        main_effects.add(m0)
        main_effects.add(m1)

        interaction_effects = set()
        random_effects = set()
        family_candidates = infer_family_functions(query=query)
        link_candidates = set()
        family_link_paired = dict()
        for f in family_candidates: 
            l = infer_link_functions(query=query, family=f)
            # Add Family: Link options 
            assert(f.__class__ not in family_link_paired.keys())
            family_link_paired[f.__class__] = l

        combined_dict = collect_model_candidates(query=query, main_effects_candidates=main_effects, interaction_effects_candidates=interaction_effects, random_effects_candidates=random_effects, family_link_paired_candidates=family_link_paired)
        self.assertEqual(len(combined_dict.keys()), 1) # "input"
        input = combined_dict["input"]
        input_keys = input.keys()
        self.assertIsInstance(input, dict)
        self.assertEqual(len(input_keys), 5)
        self.assertIn("query", input_keys)
        self.assertIn("generated main effects", input_keys)
        self.assertIn("generated interaction effects", input_keys)
        self.assertIn("generated random effects", input_keys)
        self.assertIn("generated family, link functions", input_keys)
        self.assertIsInstance(input["query"], dict)
        self.assertIsInstance(input["generated main effects"], list)
        self.assertIsInstance(input["generated interaction effects"], list)
        self.assertIsInstance(input["generated random effects"], dict)
        self.assertIsInstance(input["generated family, link functions"], dict)
