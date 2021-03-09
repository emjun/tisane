import tisane as ts

from z3 import *
import unittest

# TODO: Expressivity coverage: Look at and re-implement lmer test cases
# TODO: Examples: CCWA, Kreft and de Leeuw, Statistical Rethinking --> look for adversarial examples

class StatisticalModelTest(unittest.TestCase): 
    def test_initialize_fixed_only(self):
        """ Example from Bansal et al. CHI 2021
        """ 
        expl = ts.Nominal('explanation type')
        acc = ts.Numeric('accuracy')
        variables = [acc, expl]

        sm = ts.StatisticalModel(
            dv=acc,
            fixed_ivs=[expl]
        )

        # Statistical Model has properties we expect
        self.assertEquals(sm.random_slopes, list())
        self.assertEquals(sm.random_intercepts, list())
        self.assertEquals(sm.interactions, list())
        self.assertIsNone(sm.family)
        self.assertIsNone(sm.link_func)

        # The graph IR has all the variables
        for v in variables: 
            self.assertTrue(sm.graph.has_variable(v))
        self.assertEquals(len(sm.graph.get_variables()), 2)
        
        # The graph IR has all the edges we expect
        self.assertEquals(len(sm.graph.get_edges()), 1)
        self.assertTrue(sm.graph.has_edge(expl, acc, edge_type='contribute'))
        
    def test_initialize_fixed_interaction_1(self): 
        """ Example from Jun et al. CSCW 2019
        """
        chronotype = ts.Nominal('Group chronotype')
        composition = ts.Nominal('Group composition')
        tod = ts.Nominal('Time of day')
        qtype = ts.Nominal('Question type')
        acc = ts.Numeric('Accuracy')
        group = ts.Nominal('Group')
        variables = [acc, chronotype, composition, tod, qtype]
        
        sm = ts.StatisticalModel(
            dv=acc,
            fixed_ivs=[chronotype, composition, tod, qtype, group], 
            random_slopes=None, 
            random_intercepts=None,
            interactions=[(qtype, tod)]
        )

        # Statistical Model has properties we expect
        self.assertEquals(sm.random_slopes, list())
        self.assertEquals(sm.random_intercepts, list())
        self.assertIsNone(sm.family)
        self.assertIsNone(sm.link_func)

        # The graph IR has all the variables
        self.assertEquals(len(sm.graph.get_variables()), 7) # variables + 1 interaction 
        for v in variables: 
            self.assertTrue(sm.graph.has_variable(v))
        variables_in_graph = sm.graph.get_variables()
        ixn_var = None
        for v in variables_in_graph: 
            if v.name == '*'.join([qtype.name,tod.name]):
                ixn_var = v
        self.assertIsNotNone(ixn_var) # Interaction variable in the graph as a node
        
        # The graph IR has all the edges we expect
        self.assertEquals(len(sm.graph.get_edges()), 6)
        # Main effects
        self.assertTrue(sm.graph.has_edge(chronotype, acc, edge_type='contribute'))
        self.assertTrue(sm.graph.has_edge(composition, acc, edge_type='contribute'))
        self.assertTrue(sm.graph.has_edge(tod, acc, edge_type='contribute'))
        self.assertTrue(sm.graph.has_edge(qtype, acc, edge_type='contribute'))
        self.assertTrue(sm.graph.has_edge(group, acc, edge_type='contribute'))
        # Interaction effects
        self.assertTrue(sm.graph.has_edge(ixn_var, acc, edge_type='contribute'))
    
    def test_initialize_main_interaction_2(self): 
        """ Example adapted from Jun et al. CSCW 2019
        """
        chronotype = ts.Nominal('Group chronotype')
        composition = ts.Nominal('Group composition')
        tod = ts.Nominal('Time of day')
        qtype = ts.Nominal('Question type')
        acc = ts.Numeric('Accuracy')
        group = ts.Nominal('Group')
        variables = [acc, chronotype, composition, tod, qtype]
        
        sm = ts.StatisticalModel(
            dv=acc,
            fixed_ivs=[chronotype, composition, tod, qtype, group], 
            random_slopes=None, 
            random_intercepts=None,
            interactions=[(qtype, tod, composition)]
        )

        # Statistical Model has properties we expect
        self.assertEquals(sm.random_slopes, list())
        self.assertEquals(sm.random_intercepts, list())
        self.assertIsNone(sm.family)
        self.assertIsNone(sm.link_func)

        # The graph IR has all the variables
        self.assertEquals(len(sm.graph.get_variables()), 7) # variables + 1 interaction 
        for v in variables: 
            self.assertTrue(sm.graph.has_variable(v))
        variables_in_graph = sm.graph.get_variables()
        ixn_var = None
        for v in variables_in_graph: 
            if v.name == '*'.join([qtype.name,tod.name,composition.name]):
                ixn_var = v
        self.assertIsNotNone(ixn_var) # Interaction variable in the graph as a node
        
        # The graph IR has all the edges we expect
        self.assertEquals(len(sm.graph.get_edges()), 6)
        # Main effects
        self.assertTrue(sm.graph.has_edge(chronotype, acc, edge_type='contribute'))
        self.assertTrue(sm.graph.has_edge(composition, acc, edge_type='contribute'))
        self.assertTrue(sm.graph.has_edge(tod, acc, edge_type='contribute'))
        self.assertTrue(sm.graph.has_edge(qtype, acc, edge_type='contribute'))
        self.assertTrue(sm.graph.has_edge(group, acc, edge_type='contribute'))
        # Interaction effects
        self.assertTrue(sm.graph.has_edge(ixn_var, acc, edge_type='contribute'))
    
    def test_initialize_random_slopes_1(self): 
        """ From Kreft and de Leeuw 1989
        """
        math = ts.Numeric('MathAchievement')
        # Student-level variables 
        student = ts.Nominal('id')
        hw = ts.Numeric('HomeWork')
        race = ts.Nominal('Race')
        # School-level variables
        school = ts.Nominal('school')
        mean_ses = ts.Numeric('MeanSES')
        variables = [math, hw, race, mean_ses]
        identifiers = [student, school]

        random_slopes = [(hw, school)]
        sm = ts.StatisticalModel(
            dv=math,
            fixed_ivs=[race, mean_ses], 
            random_slopes=random_slopes, 
            random_intercepts=None,
            interactions=[(hw, mean_ses)], 
        )

        # Statistical Model has properties we expect
        self.assertEquals(sm.random_slopes, random_slopes)
        self.assertEquals(sm.random_intercepts, list())
        self.assertIsNone(sm.family)
        self.assertIsNone(sm.link_func)

        # The graph IR has all the variables
        self.assertEquals(len(sm.graph.get_variables()), 7) # 1 dv + 2 fixed + 3 random slopes + 1 interaction
        for v in variables: 
            self.assertTrue(sm.graph.has_variable(v))
        variables_in_graph = sm.graph.get_variables()
        student_id = None 
        school_id = None
        ixn_var = None
        for v in variables_in_graph: 
            if v.name == '*'.join([hw.name,mean_ses.name]):
                ixn_var = v
            if v.name == 'Unknown identifier': 
                student_id = v
            if v.name == 'school': 
                school_id = v
        self.assertIsNotNone(ixn_var) # Interaction variable in the graph as a node
        self.assertIsNotNone(student_id) # Student variable in the graph as an unknown identifier node
        self.assertIsNotNone(school_id) # School variable in the graph as an identifier node
        
        # The graph IR has all the edges we expect
        self.assertEquals(len(sm.graph.get_edges()), 7)
        # Main effects
        self.assertTrue(sm.graph.has_edge(hw, math, edge_type='contribute'))
        self.assertTrue(sm.graph.has_edge(race, math, edge_type='contribute'))
        self.assertTrue(sm.graph.has_edge(mean_ses, math, edge_type='contribute'))
        # Interaction effects
        self.assertTrue(sm.graph.has_edge(ixn_var, math, edge_type='contribute'))
        # Identifier
        self.assertTrue(sm.graph.has_edge(student_id, hw, edge_type='has'))
        self.assertTrue(sm.graph.has_edge(student_id, ixn_var, edge_type='has'))
        # Nesting
        self.assertTrue(sm.graph.has_edge(student_id, school_id, edge_type='nest'))

    # def test_initialize_random_slopes_2(self): 
    #     pass

    # Note: Graph of Variable as a random Random Slope or Random Intercept are identical
    def test_initialize_random_intercepts_1(self): 
        """ From Kreft and de Leeuw 1989
        """
        math = ts.Numeric('MathAchievement')
        # Student-level variables 
        student = ts.Nominal('id')
        hw = ts.Numeric('HomeWork')
        race = ts.Nominal('Race')
        # School-level variables
        school = ts.Nominal('school')
        mean_ses = ts.Numeric('MeanSES')
        variables = [math, hw, race, mean_ses]
        identifiers = [student, school]

        random_intercepts = [(hw, school)]
        sm = ts.StatisticalModel(
            dv=math,
            fixed_ivs=[race, mean_ses], 
            random_slopes=None,
            random_intercepts=random_intercepts,
            interactions=[(hw, mean_ses)], 
        )

        # Statistical Model has properties we expect
        self.assertEquals(sm.random_slopes, list())
        self.assertEquals(sm.random_intercepts, random_intercepts)
        self.assertIsNone(sm.family)
        self.assertIsNone(sm.link_func)

        # The graph IR has all the variables
        self.assertEquals(len(sm.graph.get_variables()), 7) # 1 dv + 2 fixed + 3 random intercepts + 1 interaction
        for v in variables: 
            self.assertTrue(sm.graph.has_variable(v))
        variables_in_graph = sm.graph.get_variables()
        student_id = None 
        school_id = None
        ixn_var = None
        for v in variables_in_graph: 
            if v.name == '*'.join([hw.name,mean_ses.name]):
                ixn_var = v
            if v.name == 'Unknown identifier': 
                student_id = v
            if v.name == 'school': 
                school_id = v
        self.assertIsNotNone(ixn_var) # Interaction variable in the graph as a node
        self.assertIsNotNone(student_id) # Student variable in the graph as an unknown identifier node
        self.assertIsNotNone(school_id) # School variable in the graph as an identifier node
        
        # The graph IR has all the edges we expect
        self.assertEquals(len(sm.graph.get_edges()), 7)
        # Main effects
        self.assertTrue(sm.graph.has_edge(hw, math, edge_type='contribute'))
        self.assertTrue(sm.graph.has_edge(race, math, edge_type='contribute'))
        self.assertTrue(sm.graph.has_edge(mean_ses, math, edge_type='contribute'))
        # Interaction effects
        self.assertTrue(sm.graph.has_edge(ixn_var, math, edge_type='contribute'))
        # Identifier
        self.assertTrue(sm.graph.has_edge(student_id, hw, edge_type='has'))
        self.assertTrue(sm.graph.has_edge(student_id, ixn_var, edge_type='has'))
        # Nesting
        self.assertTrue(sm.graph.has_edge(student_id, school_id, edge_type='nest'))

    # def test_initialize_random_intercepts_2(self): 
    #     pos_aff = ts.Numeric('Positive Affect')
    #     es = ts.Numeric('Emotional Suppression')
    #     cr = ts.Numeric('Cognitive Reappraisal')
    #     gender = ts.Numeric('Gender')
    #     age = ts.Numeric('Age')
    #     time = ts.Numeric('Hours since 7am')
    #     participant = ts.Nominal('participant')
    #     # TODO: Update if add random slopes, random intercepts to the graph!
    #     variables = [pos_aff, es, cr, gender, age, time]

    #     sm = ts.StatisticalModel(
    #         dv=pos_aff,
    #         main_effects=[es, cr, age, gender, time],
    #         interaction_effects=[(es, time), (cr, time)],
    #         random_intercepts=[(participant)] # how to include as a random variable?   
    #     )

    #     # The graph IR has all the variables
    #     for v in variables: 
    #         self.assertTrue(sm.graph.has_variable(v))
        
    #     # The graph IR has all the edges we expect
    #     # Main effects
    #     self.assertTrue(sm.graph.has_edge(es, pos_aff, edge_type='unknown'))
    #     self.assertTrue(sm.graph.has_edge(cr, pos_aff, edge_type='unknown'))
    #     self.assertTrue(sm.graph.has_edge(age, pos_aff, edge_type='unknown'))
    #     self.assertTrue(sm.graph.has_edge(gender, pos_aff, edge_type='unknown'))
    #     self.assertTrue(sm.graph.has_edge(time, pos_aff, edge_type='unknown'))

    #     # Interations
    #     # TODO: Update if add a new node to IR
    #     self.assertTrue(sm.graph.has_edge(es, time, edge_type='unknown'))
    #     self.assertTrue(sm.graph.has_edge(cr, time, edge_type='unknown'))

    #     # Random intercepts
    #     self.assertTrue((participant) in sm.random_intercepts)

    # def test_verify_(self): 
    #     # Determining the units seems to be a central part of study design specification
    #     # Unit = who/what the treatment applies to (in the case of experiment)
    #     # OR who/what the property or observation belongs to (in the case of
    #     # observational study)
    #     st = StudyDesign(
    #         ivs=[ts.IndependentVariable(variable=hw, unit=student), ts.IndependentVarible(variable=...)]
    #     )

    # def test_verify_with_study_design_main_true(self): 
    #     expl = ts.Nominal('explanation type')
    #     acc = ts.Numeric('accuracy')
    #     participant = ts.Nominal('id')
    #     variables = [acc, expl, participant]

    #     sm = ts.StatisticalModel(
    #         dv=acc, 
    #         main_effects=[expl]
    #     )

    #     sd = ts.Design(
    #         dv = acc, 
    #         ivs = [expl.treat(participant)], # expl which was treated on participant
    #         groupings = None
    #     )

    #     verif = ts.verify(sm, sd)
    #     self.assertTrue(verif)

    # def test_verify_with_study_design_main_false(self): 
    #     expl = ts.Nominal('explanation type')
    #     acc = ts.Numeric('accuracy')
    #     participant = ts.Nominal('id')
    #     variables = [acc, expl, participant]

    #     sm = ts.StatisticalModel(
    #         dv=acc, 
    #         main_effects=[expl, participant]
    #     )

    #     sd = ts.Design(
    #         dv = acc, 
    #         ivs = [expl.treat(participant)], # expl which was treated on participant
    #         groupings = None
    #     )

    #     verif = ts.verify(sm, sd)
    #     self.assertFalse(verif)

    # def test_verify_with_study_design_interaction_true(self): 
    #     pass
    
    # def test_verify_with_study_design_interaction_false(self): 
    #     pass
    
    # def test_verify_with_study_design_random_slopes_true(self): 
    #     pass

    # def test_verify_with_study_design_random_slopes_false(self): 
    #     pass

    # def test_verify_with_study_design_random_intercepts_true(self): 
    #     pos_aff = ts.Numeric('Positive Affect')
    #     es = ts.Numeric('Emotional Suppression')
    #     cr = ts.Numeric('Cognitive Reappraisal')
    #     gender = ts.Numeric('Gender')
    #     age = ts.Numeric('Age')
    #     time = ts.Numeric('Hours since 7am')
    #     participant = ts.Nominal('participant')
    #     variables = [pos_aff, es, cr, gender, age, time, participant]

    #     sm = ts.StatisticalModel(
    #         dv=pos_aff,
    #         main_effects=[es, cr, age, gender, time],
    #         interaction_effects=[(es, time), (cr, time)],
    #         random_intercepts=[(participant)] # how to include as a random variable?   
    #     )

    #     sd = ts.Design(
    #         dv=pos_aff,
    #         ivs=[es, cr, age, gender, time],
    #         groupings=[participant.repeat(pos_aff, 12)] # the 12 should really be the cardinality of time
    #     )

    #     verif = ts.verify(sm, sd)
    #     self.assertTrue(verif)

    # def test_verify_with_study_design_random_intercepts_false(self): 
    #     pass