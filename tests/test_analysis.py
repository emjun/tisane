import tisane as ts
from tisane.main import TASK, RELATIONSHIP
from tisane.concept_graph import CONCEPTUAL_RELATIONSHIP
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
        self.assertTrue(nx.is_empty(analysis.graph._graph))
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
        self.assertEqual(analysis.graph._graph.number_of_nodes(), 3)
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
        self.assertTrue(nx.is_empty(analysis.graph._graph))

        # Implicitly add concepts    
        analysis.relate(ivs=[intelligence, tutoring], dv=[test_score], relationship="linear")

        # ASSERT
        self.assertEqual(analysis.task,TASK.cast("prediction"))
        self.assertEqual(analysis.graph._graph.number_of_nodes(), 3)
        for con in concepts: 
            self.assertTrue(analysis.graph.hasConcept(con))
        self.assertEqual(analysis.relationship, RELATIONSHIP.cast("linear"))
        self.assertIsNone(analysis.data)

# START HERE: Debug nubmer of nodes added in relationships -- seems to be double, why!?
    def test_addRelationships_cause(self): 
        analysis = ts.Tisane(task="prediction") # analysis has one task

        test_score = ts.Concept("Test Score")
        intelligence = ts.Concept("Intelligence")
        tutoring = ts.Concept("Tutoring")
        concepts = [test_score, intelligence, tutoring]

        # ASSERT 
        self.assertTrue(nx.is_empty(analysis.graph._graph))

        analysis.addRelationship(intelligence, test_score, "cause")
        analysis.addRelationship(tutoring, test_score, "cause")

        # ASSERT
        self.assertEqual(analysis.task,TASK.cast("prediction"))
        self.assertEqual(analysis.graph._graph.number_of_nodes(), 3)
        for con in concepts: 
            self.assertTrue(analysis.graph.hasConcept(con))

        self.assertEqual(len(analysis.graph._graph.edges()), 2)
        self.assertTrue(analysis.graph._graph.has_edge(intelligence.name, test_score.name))
        edge_info = analysis.graph._graph.get_edge_data(intelligence.name, test_score.name)
        edge_type = edge_info[0]['edge_type']
        self.assertEqual(edge_type, CONCEPTUAL_RELATIONSHIP.CAUSE)
        
        self.assertTrue(analysis.graph._graph.has_edge(tutoring.name, test_score.name))
        edge_info = analysis.graph._graph.get_edge_data(tutoring.name, test_score.name)
        edge_type = edge_info[0]['edge_type']
        self.assertEqual(edge_type, CONCEPTUAL_RELATIONSHIP.CAUSE)
        
        self.assertIsNone(analysis.relationship)
        self.assertIsNone(analysis.data)

    def test_addRelationships_correlate(self): 
        analysis = ts.Tisane(task="prediction") # analysis has one task

        test_score = ts.Concept("Test Score")
        intelligence = ts.Concept("Intelligence")
        tutoring = ts.Concept("Tutoring")
        concepts = [test_score, intelligence, tutoring]

        # ASSERT 
        self.assertTrue(nx.is_empty(analysis.graph._graph))

        analysis.addRelationship(intelligence, test_score, "correlate")
        analysis.addRelationship(tutoring, test_score, "correlate")

        # ASSERT
        self.assertEqual(analysis.task,TASK.cast("prediction"))
        self.assertEqual(analysis.graph._graph.number_of_nodes(), 3)
        for con in concepts: 
            self.assertTrue(analysis.graph.hasConcept(con))

        self.assertEqual(len(analysis.graph._graph.edges()), 2)
        self.assertTrue(analysis.graph._graph.has_edge(intelligence.name, test_score.name))
        edge_info = analysis.graph._graph.get_edge_data(intelligence.name, test_score.name)
        edge_type = edge_info[0]['edge_type']
        self.assertEqual(edge_type, CONCEPTUAL_RELATIONSHIP.CORRELATION)
        
        self.assertTrue(analysis.graph._graph.has_edge(tutoring.name, test_score.name))
        edge_info = analysis.graph._graph.get_edge_data(tutoring.name, test_score.name)
        edge_type = edge_info[0]['edge_type']
        self.assertEqual(edge_type, CONCEPTUAL_RELATIONSHIP.CORRELATION)
        
        self.assertIsNone(analysis.relationship)
        self.assertIsNone(analysis.data)

    def test_addRelationships_mixed(self): 
        analysis = ts.Tisane(task="prediction") # analysis has one task

        test_score = ts.Concept("Test Score")
        intelligence = ts.Concept("Intelligence")
        tutoring = ts.Concept("Tutoring")
        concepts = [test_score, intelligence, tutoring]

        # ASSERT 
        self.assertTrue(nx.is_empty(analysis.graph._graph))

        analysis.addRelationship(intelligence, test_score, "cause")
        analysis.addRelationship(tutoring, test_score, "cause")
        analysis.addRelationship(intelligence, tutoring, "correlate")

        # ASSERT
        self.assertEqual(analysis.task,TASK.cast("prediction"))
        self.assertEqual(analysis.graph._graph.number_of_nodes(), 3)
        for con in concepts: 
            self.assertTrue(analysis.graph.hasConcept(con))
        
        self.assertEqual(len(analysis.graph._graph.edges()), 3)
        self.assertTrue(analysis.graph._graph.has_edge(intelligence.name, test_score.name))
        edge_info = analysis.graph._graph.get_edge_data(intelligence.name, test_score.name)
        edge_type = edge_info[0]['edge_type']
        self.assertEqual(edge_type, CONCEPTUAL_RELATIONSHIP.CAUSE)
        
        self.assertTrue(analysis.graph._graph.has_edge(tutoring.name, test_score.name))
        edge_info = analysis.graph._graph.get_edge_data(tutoring.name, test_score.name)
        edge_type = edge_info[0]['edge_type']
        self.assertEqual(edge_type, CONCEPTUAL_RELATIONSHIP.CAUSE)

        self.assertTrue(analysis.graph._graph.has_edge(intelligence.name, tutoring.name))
        edge_info = analysis.graph._graph.get_edge_data(intelligence.name, tutoring.name)
        edge_type = edge_info[0]['edge_type']
        self.assertEqual(edge_type, CONCEPTUAL_RELATIONSHIP.CORRELATION)
        
        self.assertIsNone(analysis.relationship)
        self.assertIsNone(analysis.data)

    # def test_explain_tc_simple(self): 
    #     analysis = ts.Tisane(task="explanation") # analysis has one task

    #     test_score = ts.Concept("Test Score")
    #     intelligence = ts.Concept("Intelligence")
    #     tutoring = ts.Concept("Tutoring")
    #     concepts = [test_score, intelligence, tutoring]

    #     analysis.addRelationship(intelligence, test_score, "cause")
    #     analysis.addRelationship(tutoring, test_score, "cause")
    #     analysis.addRelationship(intelligence, tutoring, "correlate")

    #     effects_sets = analysis.generate_effects_sets_with_ivs(ivs=[intelligence, tutoring], dv=test_score)
    #     self.assertEqual(len(effects_sets), 7)

    #     analysis.pretty_print_effects_sets(dv=test_score)


    #     # Main effects = 3

    #     # Interaction effects = 1

    def test_explain_tc_cut(self): 
        analysis = ts.Tisane(task="explanation") # analysis has one task

        test_score = ts.Concept("Test Score")
        intelligence = ts.Concept("Intelligence")
        tutoring = ts.Concept("Tutoring")
        income = ts.Concept("Income")
        concepts = [test_score, intelligence, tutoring, income]

        analysis.addRelationship(intelligence, test_score, "cause")
        analysis.addRelationship(tutoring, test_score, "cause")
        analysis.addRelationship(intelligence, tutoring, "correlate")
        analysis.addRelationship(test_score, income, "cause")
        analysis.addRelationship(intelligence, income, "correlate")
    
        # TODO: Check that test_score ->cause income is not in effects set/subgraph
        # TODO: Check that the edges we expect are in the subgraph?


        effects_sets = analysis.generate_effects_sets_with_ivs(ivs=[intelligence, tutoring], dv=test_score)
        import pdb; pdb.set_trace()
        self.assertEqual(len(effects_sets), 7)

        analysis.pretty_print_effects_sets(dv=test_score)

    def test_explain_tc_cut_filter_noop(self): 
        analysis = ts.Tisane(task="explanation") # analysis has one task

        test_score = ts.Concept("Test Score")
        intelligence = ts.Concept("Intelligence")
        tutoring = ts.Concept("Tutoring")
        income = ts.Concept("Income")
        sex = ts.Concept("Sex")
        concepts = [test_score, intelligence, tutoring, income, sex]

        analysis.addRelationship(intelligence, test_score, "cause")
        analysis.addRelationship(tutoring, test_score, "cause")
        analysis.addRelationship(intelligence, tutoring, "correlate")
        analysis.addRelationship(test_score, income, "cause")
        analysis.addRelationship(intelligence, income, "correlate")
        analysis.addRelationship(sex, income, "correlate") 

        # TODO should not see sex in sets of effects
        effects_sets = analysis.generate_effects_sets_with_ivs(ivs=[intelligence, tutoring], dv=test_score)

    def test_explain_tc_cut_filter(self):
        analysis = ts.Tisane(task="explanation") # analysis has one task

        test_score = ts.Concept("Test Score")
        intelligence = ts.Concept("Intelligence")
        tutoring = ts.Concept("Tutoring")
        income = ts.Concept("Income")
        sex = ts.Concept("Sex")
        concepts = [test_score, intelligence, tutoring, income, sex]

        analysis.addRelationship(intelligence, test_score, "cause")
        analysis.addRelationship(tutoring, test_score, "cause")
        analysis.addRelationship(intelligence, tutoring, "correlate")
        analysis.addRelationship(test_score, income, "cause")
        analysis.addRelationship(intelligence, income, "correlate")
        
        # HOWEVER, if add this: 
        analysis.addRelationship(sex, intelligence, "correlate")
        # TODO: should see sex in sets of effects
        effects_sets = analysis.generate_effects_sets_with_ivs(ivs=[intelligence, tutoring], dv=test_score)
        
        pass

    def test_explain(self): 
        analysis = ts.Tisane(task="prediction") # analysis has one task

        test_score = ts.Concept("Test Score")
        intelligence = ts.Concept("Intelligence")
        tutoring = ts.Concept("Tutoring")
        concepts = [test_score, intelligence, tutoring]

        analysis.addRelationship(intelligence, test_score, "cause")
        analysis.addRelationship(tutoring, test_score, "cause")
        analysis.addRelationship(intelligence, tutoring, "correlate")

        analysis.explain(test_score)
        
        self.assertEqual(analysis.graph._graph.number_of_nodes(), 3)

class DataForTests:
    concepts_to_define = [
        {"name": "NominalT", "data type": "nominal", "categories": ["Nominal0"], "data": ["Val1", "Val2", "Val3"]},
        {"name": "OrdinalT", "data type": "ordinal", "ordered_categories": ["Ordinal1", "Ordinal2", "Ordinal3"], "data": ["Ordinal2", "Ordinal1", "Ordinal3"]},
        {"name": "NumericT", "data type": "numeric", "data": [1, 2, 3]},
    ]        