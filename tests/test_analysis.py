import tisane as ts
from tisane.main import TASK, RELATIONSHIP
# from tisane.variable import NominalVariable, OrdinalVariable, NumericVariable

import networkx as nx

import unittest


class AnalysisTests(unittest.TestCase): 
    # def setUp(self): 
    #     reload(ts.main)

    def test_ctor(self): 
        analysis = ts.Tisane(task="prediction") # analysis has one task

        # ASSERT
        self.assertEqual(analysis.task,TASK.cast("prediction"))
        self.assertTrue(nx.is_empty(analysis.graph.elts))
        self.assertIsNone(analysis.relationship)
        self.assertIsNone(analysis.data)
        

        
    def test_addConcepts_explicit(self): 
        analysis = ts.Tisane(task="prediction") # analysis has one task

        test_score = ts.Concept("Test Score")
        intelligence = ts.Concept("Intelligence")
        tutoring = ts.Concept("Tutoring")
        concepts = [test_score, intelligence, tutoring]

        # Explicitly add concepts
        analysis.addConcept(test_score)
        analysis.addConcept(intelligence)
        analysis.addConcept(tutoring)
    
        # ASSERT
        self.assertEqual(analysis.task,TASK.cast("prediction"))
        gr = analysis.graph
        for con in concepts: 
            self.assertTrue(gr.hasConcept(con))
        self.assertIsNone(analysis.relationship)
        self.assertIsNone(analysis.data)

    def test_addConcepts_implicit(self): 
        analysis = ts.Tisane(task="prediction") # analysis has one task

        test_score = ts.Concept("Test Score")
        intelligence = ts.Concept("Intelligence")
        tutoring = ts.Concept("Tutoring")
        concepts = [test_score, intelligence, tutoring]

        # ASSERT 
        self.assertTrue(nx.is_empty(analysis.graph.elts))

        # Implicitly add concepts    
        analysis.relate(ivs=[intelligence, tutoring], dv=[test_score], relationship="linear")

        # ASSERT
        self.assertEqual(analysis.task,TASK.cast("prediction"))
        for con in concepts: 
            self.assertTrue(analysis.graph.hasConcept(con))
        self.assertEqual(analysis.relationship, RELATIONSHIP.cast("linear"))
        self.assertIsNone(analysis.data)


class DataForTests:
    concepts_to_define = [
        {"name": "NominalT", "data type": "nominal", "categories": ["Nominal0"], "data": ["Val1", "Val2", "Val3"]},
        {"name": "OrdinalT", "data type": "ordinal", "ordered_categories": ["Ordinal1", "Ordinal2", "Ordinal3"], "data": ["Ordinal2", "Ordinal1", "Ordinal3"]},
        {"name": "NumericT", "data type": "numeric", "data": [1, 2, 3]},
    ]        