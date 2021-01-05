import tisane as ts
from tisane.effect_set import EffectSet, MainEffect, InteractionEffect, MixedEffect
# from tisane.smt.knowledge_base import KnowledgeBase, find_statistical_models

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
        # Generate effects sets
        effects = analysis.generate_effects_sets(ivs=[intelligence, tutoring], dv=test_score)


        # Add assertions
        test_score.assert_property(prop="")
        intelligence.assert_property(prop="")
        tutoring.assert_property(prop="")

        # Effects Sets as a class that have residual properties?

        # Could we set up one end-to-end with all assertions and then figure out from there?

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