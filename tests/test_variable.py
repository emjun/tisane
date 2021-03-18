import tisane as ts
from tisane.variable import Associate, Has, Cause, Nest

import unittest

class VariableTest(unittest.TestCase):
    
    def test_associates_with(self):
        pid = ts.Nominal('participant')
        expl = ts.Nominal('explanation type')
        acc = ts.Numeric('accuracy')

        # Conceptual relationships
        acc.associates_with(expl)
        
        self.assertEqual(len(acc.relationships), 1)
        self.assertIsInstance(acc.relationships[0], Associate)
        self.assertEqual(acc.relationships[0].lhs, acc)
        self.assertEqual(acc.relationships[0].rhs, expl)
        self.assertEqual(len(expl.relationships), 1)
        self.assertIsInstance(expl.relationships[0], Associate)
        self.assertEqual(expl.relationships[0].lhs, expl)
        self.assertEqual(expl.relationships[0].rhs, acc)

    def test_treats(self): 
        pid = ts.Nominal('participant')
        expl = ts.Nominal('explanation type')
        acc = ts.Numeric('accuracy')

        # Data measurement relationships
        expl.treats(pid)

        self.assertEqual(len(pid.relationships), 1)
        self.assertIsInstance(pid.relationships[0], Has)
        self.assertEqual(pid.relationships[0].variable, pid)
        self.assertEqual(pid.relationships[0].measure, expl)
    
    def test_all_conceptual_relationships(self):
        math = ts.Numeric('MathAchievement')
        hw = ts.Numeric('HomeWork')
        race = ts.Nominal('Race')
        ses = ts.Numeric('SES')
        
        # Conceptual relationships 
        # NOTE: This is purely to taste the API, not to make any statements about how these variables relate in the real world
        race.associates_with(math)
        ses.cause(hw)
        hw.cause(math)

        self.assertEqual(len(race.relationships), 1)
        self.assertIsInstance(race.relationships[0], Associate)
        self.assertEqual(race.relationships[0].lhs, race)
        self.assertEqual(race.relationships[0].rhs, math)

        self.assertEqual(len(ses.relationships), 1)
        self.assertIsInstance(ses.relationships[0], Cause)
        self.assertEqual(ses.relationships[0].cause, ses)
        self.assertEqual(ses.relationships[0].effect, hw)

        self.assertEqual(len(hw.relationships), 2)
        self.assertIsInstance(hw.relationships[0], Cause)
        self.assertEqual(hw.relationships[0].cause, ses)
        self.assertEqual(hw.relationships[0].effect, hw)
        self.assertIsInstance(hw.relationships[1], Cause)
        self.assertEqual(hw.relationships[1].cause, hw)
        self.assertEqual(hw.relationships[1].effect, math)

        self.assertEqual(len(math.relationships), 2)
        self.assertIsInstance(math.relationships[0], Associate)
        self.assertEqual(math.relationships[0].lhs, math)
        self.assertEqual(math.relationships[0].rhs, race)
        self.assertIsInstance(math.relationships[1], Cause)
        self.assertEqual(math.relationships[1].cause, hw)
        self.assertEqual(math.relationships[1].effect, math)

    # Test that the has relationship update both variables
    def test_has(self): 
        pid = ts.Nominal('participant')
        expl = ts.Nominal('explanation type')
        acc = ts.Numeric('accuracy')

        pid.has(expl)

        self.assertTrue(len(pid.relationships), 1)
        self.assertIsInstance(pid.relationships[0], Has)
        self.assertEqual(pid.relationships[0].variable, pid)
        self.assertEqual(pid.relationships[0].measure, expl)

        self.assertTrue(len(expl.relationships), 1)
        self.assertIsInstance(expl.relationships[0], Has)
        self.assertEqual(expl.relationships[0].variable, pid)
        self.assertEqual(expl.relationships[0].measure, expl)
    
    # Test that the nest relationships updates both variables
    def test_nest(self): 
        student = ts.Nominal('student id')
        school = ts.Nominal('school id')

        student.nest_under(school)

        self.assertEqual(len(student.relationships), 1)
        self.assertIsInstance(student.relationships[0], Nest)
        self.assertEqual(student.relationships[0].base, student)
        self.assertEqual(student.relationships[0].group, school)

        self.assertEqual(len(school.relationships), 1)
        self.assertIsInstance(school.relationships[0], Nest)
        self.assertEqual(school.relationships[0].base, student)
        self.assertEqual(school.relationships[0].group, school)

    # def test_has_two_levels(self): 
    #     math = ts.Numeric('MathAchievement')
    #     hw = ts.Numeric('HomeWork')
    #     race = ts.Nominal('Race')
    #     ses = ts.Numeric('SES')

    #     # No need to create a separate variable for 'student' and 'school'
    #     student_level = ts.Level(identifier='student', measures=[hw, race])
    #     school_level = ts.Level(identifier='school', measures=[ses])

    #     design = ts.Design(
    #         dv=math, 
    #         ivs=student_level.nest_under(school_level)
    #     )


        # NOTE: to use streamlit, try starting up and running streamlit from
        # Input Interface before asking for input?