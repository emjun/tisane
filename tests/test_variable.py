"""
Tests variable API.
NOTE: The API tests are only to test the API, not to make any statements about how these variables relate in the real world
"""

import tisane as ts
from tisane.variable import (
    AbstractVariable,
    Associates,
    Has,
    Causes,
    Moderates,
    Nests,
    NumberValue,
    Exactly,  # Subclass of NumberValue
    AtMost,  # Subclass of NumberValue
    Repeats,
)

import unittest


class VariableTest(unittest.TestCase):
    def test_unit_type(self):
        student = ts.Unit("student id")
        school = ts.Unit("school id")

        self.assertIsInstance(student, ts.Unit)
        self.assertIsInstance(school, ts.Unit)

        self.assertIsInstance(student, AbstractVariable)
        self.assertIsInstance(school, AbstractVariable)

    def test_unit_has_error(self):
        student = ts.Unit("student id")
        school = ts.Unit("school id")
        test_score = student.numeric("test score")

        error = False
        try:
            student._has(test_score)

        except:
            error = True

        self.assertTrue(error)

    def test_unit_has_exactly(self):
        student = ts.Unit("student id")
        test_score = student.numeric("test score")

        # Check that student and test_score have the same has relationship stored
        self.assertEqual(len(student.relationships), 1)
        self.assertEqual(len(test_score.relationships), 1)

        relat = student.relationships[0]
        self.assertIn(relat, test_score.relationships)

        self.assertIsInstance(relat.repetitions, NumberValue)
        self.assertIsInstance(relat.repetitions, Exactly)
        self.assertTrue(relat.repetitions.is_equal_to_one())

    def test_unit_has_up_to(self):
        student = ts.Unit("student id")
        test_score = student.numeric("test score", number_of_instances=2)

        # student._has(test_score, up_to=2)

        # Check that student and test_score have the same has relationship stored
        self.assertEqual(len(student.relationships), 1)
        self.assertEqual(len(test_score.relationships), 1)

        relat = student.relationships[0]
        self.assertIn(relat, test_score.relationships)

        self.assertIsInstance(relat.repetitions, NumberValue)
        self.assertIsInstance(relat.repetitions, Exactly)
        self.assertTrue(relat.repetitions.is_greater_than_one())

    # Test that the has relationship update both variables
    def test_has(self):
        pid = ts.Unit("participant")
        expl = pid.nominal("explanation type", number_of_instances=1)
        acc = pid.numeric("accuracy")

        self.assertTrue(len(pid.relationships), 1)
        self.assertIsInstance(pid.relationships[0], Has)
        self.assertEqual(pid.relationships[0].variable, pid)
        self.assertEqual(pid.relationships[0].measure, expl)

        self.assertTrue(len(expl.relationships), 1)
        self.assertIsInstance(expl.relationships[0], Has)
        self.assertEqual(expl.relationships[0].variable, pid)
        self.assertEqual(expl.relationships[0].measure, expl)

    def test_associates_with(self):
        pid = ts.Unit("participant")
        expl = pid.nominal("explanation type", number_of_instances=1)
        acc = pid.numeric("accuracy")

        # Conceptual relationships
        acc.associates_with(expl)

        self.assertEqual(len(acc.relationships), 2)
        self.assertIsInstance(acc.relationships[0], Has)
        self.assertEqual(acc.relationships[0].variable, pid)
        self.assertEqual(acc.relationships[0].measure, acc)
        self.assertTrue(acc.relationships[0].repetitions.is_equal_to_one())
        self.assertIsInstance(acc.relationships[1], Associates)
        self.assertEqual(acc.relationships[1].lhs, acc)
        self.assertEqual(acc.relationships[1].rhs, expl)

        self.assertEqual(len(expl.relationships), 2)
        self.assertIsInstance(expl.relationships[0], Has)
        self.assertEqual(expl.relationships[0].variable, pid)
        self.assertEqual(expl.relationships[0].measure, expl)
        self.assertTrue(expl.relationships[0].repetitions.is_equal_to_one())
        self.assertIsInstance(expl.relationships[1], Associates)
        self.assertEqual(expl.relationships[1].lhs, acc)
        self.assertEqual(expl.relationships[1].rhs, expl)

    def test_all_conceptual_relationships(self):
        student = ts.Unit("student")
        math = student.numeric("MathAchievement")
        hw = student.numeric("HomeWork")
        race = student.nominal("Race")
        ses = student.numeric("SES")

        # Conceptual relationships
        race.associates_with(math)
        ses.causes(hw)
        hw.causes(math)

        # Test race variable's conceptual relationships
        conceptual_relationships = list()
        for r in race.relationships:
            if isinstance(r, Causes):
                conceptual_relationships.append(r)
            elif isinstance(r, Associates):
                conceptual_relationships.append(r)
            else:
                pass
        self.assertEqual(len(conceptual_relationships), 1)
        self.assertIsInstance(conceptual_relationships[0], Associates)
        self.assertEqual(conceptual_relationships[0].lhs, race)
        self.assertEqual(conceptual_relationships[0].rhs, math)

        # Test ses variable's conceptual relationships
        conceptual_relationships = list()
        for r in ses.relationships:
            if isinstance(r, Causes):
                conceptual_relationships.append(r)
            elif isinstance(r, Associates):
                conceptual_relationships.append(r)
            else:
                pass
        self.assertEqual(len(conceptual_relationships), 1)
        self.assertIsInstance(conceptual_relationships[0], Causes)
        self.assertEqual(conceptual_relationships[0].cause, ses)
        self.assertEqual(conceptual_relationships[0].effect, hw)

        # Test hw variable's conceptual relationships
        conceptual_relationships = list()
        for r in hw.relationships:
            if isinstance(r, Causes):
                conceptual_relationships.append(r)
            elif isinstance(r, Associates):
                conceptual_relationships.append(r)
            else:
                pass
        self.assertEqual(len(conceptual_relationships), 2)
        self.assertIsInstance(conceptual_relationships[0], Causes)
        self.assertEqual(conceptual_relationships[0].cause, ses)
        self.assertEqual(conceptual_relationships[0].effect, hw)
        self.assertIsInstance(conceptual_relationships[1], Causes)
        self.assertEqual(conceptual_relationships[1].cause, hw)
        self.assertEqual(conceptual_relationships[1].effect, math)

        # Test math variable's conceptual relationships
        conceptual_relationships = list()
        for r in math.relationships:
            if isinstance(r, Causes):
                conceptual_relationships.append(r)
            elif isinstance(r, Associates):
                conceptual_relationships.append(r)
            else:
                pass
        self.assertEqual(len(conceptual_relationships), 2)
        self.assertIsInstance(conceptual_relationships[0], Associates)
        self.assertEqual(conceptual_relationships[0].lhs, race)
        self.assertEqual(conceptual_relationships[0].rhs, math)
        self.assertIsInstance(conceptual_relationships[1], Causes)
        self.assertEqual(conceptual_relationships[1].cause, hw)
        self.assertEqual(conceptual_relationships[1].effect, math)

    def test_moderate_obj(self):
        u = ts.Unit("Unit")
        v1 = u.nominal("V1")
        v2 = u.nominal("V2")
        v3 = u.nominal("V3")

        v1.moderate([v2], on=v3)
        self.assertEqual(len(v1.relationships), 2)
        self.assertEqual(len(v2.relationships), 2)
        self.assertEqual(len(v3.relationships), 2)

        relat = None
        for r in v1.relationships:
            if isinstance(r, Moderates):
                relat = r

        self.assertIsNotNone(relat)
        self.assertIn(v1, relat.moderator)
        self.assertIn(v2, relat.moderator)
        self.assertIs(v3, relat.on)

    def test_moderate_two_variables(self):
        u = ts.Unit("Unit")
        race = u.nominal("Race")
        ses = u.numeric("SES")
        test_score = u.numeric("Test score")

        race.moderate(ses, on=test_score)
        self.assertEqual(len(race.relationships), 2)
        self.assertEqual(len(ses.relationships), 2)
        self.assertEqual(len(test_score.relationships), 2)

        relat = None
        for r in race.relationships:
            if isinstance(r, Moderates):
                relat = r

        self.assertIn(relat, race.relationships)
        self.assertIn(relat, ses.relationships)
        self.assertIn(relat, test_score.relationships)

    def test_moderate_three_variables(self):
        u = ts.Unit("Unit")
        v1 = u.nominal("V1")
        v2 = u.nominal("V2")
        v3 = u.nominal("V3")
        v4 = u.nominal("V4")

        v1.moderate([v2, v3], on=v4)
        self.assertEqual(len(v1.relationships), 2)
        self.assertEqual(len(v2.relationships), 2)
        self.assertEqual(len(v3.relationships), 2)
        self.assertEqual(len(v4.relationships), 2)

        relat = None
        for r in v1.relationships:
            if isinstance(r, Moderates):
                relat = r

        self.assertIn(relat, v1.relationships)
        self.assertIn(relat, v2.relationships)
        self.assertIn(relat, v3.relationships)
        self.assertIn(relat, v4.relationships)

    def test_repeats(self):
        pig = ts.Unit("pig id")
        time = pig.nominal("week number", cardinality=12)
        weight = pig.numeric("weight", number_of_instances=time)

        self.assertEqual(len(pig.relationships), 2)
        self.assertIsInstance(pig.relationships[0], Has)
        self.assertEqual(pig.relationships[0].variable, pig)
        self.assertEqual(pig.relationships[0].measure, time)
        self.assertIsInstance(pig.relationships[0].repetitions, Exactly)
        self.assertTrue(pig.relationships[0].repetitions.is_equal_to_one())
        self.assertIsInstance(pig.relationships[1], Has)
        self.assertEqual(pig.relationships[1].variable, pig)
        self.assertEqual(pig.relationships[1].measure, weight)
        self.assertIsInstance(pig.relationships[1].repetitions, Exactly)
        self.assertTrue(pig.relationships[1].repetitions.is_greater_than_one())
        self.assertEqual(pig.relationships[1].repetitions.value, 12)

    def test_unit_repeats(self):
        student = ts.Unit("student id")
        test_time = ts.SetUp("pre/post", cardinality=2)
        test_score = student.numeric("test score", number_of_instances=test_time)

        self.assertEqual(len(student.relationships), 1)
        self.assertEqual(len(test_score.relationships), 1)

        relat = None
        for r in student.relationships:
            if isinstance(r, Has):
                relat = r

        self.assertIsNotNone(relat)
        self.assertIn(relat, test_score.relationships)
        self.assertEqual(relat.repetitions.value, test_time.get_cardinality())
        self.assertEqual(relat.according_to, test_time)

    # Test that the nest relationships updates both variables
    def test_nest(self):
        student = ts.Unit("student id")
        school = ts.Unit("school id")

        student.nests_within(school)

        self.assertEqual(len(student.relationships), 1)
        self.assertIsInstance(student.relationships[0], Nests)
        self.assertEqual(student.relationships[0].base, student)
        self.assertEqual(student.relationships[0].group, school)

        self.assertEqual(len(school.relationships), 1)
        self.assertIsInstance(school.relationships[0], Nests)
        self.assertEqual(school.relationships[0].base, student)
        self.assertEqual(school.relationships[0].group, school)

    # def test_has_variables(self):
    #     # Main question: How do we specify "time" variables that are necessary for expressing repeated measures and inferring random effects

    #     # Simple case: Tutoring is between-subjects
    #     student = ts.Unit("Student ID")
    #     race = student.nominal("Race")  # exactly=1 by default
    #     tutoring = student.nominal("Tutoring")  # exactly=1 by default
    #     score = student.numeric("Test score")  # exactly=1 by default

    #     # Tutoring is within-subjects
    #     student = ts.Unit("Student ID")
    #     race = student.nominal("Race")  # exactly=1 by default
    #     tutoring = student.nominal(
    #         "Tutoring", exactly=2
    #     )  # each student receives 2 conditions of tutoring
    #     score = student.numeric("Test score", exactly=2)
    #     student.repeats(score, according_to=tutoring)  # 1 score per tutoring condition
    #     # There need to be checks that validate the number of scores per student == number of tutoring conditions per student
    #     # Maybe some minimal upper bound checking if use up_to instead of exactly OR require both statements to use exactly/up_to

    #     # Repeated measures with time
    #     student = ts.Unit("Student ID")
    #     race = student.nominal("Race")  # exactly=1 by default
    #     score = student.numeric("Test score", exactly="week")
    #     week = student.ordinal("Week", cardinality=10)  # Week in quarter

    #     student.repeats(score, according_to=week)  # 1 score per week (10:10)

    #     # Repeated measures with Tutoring X Time
    #     student = ts.Unit("Student ID")
    #     race = student.nominal("Race")  # exactly=1 by default
    #     tutoring = student.nominal(
    #         "Tutoring", exactly=2
    #     )  # each student receives 2 conditions of tutoring
    #     score = student.numeric(
    #         "Test score", exactly=20
    #     )  # TODO: how often variable is measured according to turoring * week, no need to express repeats/what 20 corresponds to
    #     # + operator: tutoring + something else
    #     # repeated measure as how often measured according to what
    #     week = ts.CONTROL("Week", cardinality=10)  # Week in quarter

    #     student.repeats(score, according_to=tutoring)  # 1 score per tutoring condition
    #     student.repeats(
    #         score, according_to=week
    #     )  # ?? 2 scores per week in quarter if test both conditions each week
    #     # OR
    #     student.repeats(
    #         score, according_to=[tutoring, week]
    #     )  # Does this mean that the cross product of tutoring x week is unique identifier for each repeat measure?
    #     student.repeats(
    #         score, according_to=tutoring * week
    #     )  # Does this mean that the cross product of tutoring x week is unique identifier for each repeat measure?

    #     ## TODO: How are repeated measures used to generate random effects????
    #     # time as a within-subjects condition for a unit
    #     score = student.numeric("Test score", exactly=20)
    #     time = student.nominal("Week", exactly=10)
    #     student.repeats(score, according_to=10)

    #     # Is the more general problem: What happens when there are multiple within-subjects variables?
