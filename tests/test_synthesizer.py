import tisane as ts 

import unittest
from unittest.mock import patch
from unittest.mock import Mock

class SynthesizerTest(unittest.TestCase): 


    @patch('tisane.smt.input_interface.InputInterface.ask_inclusion_prompt', return_value='y')
    @patch('tisane.smt.input_interface.InputInterface.ask_inclusion_prompt', return_value='y')
    def test_answer_inclusion_yes(self, input):
        self.assertTrue(InputInterface.ask_inclusion('subject'))
    def test_synth_one_level_fixed(self): 
        pass

    def test_one_level_fixed(self): 
        """
        Example from Bansal et al. CHI 2021
        """
        acc = ts.Numeric('accuracy')
        expl = ts.Nominal('explanation type')
        variables = [acc, expl]

        design = ts.Design(
            dv = acc, 
            ivs = ts.Level(identifier='id', measures=[expl])
        )

        ts.synthesize_statistical_model(design=design)
    
    def test_one_level_fixed_interaction(self): 
        """
        Example from Kreft & de Leeuw, 1989
        """
        math = ts.Numeric('MathAchievement')
        hw = ts.Numeric('HomeWork')
        race = ts.Nominal('Race')
        ses = ts.Numeric('SES')

        design = ts.Design(
            dv = math, 
            ivs = ts.Level(identifier='student', measures=[hw, race, ses])
        )

        ts.synthesize_statistical_model(design=design)
    
    def test_two_levels_fixed_interaction(self): 
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

        ts.synthesize_statistical_model(design=design)

    def test_two_levels_random(self): 
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

        ts.synthesize_statistical_model(design=design)