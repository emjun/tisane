import tisane as ts

from z3 import *
import unittest

# TODO: Expressivity coverage: Look at and re-implement lmer test cases
# TODO: Examples: CCWA, Kreft and de Leeuw, Statistical Rethinking --> look for adversarial examples

class StatisticalModelTest(unittest.TestCase): 

    def test_initialize_main_only_1(self): 
        expl = ts.Nominal('explanation type')
        acc = ts.Numeric('accuracy')
        variables = [acc, expl]

        sm = ts.StatisticalModel(
            dv=acc,
            main_effects=[expl]
        )

        # The graph IR has all the variables
        for v in variables: 
            self.assertTrue(sm.graph.has_variable(v))
        
        # The graph IR has all the edges we expect
        self.assertTrue(sm.graph.has_edge(expl, acc, edge_type='unknown'))
        
    def test_initialize_main_only_2(self): 
        pass

    def test_initialize_main_interaction_1(self): 
        chronotype = ts.Nominal('Group chronotype')
        composition = ts.Nominal('Group composition')
        tod = ts.Nominal('Time of day')
        qtype = ts.Nominal('Question type')
        acc = ts.Numeric('Accuracy')
        group = ts.Nominal('Group')
        variables = [acc, chronotype, composition, tod, qtype]
        
        sm = ts.StatisticalModel(
            dv=acc,
            main_effects=[chronotype, composition, tod, qtype, group], 
            interaction_effects=[(qtype, tod)], 
            random_slopes=None, 
            random_intercepts=None
        )

        # The graph IR has all the variables
        for v in variables: 
            self.assertTrue(sm.graph.has_variable(v))
        
        # The graph IR has all the edges we expect
        # Main effects
        self.assertTrue(sm.graph.has_edge(chronotype, acc, edge_type='unknown'))
        self.assertTrue(sm.graph.has_edge(composition, acc, edge_type='unknown'))
        self.assertTrue(sm.graph.has_edge(tod, acc, edge_type='unknown'))
        self.assertTrue(sm.graph.has_edge(qtype, acc, edge_type='unknown'))
        self.assertTrue(sm.graph.has_edge(group, acc, edge_type='unknown'))

        # Interaction effects
        # TODO: If introduce a new node, we may want to change/update this
        self.assertTrue(sm.graph.has_edge(qtype, tod, edge_type='unknown'))
    
    def test_initialize_main_interaction_2(self): 
        pass
    
    def test_initialize_random_slopes_1(self): 
        pass

    def test_initialize_random_slopes_2(self): 
        pass

    def test_initialize_random_intercepts_1(self): 
        pos_aff = ts.Numeric('Positive Affect')
        es = ts.Numeric('Emotional Suppression')
        cr = ts.Numeric('Cognitive Reappraisal')
        gender = ts.Numeric('Gender')
        age = ts.Numeric('Age')
        time = ts.Numeric('Hours since 7am')
        participant = ts.Nominal('participant')
        # TODO: Update if add random slopes, random intercepts to the graph!
        variables = [pos_aff, es, cr, gender, age, time]

        sm = ts.StatisticalModel(
            dv=pos_aff,
            main_effects=[es, cr, age, gender, time],
            interaction_effects=[(es, time), (cr, time)],
            random_intercepts=[(participant)] # how to include as a random variable?   
        )

        # The graph IR has all the variables
        for v in variables: 
            self.assertTrue(sm.graph.has_variable(v))
        
        # The graph IR has all the edges we expect
        # Main effects
        self.assertTrue(sm.graph.has_edge(es, pos_aff, edge_type='unknown'))
        self.assertTrue(sm.graph.has_edge(cr, pos_aff, edge_type='unknown'))
        self.assertTrue(sm.graph.has_edge(age, pos_aff, edge_type='unknown'))
        self.assertTrue(sm.graph.has_edge(gender, pos_aff, edge_type='unknown'))
        self.assertTrue(sm.graph.has_edge(time, pos_aff, edge_type='unknown'))

        # Interations
        # TODO: Update if add a new node to IR
        self.assertTrue(sm.graph.has_edge(es, time, edge_type='unknown'))
        self.assertTrue(sm.graph.has_edge(cr, time, edge_type='unknown'))

        # Random intercepts
        self.assertTrue((participant) in sm.random_intercepts)

    def test_initialize_random_intercepts_2(self): 
        pass

    def test_verify_(self): 
        # Determining the units seems to be a central part of study design specification
        # Unit = who/what the treatment applies to (in the case of experiment)
        # OR who/what the property or observation belongs to (in the case of
        # observational study)
        st = StudyDesign(
            ivs=[ts.IndependentVariable(variable=hw, unit=student), ts.IndependentVarible(variable=...)]
        )

    def test_verify_with_study_design_main_true(self): 
        expl = ts.Nominal('explanation type')
        acc = ts.Numeric('accuracy')
        participant = ts.Nominal('id')
        variables = [acc, expl, participant]

        sm = ts.StatisticalModel(
            dv=acc, 
            main_effects=[expl]
        )

        sd = ts.Design(
            dv = acc, 
            ivs = [expl.treat(participant)], # expl which was treated on participant
            groupings = None
        )

        verif = ts.verify(sm, sd)
        self.assertTrue(verif)

    def test_verify_with_study_design_main_false(self): 
        expl = ts.Nominal('explanation type')
        acc = ts.Numeric('accuracy')
        participant = ts.Nominal('id')
        variables = [acc, expl, participant]

        sm = ts.StatisticalModel(
            dv=acc, 
            main_effects=[expl, participant]
        )

        sd = ts.Design(
            dv = acc, 
            ivs = [expl.treat(participant)], # expl which was treated on participant
            groupings = None
        )

        verif = ts.verify(sm, sd)
        self.assertFalse(verif)

    def test_verify_with_study_design_interaction_true(self): 
        pass
    
    def test_verify_with_study_design_interaction_false(self): 
        pass
    
    def test_verify_with_study_design_random_slopes_true(self): 
        pass

    def test_verify_with_study_design_random_slopes_false(self): 
        pass

    def test_verify_with_study_design_random_intercepts_true(self): 
        pos_aff = ts.Numeric('Positive Affect')
        es = ts.Numeric('Emotional Suppression')
        cr = ts.Numeric('Cognitive Reappraisal')
        gender = ts.Numeric('Gender')
        age = ts.Numeric('Age')
        time = ts.Numeric('Hours since 7am')
        participant = ts.Nominal('participant')
        variables = [pos_aff, es, cr, gender, age, time, participant]

        sm = ts.StatisticalModel(
            dv=pos_aff,
            main_effects=[es, cr, age, gender, time],
            interaction_effects=[(es, time), (cr, time)],
            random_intercepts=[(participant)] # how to include as a random variable?   
        )

        sd = ts.Design(
            dv=pos_aff,
            ivs=[es, cr, age, gender, time],
            groupings=[participant.repeat(pos_aff, 12)] # the 12 should really be the cardinality of time
        )

        verif = ts.verify(sm, sd)
        self.assertTrue(verif)

    def test_verify_with_study_design_random_intercepts_false(self): 
        pass