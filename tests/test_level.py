from tisane.level import Level, LevelSet
import tisane as ts

import unittest

class LevelTest(unittest.TestCase): 
    
    def test_level_initialize_null(self): 
        student_level = ts.Level(identifier='student', measures=None)
        school_level = ts.Level(identifier='school', measures=None)

        self.assertEquals(student_level._id, 'student')
        self.assertIsNone(student_level._measures)
        self.assertEquals(school_level._id, 'school')
        self.assertIsNone(school_level._measures)
    
    def test_level_initialize(self): 
        # Variables
        math = ts.Numeric('MathAchievement')
        hw = ts.Numeric('HomeWork')
        race = ts.Nominal('Race')
        mean_ses = ts.Numeric('MeanSES')

        # No need to create a separate variable for 'student' and 'school'
        student_level = ts.Level(identifier='student', measures=[hw, race])
        school_level = ts.Level(identifier='school', measures=[mean_ses])

        self.assertEquals(student_level._id, 'student')
        self.assertEquals(student_level._measures, [hw, race])
        self.assertEquals(school_level._id, 'school')
        self.assertEquals(school_level._measures, [mean_ses])

    def test_nest_under_levels(self): 
        # Variables
        math = ts.Numeric('MathAchievement')
        hw = ts.Numeric('HomeWork')
        race = ts.Nominal('Race')
        mean_ses = ts.Numeric('MeanSES')

        student_level = ts.Level(identifier='student', measures=[hw, race])
        school_level = ts.Level(identifier='school', measures=[mean_ses])

        levels = student_level.nest_under(school_level)

        self.assertTrue(isinstance(levels, LevelSet))
        self.assertTrue(len(levels._level_set), 2)
        self.assertEquals(levels._level_set, [student_level, school_level])


    def test_nest_under_chaining(self): 
        # Variables
        math = ts.Numeric('MathAchievement')
        hw = ts.Numeric('HomeWork')
        race = ts.Nominal('Race')
        mean_ses = ts.Numeric('MeanSES')
        income = ts.Numeric('Median Income')

        student_level = ts.Level(identifier='student', measures=[hw, race])
        school_level = ts.Level(identifier='school', measures=[mean_ses])
        district_level = ts.Level(identifier='district', measures=[income])

        levels = student_level.nest_under(school_level).nest_under(district_level)

        self.assertTrue(isinstance(levels, LevelSet))
        self.assertTrue(len(levels._level_set), 3)
        self.assertEquals(levels._level_set, [student_level, school_level, district_level])
