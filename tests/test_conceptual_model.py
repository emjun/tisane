import tisane as ts
from tisane.variable import Treatment, Nest, RepeatedMeasure, Cause, Associate

import unittest

class ConceptualModelTest(unittest.TestCase): 
    def test_initialize_cause_only(self):
        acc = ts.Numeric('accuracy')
        expl = ts.Nominal('explanation type')
        variables = [acc, expl]

        cm = ts.ConceptualModel(
            causal_relationships = [expl.cause(acc)]
        )

        # The graph IR has all the variables
        for v in variables: 
            self.assertTrue(cm.graph.has_variable(v))
        
        # The graph IR has all the edges we expect
        self.assertTrue(cm.graph.has_edge(expl, acc))
        edge = cm.graph.get_edge(expl, acc, edge_type='cause')
        self.assertIsNotNone(edge)

    def test_initialize_associate_only(self):
        approval = ts.Nominal('approval') # 4 values
        form_comp = ts.Numeric('form completion') 
        doc = ts.Ordinal('persistent documentation') # 3 values
        comm = ts.Nominal('replicated by community') # binary
        variables = [approval, form_comp, doc, comm]

        cm = ts.ConceptualModel(
            associative_relationships = [form_comp.associate(approval), doc.associate(approval), comm.associate(approval)]
        )

        # The graph IR has all the variables
        for v in variables: 
            self.assertTrue(cm.graph.has_variable(v))
        
        # The graph IR has all the edges we expect
        self.assertTrue(cm.graph.has_edge(form_comp, approval))
        edge = cm.graph.get_edge(form_comp, approval, edge_type='associate')
        self.assertIsNotNone(edge)
        self.assertTrue(cm.graph.has_edge(doc, approval))
        edge = cm.graph.get_edge(doc, approval, edge_type='associate')
        self.assertIsNotNone(edge)
        self.assertTrue(cm.graph.has_edge(comm, approval))
        edge = cm.graph.get_edge(comm, approval, edge_type='associate')
        self.assertIsNotNone(edge)
    
    def test_initialize_cause_associate(self):
        pos_aff = ts.Numeric('Positive Affect')
        es = ts.Numeric('Emotional Suppression')
        cr = ts.Numeric('Cognitive Reappraisal')
        age = ts.Numeric('Age')
        time = ts.Numeric('Hours since 7am')
        variables = [pos_aff, es, cr, age, time]

        cm = ts.ConceptualModel(
            causal_relationships = [es.cause(pos_aff), cr.cause(pos_aff)],
            associative_relationships = [age.associate(pos_aff), time.associate(pos_aff)]
        )

        # The graph IR has all the variables
        for v in variables: 
            self.assertTrue(cm.graph.has_variable(v))
        
        # The graph IR has all the edges we expect
        self.assertTrue(cm.graph.has_edge(es, pos_aff))
        edge = cm.graph.get_edge(es, pos_aff, edge_type='cause')
        self.assertIsNotNone(edge)
        self.assertTrue(cm.graph.has_edge(cr, pos_aff))
        edge = cm.graph.get_edge(cr, pos_aff, edge_type='cause')
        self.assertIsNotNone(edge)
        self.assertTrue(cm.graph.has_edge(age, pos_aff))
        edge = cm.graph.get_edge(age, pos_aff, edge_type='associate')
        self.assertIsNotNone(edge)
        self.assertTrue(cm.graph.has_edge(time, pos_aff))
        edge = cm.graph.get_edge(time, pos_aff, edge_type='associate')
        self.assertIsNotNone(edge)
