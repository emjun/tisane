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
            # TODO: This seems weird...?
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
        

    # def test_design_vis(self): 
    #     student_id = Numeric('student_id')
    #     sat_score = Numeric('sat_score')
    #     tutoring = Nominal('tutoring', cardinality=2) # Categorical('tutoring')
        
    #     design = Design(dv = sat_score)
    #     design.treat(student_id, tutoring, times=1)
        
    #     design.visualize_design() 