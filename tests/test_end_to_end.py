import tisane as ts
from tisane.effect_set import EffectSet, MainEffect, InteractionEffect, MixedEffect
from tisane.statistical_model import StatisticalModel, LinearRegression

import unittest

class EndToEndTests(unittest.TestCase): 

    def test_sample_tisane_program(self): 
        analysis = ts.Tisane(task="explanation")

        ### PHASE 0: CONCEPTUAL RELATIONSHIPS
        # Add concepts
        test_score = ts.Concept("Test Score")
        intelligence = ts.Concept("Intelligence")
        tutoring = ts.Concept("Tutoring")
    
        # Add relationships
        analysis.addRelationship(intelligence, test_score, "cause")
        analysis.addRelationship(tutoring, test_score, "cause")
        analysis.addRelationship(intelligence, tutoring, "correlate")
        
        ### PHASE 1: IV, DV SPECIFICATION
        ### PHASE 2: EFFECTS SETS GENERATION 
        # Generate effects sets
        effects = analysis.generate_effects_sets(ivs=[intelligence, tutoring], dv=test_score)

        ### PHASE 3A: ASSERTIONS ABOUT VARIABLES AND SETS OF VARIABLES
        # Specify data (schema) --> generates assertions about variables/data
        # If have data: automatically detect and verify these based on uploaded data
        test_score.specifyData(dtype="numeric")
        intelligence.specifyData(dtype="numeric")
        tutoring.specifyData(dtype="nominal", categories=["After school", "Before school"])

        # THIS MIMICS END-USERS SELECTING A SET OF EFFECTS TO MODEL 
        linear_reg_es = None
        for es in effects: 
            if es.to_dict() == DataForTests.expected_effects_set[2]: 
                linear_reg_es = es
                break
        # Add assertions that pertain to effects sets
        linear_reg_es.assert_property(prop="tolerate_correlation", val=True)
        linear_reg_es.assert_property(prop="normal_residuals", val=True)
        linear_reg_es.assert_property(prop="homoscedastic_residuals", val=True)

        # PHASE 3B: QUERYING KNOWLEDGE BASE
        # TODO: TEST INCREMENTAL SOLVING ASPECT
        valid_models = analysis.start_model(effect_set=linear_reg_es) 
        print(valid_models) # "Linear Regression"
        self.assertTrue(len(valid_models), 1)
        model = valid_models[0]
        self.assertTrue(isinstance(model, LinearRegression))

    def test_generate_effects_sets(self):
        analysis = ts.Tisane(task="explanation") # analysis has one task

        test_score = ts.Concept("Test Score")
        intelligence = ts.Concept("Intelligence")
        tutoring = ts.Concept("Tutoring")
        concepts = [test_score, intelligence, tutoring]

        analysis.addRelationship(intelligence, test_score, "cause")
        analysis.addRelationship(tutoring, test_score, "cause")
        analysis.addRelationship(intelligence, tutoring, "correlate")

        effects = analysis.generate_effects_sets(ivs=[intelligence, tutoring], dv=test_score)
        
        # check total number of effect sets 
        self.assertEqual(len(effects), 7)
        # check each effect set is valid
        for es in effects: 
            es_dict = es.to_dict()
            self.assertTrue(es_dict in DataForTests.expected_effects_set)    

        
class DataForTests: 
    test_score = ts.Concept("Test Score")
    intelligence = ts.Concept("Intelligence")
    tutoring = ts.Concept("Tutoring")

    expected_effects_set = [
        {'dv': test_score.name, 'main': set({intelligence.name}), 'interaction': None, 'mixed': None},
        {'dv': test_score.name, 'main': set({tutoring.name}), 'interaction': None, 'mixed': None},
        {'dv': test_score.name, 'main': set({tutoring.name, intelligence.name}), 'interaction': None, 'mixed': None},
        {'dv': test_score.name, 'main': set({tutoring.name, intelligence.name}), 'interaction': set({(intelligence.name, tutoring.name)}), 'mixed': None},
        {'dv': test_score.name, 'main': set({intelligence.name}), 'interaction': set({(intelligence.name, tutoring.name)}), 'mixed': None},
        {'dv': test_score.name, 'main': set({tutoring.name}), 'interaction': set({(intelligence.name, tutoring.name)}), 'mixed': None},
        {'dv': test_score.name, 'main': None, 'interaction': set({(intelligence.name, tutoring.name)}), 'mixed': None},
    ]