import tisane as ts
from tisane.variable import Associate, Has, Cause, Nest, Treatment, RepeatedMeasure

import unittest


class VariableTest(unittest.TestCase):
    def test_associates_with(self):
        pid = ts.Nominal("participant")
        expl = ts.Nominal("explanation type")
        acc = ts.Numeric("accuracy")

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
        pid = ts.Nominal("participant")
        expl = ts.Nominal("explanation type")
        acc = ts.Numeric("accuracy")

        # Data measurement relationships
        expl.treats(pid)

        self.assertEqual(len(pid.relationships), 1)
        self.assertIsInstance(pid.relationships[0], Treatment)
        self.assertEqual(pid.relationships[0].unit, pid)
        self.assertEqual(pid.relationships[0].treatment, expl)

    def test_repeats(self):
        pig = ts.Nominal("pig id")
        time = ts.Nominal("week number")
        weight = ts.Numeric("weight")

        pig.repeats(weight, according_to=time)

        self.assertEqual(len(pig.relationships), 1)
        self.assertIsInstance(pig.relationships[0], RepeatedMeasure)
        relat = pig.relationships[0]
        self.assertEqual(relat.unit, pig)
        self.assertEqual(relat.response, weight)
        self.assertEqual(relat.according_to, time)

    def test_all_conceptual_relationships(self):
        math = ts.Numeric("MathAchievement")
        hw = ts.Numeric("HomeWork")
        race = ts.Nominal("Race")
        ses = ts.Numeric("SES")

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
        pid = ts.Nominal("participant")
        expl = ts.Nominal("explanation type")
        acc = ts.Numeric("accuracy")

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
        student = ts.Nominal("student id")
        school = ts.Nominal("school id")

        student.nest_under(school)

        self.assertEqual(len(student.relationships), 1)
        self.assertIsInstance(student.relationships[0], Nest)
        self.assertEqual(student.relationships[0].base, student)
        self.assertEqual(student.relationships[0].group, school)

        self.assertEqual(len(school.relationships), 1)
        self.assertIsInstance(school.relationships[0], Nest)
        self.assertEqual(school.relationships[0].base, student)
        self.assertEqual(school.relationships[0].group, school)

    def test_unit_type(self):
        student = ts.Unit("student id")
        school = ts.Unit("school id")

        self.assertIsInstance(student, ts.Unit)
        self.assertIsInstance(school, ts.Unit)

        self.assertIsInstance(student, ts.Nominal)
        self.assertIsInstance(school, ts.Nominal)

    def test_unit_has_error(self):
        student = ts.Unit("student id")
        school = ts.Unit("school id")
        test_score = ts.Numeric("test score")

        error = False
        try:
            student.has(test_score)

        except:
            error = True

        self.assertTrue(error)

    def test_unit_has_exactly(self):
        student = ts.Unit("student id")
        test_score = ts.Numeric("test score")

        student.has(test_score, exactly=1)

        # Check that student and test_score have the same has relationship stored
        self.assertEqual(len(student.relationships), 1)
        self.assertEqual(len(test_score.relationships), 1)

        relat = student.relationships[0]
        self.assertIn(relat, test_score.relationships)

        self.assertEqual(relat.repetitions, 1)

    def test_unit_has_up_to(self):
        student = ts.Unit("student id")
        test_score = ts.Numeric("test score")

        student.has(test_score, up_to=2)

        # Check that student and test_score have the same has relationship stored
        self.assertEqual(len(student.relationships), 1)
        self.assertEqual(len(test_score.relationships), 1)

        relat = student.relationships[0]
        self.assertIn(relat, test_score.relationships)

        self.assertEqual(relat.repetitions, 2)


    def test_unit_repeats(self):
        student = ts.Unit("student id")
        test_score = ts.Numeric("test score")
        test_time = ts.Nominal("pre/post", cardinality=2)

        student.repeats(test_score, according_to=test_time)  # repeats
        # student.has(test_score, exactly=1).foreach(test_time) # under the hood?
        self.assertEqual(len(student.relationships), 1)
        self.assertEqual(len(test_score.relationships), 1)

        relat = student.relationships[0]
        self.assertIn(relat, test_score.relationships)

        self.assertEqual(relat.according_to, test_time)

        # Alternative
        # student.has(test_score, exactly=2)
        # test_score.has(test_time, exactly=1).foreach(test_time)

    def test_unit_has_relationships(self): 
        pass