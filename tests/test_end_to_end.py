import tisane as ts
from tisane.effect_set import EffectSet, MainEffect, InteractionEffect, MixedEffect
from tisane.statistical_model import StatisticalModel

import unittest

class EndToEndTests(unittest.TestCase): 
    
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
    

    def test_effects_ASP(self):
        analysis = ts.Tisane(task="explanation")

        # Add concepts
        test_score = ts.Concept("Test Score")
        intelligence = ts.Concept("Intelligence")
        tutoring = ts.Concept("Tutoring")
        concepts = [test_score, intelligence, tutoring]

        # Add relationships
        analysis.addRelationship(intelligence, test_score, "cause")
        analysis.addRelationship(tutoring, test_score, "cause")
        analysis.addRelationship(intelligence, tutoring, "correlate")

        # Specify data (schema)
        test_score.specifyData(dtype="numeric")
        intelligence.specifyData(dtype="numeric")
        tutoring.specifyData(dtype="nominal", categories=["After school", "Before school"])
        # tutoring.specifyData(dtype="nominal", categories=["After school", "Before school", "None"])

        # Get valid statistical models
        # Assert statistical properties needed for linear regression
        # Generate effects sets
        effects = analysis.generate_effects_sets(ivs=[intelligence, tutoring], dv=test_score)

        # Add individual variable assertions
        # Some assertions are inferred from data schema, see above
        self.assertTrue(test_score.getVariable().has_property_value(prop="dtype", val="numeric"))
        self.assertTrue(intelligence.getVariable().has_property_value(prop="dtype", val="numeric"))
        self.assertTrue(tutoring.getVariable().has_property_value(prop="dtype", val="nominal"))
        
        self.assertFalse(test_score.getVariable().has_property(prop="cardinality"))
        self.assertFalse(intelligence.getVariable().has_property(prop="cardinality"))
        self.assertTrue(tutoring.getVariable().has_property_value(prop="cardinality", val="binary"))

        # Add assertions that pertain to effects sets
        linear_reg_es = None
        for es in effects: 
            if es.to_dict() == DataForTests.expected_effects_set[2]: 
                linear_reg_es = es
                break
        linear_reg_es.assert_property(prop="tolerate_correlation", val=True)
        
        # Convert linear regression model EffectSet to statistical model
        linear_reg_sm = StatisticalModel.create(model_type='linear_regression', effect_set=linear_reg_es)
        
        # Add assertions that pertain to the models
        # Note: Make assertions that will involve interaction (interactions compile to these statements)
        # Note: These assertions should be made on the *MODEL* not the *Effect Set*
        linear_reg_sm.get_residuals().assert_property(prop="distribution", val="normal")
        linear_reg_sm.get_residuals().assert_property(prop="homoscedastic", val=True)
        
        # TODO: Compile all these assertions into constraints
        # Should be in KnowledgeBase class or main Tisane class?
        
        # Query KB for statistical models


        
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