import tisane as ts
from tisane.smt.knowledge_base import KnowledgeBase, find_statistical_models

import unittest

class KnowledgeBaseTests(unittest.TestCase): 
    
    def test_ctor(self): 
        # analysis = ts.Tisane(task="prediction") # analysis has one task

        test_score = ts.Concept("Test Score")
        intelligence = ts.Concept("Intelligence")
        tutoring = ts.Concept("Tutoring")

        test_score.specifyData(dtype="numeric") # Score 0 - 100 
        intelligence.specifyData(dtype="numeric") # IQ score 
        tutoring.specifyData(dtype="nominal", categories=["afterschool", "none"])

        ivs = [intelligence, tutoring]
        dvs = [test_score]
        
        kb = KnowledgeBase(ivs, dvs)

        # ASSERT
        self.assertEqual(len(kb.all_stat_models), 2)
        self.assertEqual(kb.all_stat_models[0].name, 'Linear Regression')
        self.assertEqual(len(kb.all_stat_models[0].properties), 2)
        self.assertEqual(kb.all_stat_models[0].properties[0], kb.all_properties['numeric_dv'])
        self.assertEqual(kb.all_stat_models[0].properties[1], kb.all_properties['normal_distribution_residuals'])
        # self.assertEqual(kb.all_stat_models[0].properties[1], kb.all_properties['residual_normal_distribution'])

    def test_pick_linear_regression(self): 
        test_score = ts.Concept("Test Score")
        intelligence = ts.Concept("Intelligence")
        tutoring = ts.Concept("Tutoring")

        test_score.specifyData(dtype="numeric") # Score 0 - 100 
        intelligence.specifyData(dtype="numeric") # IQ score 
        tutoring.specifyData(dtype="nominal", categories=["afterschool", "none"])

        ivs = [intelligence, tutoring]
        dvs = [test_score]
        
        valid_models = find_statistical_models(ivs=ivs, dvs=dvs)

        self.assertEqual(len(valid_models), 2)
        self.assertEqual(valid_models[0], 'Linear Regression')

# TODO connect to the main file, test model selection (esp for all possible model variations)

    def test_dtor(self): 
        # Test resetting or nulling out all the properties and tests! 

        pass
