"""
Tests initialization, graph construction, and verification of several different study designs.
"""

import tisane as ts
from tisane.variable import Treatment, Nest, RepeatedMeasure
from tisane.level import Level, LevelSet

import unittest

class DesignTest(unittest.TestCase): 
    def test_initialize_1_level(self): 
        acc = ts.Numeric('accuracy')
        expl = ts.Nominal('explanation type')
        variables = [acc, expl]
        
        iv = ts.Level(identifier='id', measures=[expl])

        design = ts.Design(
            dv = acc, 
            ivs = iv
        )

        # DV 
        self.assertEquals(design.dv, acc)
        # Levels 
        self.assertEquals(design.levels, iv)

        # The graph IR has all the variables
        self.assertEquals(len(design.graph.get_variables()), len(variables) + 1) # +1 for the identifier
        for v in variables: 
            self.assertTrue(design.graph.has_variable(v))
        # The graph IR has the identifier
        pid = None 
        for v in design.graph.get_variables(): 
            if v.name == 'id': 
                pid = v
        self.assertIsNotNone(pid)

        # The graph IR has all the edges we expect
        self.assertEqual(len(design.graph.get_edges()), 2)
        self.assertTrue(design.graph.has_edge(expl, acc, edge_type='contribute'))
        self.assertTrue(design.graph.has_edge(pid, expl, edge_type='has'))
    
    def test_initialize_2_levels(self): 
        """Example from Kreft and de Leeuw, 1989"""

        # Variables
        math = ts.Numeric('MathAchievement')
        hw = ts.Numeric('HomeWork')
        race = ts.Nominal('Race')
        mean_ses = ts.Numeric('MeanSES')
        variables = [math, hw, race, mean_ses]

        # No need to create a separate variable for 'student' and 'school'
        student_level = ts.Level(identifier='student', measures=[hw, race])
        school_level = ts.Level(identifier='school', measures=[mean_ses])

        design = ts.Design(
            dv=math, 
            ivs=student_level.nest_under(school_level)
        )

        # DV 
        self.assertEquals(design.dv, math)
        # Levels 
        self.assertTrue(isinstance(design.levels, LevelSet))
        self.assertTrue(student_level in design.levels.get_levels())
        self.assertTrue(school_level in design.levels.get_levels())

        # The graph IR has all the variables
        self.assertEquals(len(design.graph.get_variables()), len(variables) + 2) # +1 for each identifier
        for v in variables: 
            self.assertTrue(design.graph.has_variable(v))
        # The graph IR has the identifier
        student_id = None 
        school_id = None
        for v in design.graph.get_variables(): 
            if v.name == 'student': 
                student_id = v
            elif v.name == 'school': 
                school_id = v
        self.assertIsNotNone(student_id)
        self.assertIsNotNone(school_id)

        # The graph IR has all the edges we expect
        self.assertEqual(len(design.graph.get_edges()), 7)
        self.assertTrue(design.graph.has_edge(hw, math, edge_type='contribute'))
        self.assertTrue(design.graph.has_edge(race, math, edge_type='contribute'))
        self.assertTrue(design.graph.has_edge(mean_ses, math, edge_type='contribute'))
        self.assertTrue(design.graph.has_edge(student_id, hw, edge_type='has'))
        self.assertTrue(design.graph.has_edge(student_id, race, edge_type='has'))
        self.assertTrue(design.graph.has_edge(school_id, mean_ses, edge_type='has'))
        self.assertTrue(design.graph.has_edge(student_id, school_id, edge_type='nest'))


    # def test_initialize_ivs_only_2(self): 
    #     chronotype = ts.Nominal('Group chronotype')
    #     composition = ts.Nominal('Group composition')
    #     tod = ts.Nominal('Time of day')
    #     qtype = ts.Nominal('Question type')
    #     acc = ts.Numeric('Accuracy')
    #     group = ts.Nominal('Group')
    #     variables = [acc, chronotype, composition, tod, qtype, group]

    #     design = ts.Design(
    #         dv = acc, 
    #         ivs = [chronotype.treat(group, 1), composition.treat(group, 1), tod.treat(group, 1), qtype.treat(group, 2)]
    #     )

    #     # The graph IR has all the variables
    #     for v in variables: 
    #         self.assertTrue(design.graph.has_variable(v))

    #     # The graph IR has all the edges we expect
    #     self.assertTrue(design.graph.has_edge(chronotype, acc, edge_type='unknown'))        
    #     self.assertTrue(design.graph.has_edge(composition, acc, edge_type='unknown'))        
    #     self.assertTrue(design.graph.has_edge(tod, acc, edge_type='unknown'))        
    #     self.assertTrue(design.graph.has_edge(qtype, acc, edge_type='unknown'))        
    #     # Treatment
    #     self.assertTrue(design.graph.has_edge(chronotype, group, edge_type='treat'))        
    #     edge = design.graph.get_edge(chronotype, group, edge_type='treat')
    #     edge_data = edge[2]
    #     edge_obj = edge_data['edge_obj']
    #     self.assertIsInstance(edge_obj, Treatment)
    #     self.assertIs(edge_obj.unit, group)
    #     self.assertIs(edge_obj.treatment, chronotype)
        
    #     self.assertTrue(design.graph.has_edge(composition, group, edge_type='treat'))        
    #     edge = design.graph.get_edge(composition, group, edge_type='treat')
    #     edge_data = edge[2]
    #     edge_obj = edge_data['edge_obj']
    #     self.assertIsInstance(edge_obj, Treatment)
    #     self.assertIs(edge_obj.unit, group)
    #     self.assertIs(edge_obj.treatment, composition)

    #     self.assertTrue(design.graph.has_edge(tod, group, edge_type='treat'))        
    #     edge = design.graph.get_edge(tod, group, edge_type='treat')
    #     edge_data = edge[2]
    #     edge_obj = edge_data['edge_obj']
    #     self.assertIsInstance(edge_obj, Treatment)
    #     self.assertIs(edge_obj.unit, group)
    #     self.assertIs(edge_obj.treatment, tod)

    #     self.assertTrue(design.graph.has_edge(qtype, group, edge_type='treat'))        
    #     edge = design.graph.get_edge(qtype, group, edge_type='treat')
    #     edge_data = edge[2]
    #     edge_obj = edge_data['edge_obj']
    #     self.assertIsInstance(edge_obj, Treatment)
    #     self.assertIs(edge_obj.unit, group)
    #     self.assertIs(edge_obj.treatment, qtype)

    #     self.assertEqual(len(design.graph.get_edges()), 8)
    #     self.assertEqual(len(design.graph.get_nodes()), len(variables))

    # def test_initialize_repeat_1(self): 
    #     expl = ts.Nominal('explanation type')
    #     correct = ts.Nominal('correct') # yes/no
    #     participant = ts.Nominal('id')
    #     variables = [expl, correct, participant]

    #     design = ts.Design(
    #         dv = correct, 
    #         ivs = [expl.treat(participant, 1)], # treatment
    #         groupings = [participant.repeat(correct, 50)], # participant observations are closer to each other than between participants in a condition
    #     )

    #     # The graph IR has all the edges we expect
    #     self.assertTrue(design.graph.has_edge(expl, correct, edge_type='unknown'))
    #     # Treatment 
    #     self.assertTrue(design.graph.has_edge(expl, participant, edge_type='treat'))
    #     edge = design.graph.get_edge(expl, participant, edge_type='treat')
    #     self.assertIsNotNone(edge)
    #     edge_data = edge[2]
    #     edge_obj = edge_data['edge_obj']
    #     self.assertIsInstance(edge_obj, Treatment)
    #     self.assertIs(edge_obj.unit, participant)
    #     self.assertIs(edge_obj.treatment, expl)
    #     # Nesting 
    #     design.graph.has_edge(participant, correct, edge_type='repeat')
    #     edge = design.graph.get_edge(participant, correct, edge_type='repeat')
    #     self.assertIsNotNone(edge)
    #     edge_data = edge[2]
    #     edge_obj = edge_data['edge_obj']
    #     self.assertIsInstance(edge_obj, RepeatedMeasure)
    #     self.assertIs(edge_obj.unit, participant)
    #     self.assertIs(edge_obj.response, correct)
    #     self.assertEqual(edge_obj.number_of_measures, 50)

    #     self.assertEqual(len(design.graph.get_edges()), 3)
    #     self.assertEqual(len(design.graph.get_nodes()), len(variables))

    # def test_initialize_nesting_2(self): 
    #     chronotype = ts.Nominal('Group chronotype')
    #     composition = ts.Nominal('Group composition')
    #     tod = ts.Nominal('Time of day')
    #     qtype = ts.Nominal('Question type')
    #     acc = ts.Numeric('Accuracy')
    #     group = ts.Nominal('Group')
    #     participant = ts.Nominal('id')
    #     variables = [chronotype, composition, tod, qtype, acc, group, participant]

    #     design = ts.Design(
    #         dv = acc, 
    #         ivs = [group, chronotype.treat(group, 1), composition.treat(group, 1), tod.treat(group, 1), qtype.treat(group, 2)], # listing group here is including a random slope/intercept for group
    #         groupings = [participant.nested_under(group), group.repeat(acc, 2)] # might want to separate out for end-user
    #     )

    #     # The graph IR has all the edges we expect
    #     self.assertTrue(design.graph.has_edge(group, acc, edge_type='unknown'))
    #     self.assertTrue(design.graph.has_edge(chronotype, acc, edge_type='unknown'))
    #     self.assertTrue(design.graph.has_edge(composition, acc, edge_type='unknown'))
    #     self.assertTrue(design.graph.has_edge(tod, acc, edge_type='unknown'))
    #     self.assertTrue(design.graph.has_edge(qtype, acc, edge_type='unknown'))
    #     # Treatment 
    #     self.assertTrue(design.graph.has_edge(chronotype, group, edge_type='treat'))
    #     edge = design.graph.get_edge(chronotype, group, edge_type='treat')
    #     self.assertIsNotNone(edge)
    #     edge_data = edge[2]
    #     edge_obj = edge_data['edge_obj']
    #     self.assertIsInstance(edge_obj, Treatment)
    #     self.assertIs(edge_obj.unit, group)
    #     self.assertIs(edge_obj.treatment, chronotype)

    #     self.assertTrue(design.graph.has_edge(composition, group, edge_type='treat'))
    #     edge = design.graph.get_edge(composition, group, edge_type='treat')
    #     self.assertIsNotNone(edge)
    #     edge_data = edge[2]
    #     edge_obj = edge_data['edge_obj']
    #     self.assertIsInstance(edge_obj, Treatment)
    #     self.assertIs(edge_obj.unit, group)
    #     self.assertIs(edge_obj.treatment, composition)

    #     self.assertTrue(design.graph.has_edge(tod, group, edge_type='treat'))
    #     edge = design.graph.get_edge(tod, group, edge_type='treat')
    #     self.assertIsNotNone(edge)
    #     edge_data = edge[2]
    #     edge_obj = edge_data['edge_obj']
    #     self.assertIsInstance(edge_obj, Treatment)
    #     self.assertIs(edge_obj.unit, group)
    #     self.assertIs(edge_obj.treatment, tod)

    #     self.assertTrue(design.graph.has_edge(qtype, group, edge_type='treat'))
    #     edge = design.graph.get_edge(qtype, group, edge_type='treat')
    #     self.assertIsNotNone(edge)
    #     edge_data = edge[2]
    #     edge_obj = edge_data['edge_obj']
    #     self.assertIsInstance(edge_obj, Treatment)
    #     self.assertIs(edge_obj.unit, group)
    #     self.assertIs(edge_obj.treatment, qtype)
        
    #     # Nesting 
    #     design.graph.has_edge(participant, group, edge_type='nest')
    #     edge = design.graph.get_edge(participant, group, edge_type='nest')
    #     self.assertIsNotNone(edge)
    #     edge_data = edge[2]
    #     edge_obj = edge_data['edge_obj']
    #     self.assertIsInstance(edge_obj, Nest)
    #     self.assertIs(edge_obj.unit, participant)
    #     self.assertIs(edge_obj.group, group)

    #     design.graph.has_edge(group, acc, edge_type='repeat')
    #     edge = design.graph.get_edge(group, acc, edge_type='repeat')
    #     self.assertIsNotNone(edge)
    #     edge_data = edge[2]
    #     edge_obj = edge_data['edge_obj']
    #     self.assertIsInstance(edge_obj, RepeatedMeasure)
    #     self.assertIs(edge_obj.unit, group)
    #     self.assertIs(edge_obj.response, acc)
    #     self.assertEqual(edge_obj.number_of_measures, 2)

    #     self.assertEqual(len(design.graph.get_edges()), 11)
    #     self.assertEqual(len(design.graph.get_nodes()), len(variables))

    # def test_verify_with_conceptual_model_true_1(self):
    #     pos_aff = ts.Numeric('Positive Affect')
    #     es = ts.Numeric('Emotional Suppression')
    #     cr = ts.Numeric('Cognitive Reappraisal')
    #     gender = ts.Numeric('Gender')
    #     age = ts.Numeric('Age')
    #     time = ts.Numeric('Hours since 7am')

    #     sd = ts.Design(
    #         dv=pos_aff,
    #         ivs=[es, cr, age, gender, time],
    #         groupings=None
    #     )

    #     cm = ts.ConceptualModel(
    #         causal_relationships = [es.cause(pos_aff), cr.cause(pos_aff)],
    #         associative_relationships = [age.associate(pos_aff), gender.associate(pos_aff), time.associate(pos_aff)]
    #     )

    #     verif = ts.verify(sd, cm)
    #     self.assertTrue(verif)

    # def test_verify_with_conceptual_model_true_2(self):
    #     expl = ts.Nominal('explanation type')
    #     correct = ts.Nominal('correct') # yes/no
    #     participant = ts.Nominal('id')

    #     sd = ts.Design(
    #         dv = correct, 
    #         ivs = [expl.treat(participant, 1)], # treatment
    #         groupings = [participant.repeat(correct, 50)], # participant observations are closer to each other than between participants in a condition
    #     )

    #     cm = ts.ConceptualModel(
    #         causal_relationships = [expl.cause(correct)],
    #         associative_relationships = None
    #     )

    #     verif = ts.verify(sd, cm)
    #     self.assertTrue(verif)
    
    # def test_verify_with_conceptual_model_false(self):
    #     chronotype = ts.Nominal('Group chronotype')
    #     composition = ts.Nominal('Group composition')
    #     tod = ts.Nominal('Time of day')
    #     qtype = ts.Nominal('Question type')
    #     acc = ts.Numeric('Accuracy')
    #     group = ts.Nominal('Group')
    #     variables = [acc, chronotype, composition, tod, qtype]

    #     sd = ts.Design(
    #         dv = acc, 
    #         ivs = [chronotype.treat(group, 1), composition.treat(group, 1), tod.treat(group, 1), qtype.treat(group, 2)]
    #     )

    #     cm = ts.ConceptualModel(
    #         causal_relationships=[chronotype.cause(acc), composition.cause(acc), tod.cause(acc), qtype.cause(acc)],
    #         associative_relationships=[tod.associate(qtype)]
    #     )

    #     verif = ts.verify(sd, cm)
    #     # Sound but not complete
    #     self.assertFalse(verif)

    # # TODO: Verify with statisitcal model
    # def test_verify_with_statistical_model(self):
    #     pass
