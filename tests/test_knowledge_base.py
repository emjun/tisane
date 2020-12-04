import tisane as ts
from tisane.smt.knowledge_base import KnowledgeBase

import unittest

class KnowledgeBaseTests(unittest.TestCase): 
    
    def test_ctor(self): 
        # analysis = ts.Tisane(task="prediction") # analysis has one task

        test_score = ts.Concept("Test Score")
        intelligence = ts.Concept("Intelligence")
        tutoring = ts.Concept("Tutoring")

        # CHECK THAT THE VARIABLES FOR EACH CONCEPT HAVE DTYPES, etc. 

        ivs = [intelligence, tutoring]
        dvs = [test_score]
        
        kb = KnowledgeBase(ivs, dvs)

        # ASSERT
        self.assertEqual(len(kb.all_stat_models), 1)
        self.assertEqual(kb.all_stat_models[0].name, 'Multiple Linear Regression')
        self.assertEqual(len(kb.all_stat_models[0].properties), 1)
        self.assertEqual(kb.all_stat_models[0].properties[0], kb.all_properties['numeric_dv'])


    def test_dtor(self): 
        # Test resetting or nulling out all the properties and tests! 

        pass
