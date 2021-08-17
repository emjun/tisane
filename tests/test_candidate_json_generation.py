import tisane as ts
from tisane.main import collect_model_candidates
from tisane.graph_inference import infer_interaction_effects, infer_random_effects
from tisane.family_link_inference import infer_family_functions, infer_link_functions

import unittest 

class CandidateJSONGenerationTest(unittest.TestCase): 
    def test_main_effects_only(self): 
        u0 = ts.Unit("Unit")
        m0 = u0.numeric("Measure 0")
        m1 = u0.numeric("Measure 1")
        dv = u0.numeric("Dependent variable")

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
            assert(f not in family_link_paired.keys())
            family_link_paired[f] = l

        combined_dict = collect_model_candidates(query=design, main_effects_candidates=main_effects, interaction_effects_candidates=interaction_effects, random_effects_candidates=random_effects, family_link_paired_candidates=family_link_paired)
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
        m2 = u0.numeric("Measure 2")
        dv = u0.numeric("Dependent variable")

        m0.causes(dv)
        m1.causes(dv)
        m2.moderates(moderator=m1, on=dv)
        
        design = ts.Design(dv=dv, ivs=[m0, m1, m2])
        gr = design.graph

        main_effects = set()
        main_effects.add(m0)
        main_effects.add(m1)
        main_effects.add(m2)

        interaction_effects = infer_interaction_effects(gr, design, main_effects)
        random_effects = set()
        family_candidates = infer_family_functions(query=design)
        link_candidates = set()
        family_link_paired = dict()
        for f in family_candidates: 
            l = infer_link_functions(query=design, family=f)
            # Add Family: Link options 
            assert(f not in family_link_paired.keys())
            family_link_paired[f] = l

        combined_dict = collect_model_candidates(query=design, main_effects_candidates=main_effects, interaction_effects_candidates=interaction_effects, random_effects_candidates=random_effects, family_link_paired_candidates=family_link_paired)
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
        self.assertEqual(len(input["generated interaction effects"]), 1)
        self.assertIsInstance(input["generated random effects"], dict)
        self.assertIsInstance(input["generated family, link functions"], dict)

    def test_main_interaction_random_intercept(self): 
        u0 = ts.Unit("Unit")
        s0 = ts.SetUp("Time", order=[1, 2, 3, 4, 5])
        m0 = u0.numeric("Measure 0")
        m1 = u0.numeric("Measure 1")
        m2 = u0.numeric("Measure 2")
        dv = u0.numeric("Dependent variable", number_of_instances=s0)
        
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

        interaction_effects = infer_interaction_effects(gr, design, main_effects)
        random_effects = infer_random_effects(
            gr=gr, query=design, main_effects=main_effects
        )
        family_candidates = infer_family_functions(query=design)
        link_candidates = set()
        family_link_paired = dict()
        for f in family_candidates: 
            l = infer_link_functions(query=design, family=f)
            # Add Family: Link options 
            assert(f not in family_link_paired.keys())
            family_link_paired[f] = l

        combined_dict = collect_model_candidates(query=design, main_effects_candidates=main_effects, interaction_effects_candidates=interaction_effects, random_effects_candidates=random_effects, family_link_paired_candidates=family_link_paired)
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
        self.assertEqual(len(input["generated interaction effects"]), 1)
        self.assertIsInstance(input["generated random effects"], dict)
        self.assertEqual(len(input["generated random effects"]), 2)
        self.assertIsInstance(input["generated family, link functions"], dict)
        
    def test_main_interaction_random_slope(self): 
        pass

    def test_main_interaction_random_intercept_slope_correlated(self): 
        pass

    