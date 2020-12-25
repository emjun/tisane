import tisane as ts
from tisane.asp.knowledge_base import KnowledgeBase

import unittest

class ConceptTests(unittest.TestCase): 

    def test_generate_constraints(self):
        kb = KnowledgeBase()

        test_score = ts.Concept("Test Score")
        tutoring = ts.Concept("Tutoring")
        intelligence = ts.Concept("Intelligence")

        kb.generate_constraints(name='test', ivs=[intelligence, tutoring], dv=[test_score])
        
        # with open('specific_constraints_test.lp') as f:
        #     pass