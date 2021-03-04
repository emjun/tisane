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
        self.assertTrue(cm.graph.has_edge(expl, acc, edge_type='cause'))

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
        self.assertTrue(cm.graph.has_edge(form_comp, approval, edge_type='associate'))
        self.assertTrue(cm.graph.has_edge(doc, approval, edge_type='associate'))
        self.assertTrue(cm.graph.has_edge(comm, approval, edge_type='associate'))
    
    def test_initialize_cause_associate(self):
        pos_aff = ts.Numeric('Positive Affect')
        es = ts.Numeric('Emotional Suppression')
        cr = ts.Numeric('Cognitive Reappraisal')
        gender = ts.Numeric('Gender')
        age = ts.Numeric('Age')
        time = ts.Numeric('Hours since 7am')
        variables = [pos_aff, es, cr, age, time]

        cm = ts.ConceptualModel(
            causal_relationships = [es.cause(pos_aff), cr.cause(pos_aff)],
            associative_relationships = [age.associate(pos_aff), gender.associate(pos_aff), time.associate(pos_aff)]
        )

        # The graph IR has all the variables
        for v in variables: 
            self.assertTrue(cm.graph.has_variable(v))
        
        # The graph IR has all the edges we expect
        self.assertTrue(cm.graph.has_edge(es, pos_aff, edge_type='cause'))
        self.assertTrue(cm.graph.has_edge(cr, pos_aff, edge_type='cause'))
        self.assertTrue(cm.graph.has_edge(gender, pos_aff, edge_type='associate'))
        self.assertTrue(cm.graph.has_edge(age, pos_aff, edge_type='associate'))
        self.assertTrue(cm.graph.has_edge(time, pos_aff, edge_type='associate'))
        
    # Verify CM with Study Design
    def test_verify_with_design(self):
        
        pos_aff = ts.Numeric('Positive Affect')
        es = ts.Numeric('Emotional Suppression')
        cr = ts.Numeric('Cognitive Reappraisal')
        gender = ts.Numeric('Gender')
        age = ts.Numeric('Age')
        time = ts.Numeric('Hours since 7am')

        cm = ts.ConceptualModel(
            causal_relationships = [es.cause(pos_aff), cr.cause(pos_aff)],
            associative_relationships = [age.associate(pos_aff), gender.associate(pos_aff), time.associate(pos_aff)]
        )

        sd = ts.Design(
            dv=pos_aff,
            ivs=[es, cr, age, gender, time],
            groupings=None
        )

        verif = ts.verify(cm, sd)
        self.assertTrue(verif)
    
    def test_verify_with_statistical_model(self):
        # Verify CM with Statistical Model
        pos_aff = ts.Numeric('Positive Affect')
        es = ts.Numeric('Emotional Suppression')
        cr = ts.Numeric('Cognitive Reappraisal')
        gender = ts.Numeric('Gender')
        age = ts.Numeric('Age')
        time = ts.Numeric('Hours since 7am')
        participant = ts.Nominal('Participant') # unit 

        cm = ts.ConceptualModel(
            causal_relationships = [es.cause(pos_aff), cr.cause(pos_aff)],
            associative_relationships = [age.associate(pos_aff), gender.associate(pos_aff), time.associate(pos_aff)]
        )

        sm = ts.StatisticalModel(
            dv=pos_aff,
            main_effects=[es, cr, age, gender, time],
            interaction_effects=[(es, time), (cr, time)],
            random_intercepts=[(participant)] # how to include as a random variable?   
        )

        verif = ts.verify(cm, sm)
        self.assertTrue(verif)

