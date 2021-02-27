from tisane import *
from tisane.variable import Treatment, Nest, RepeatedMeasure

import unittest

class DesignTest(unittest.TestCase): 
    def test_initialize(self): 
        acc = Numeric('accuracy')
        expl = Nominal('explanation type')
        participant = Nominal('id')
        variables = [acc, expl, participant]

        design = Design(
            dv = acc, 
            # TODO: What if list: expl(treat=participant) -- pose as option in IDL?
            ivs = [expl.treat(participant)], # expl which was treated on participant
            groupings = None # what is the unit that is assumed here? -- This needs to be formalized?
        )

        # The graph IR has all the variables
        for v in variables: 
            self.assertTrue(design.graph.has_variable(v))

        # The graph IR has all the edges we expect
        self.assertTrue(design.graph.has_edge(expl, acc))
        edge = design.graph.get_edge(expl, acc, edge_type='unknown')
        self.assertIsNotNone(edge)
        
        self.assertTrue(design.graph.has_edge(expl, participant))
        edge = design.graph.get_edge(expl, participant, edge_type='treat')
        self.assertIsNotNone(edge)
        edge_data = edge[2]
        edge_obj = edge_data['edge_obj']
        self.assertIsInstance(edge_obj, Treatment)
        self.assertIs(edge_obj.unit, participant)
        self.assertIs(edge_obj.treatment, expl)

        self.assertEqual(len(design.graph.get_edges()), 2)
        self.assertEqual(len(design.graph.get_nodes()), len(variables))

    def test_initialize_groupings(self): 
        expl = Nominal('explanation type')
        correct = Nominal('correct') # yes/no

        # Dependency/structure
        # If they did not want to calculate accuracy (1 per participant), would do something like...
        participant = Nominal('id')
        participant.repeat(correct, 50) # Could infer 50 with data
        variables = [expl, correct, participant]

        design = Design(
            dv = correct, 
            ivs = [expl.treat(participant, 1)], # treatment
            groupings = [participant.repeat(correct, 50)], # participant observations are closer to each other than between participants in a condition
        )

        # The graph IR has all the edges we expect
        self.assertTrue(design.graph.has_edge(expl, correct))
        edge = design.graph.get_edge(expl, correct, edge_type='unknown')
        self.assertIsNotNone(edge)
        # Treatment 
        self.assertTrue(design.graph.has_edge(expl, participant))
        edge = design.graph.get_edge(expl, participant, edge_type='treat')
        self.assertIsNotNone(edge)
        edge_data = edge[2]
        edge_obj = edge_data['edge_obj']
        self.assertIsInstance(edge_obj, Treatment)
        self.assertIs(edge_obj.unit, participant)
        self.assertIs(edge_obj.treatment, expl)
        # Nesting 
        design.graph.has_edge(participant, correct)
        edge = design.graph.get_edge(participant, correct, edge_type='repeat')
        self.assertIsNotNone(edge)
        edge_data = edge[2]
        edge_obj = edge_data['edge_obj']
        self.assertIsInstance(edge_obj, RepeatedMeasure)
        self.assertIs(edge_obj.unit, participant)
        self.assertIs(edge_obj.response, correct)
        self.assertEqual(edge_obj.number_of_measures, 50)

        self.assertEqual(len(design.graph.get_edges()), 3)
        self.assertEqual(len(design.graph.get_nodes()), len(variables))

    # def test_design_vis(self): 
    #     student_id = Numeric('student_id')
    #     sat_score = Numeric('sat_score')
    #     tutoring = Nominal('tutoring', cardinality=2) # Categorical('tutoring')
        
    #     design = Design(dv = sat_score)
    #     design.treat(student_id, tutoring, times=1)
        
    #     design.visualize_design() 