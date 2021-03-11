import tisane as ts 
from tisane.smt.rules import *
from tisane.smt.input_interface import InputInterface
from tisane.smt.synthesizer import Synthesizer

import unittest
from unittest.mock import patch
from unittest.mock import Mock
import pytest

# Globals
iv = ts.Nominal('IV')
dv = ts.Numeric('DV')
fixed_effect = FixedEffect(iv.const, dv.const)
v1 = ts.Nominal('V1')
v2 = ts.Nominal('V2')
interaction = EmptySet(Object)
interaction = SetAdd(interaction, v1.const)
interaction = SetAdd(interaction, v2.const)
interaction_effect = Interaction(interaction)
gaussian_family = GaussianFamily(dv.const)
gamma_family = GammaFamily(dv.const)

class SynthesizerTest(unittest.TestCase): 

    def test_synth_one_level_fixed(self): 
        pass

    @patch('tisane.smt.input_interface.InputInterface.ask_family', return_value=gaussian_family)
    def test_generate_and_select_family_gaussian(self, input): 
        global dv, v1, v2

        design = ts.Design(
            dv = dv, 
            ivs = ts.Level(identifier='id', measures=[v1, v2])
        )
        
        sm = ts.StatisticalModel(
            dv=dv,
            fixed_ivs=[v1, v2]
        )
        synth = Synthesizer()
        sm = synth.generate_and_select_family(design=design, statistical_model=sm)
        self.assertEqual(sm.dv, dv)
        self.assertTrue(v1 in sm.fixed_ivs)
        self.assertTrue(v2 in sm.fixed_ivs)
        self.assertEqual(sm.random_slopes, list())
        self.assertEqual(sm.random_intercepts, list())
        self.assertEqual(sm.interactions, list())
        self.assertEqual(sm.family, 'Gaussian')
        self.assertIsNone(sm.link_func)
    
    @patch('tisane.smt.input_interface.InputInterface.ask_family', return_value=gamma_family)
    def test_generate_and_select_family_gamma(self, input): 
        global dv, v1, v2

        design = ts.Design(
            dv = dv, 
            ivs = ts.Level(identifier='id', measures=[v1, v2])
        )
        
        sm = ts.StatisticalModel(
            dv=dv,
            fixed_ivs=[v1, v2]
        )
        synth = Synthesizer()
        sm = synth.generate_and_select_family(design=design, statistical_model=sm)
        self.assertEqual(sm.dv, dv)
        self.assertTrue(v1 in sm.fixed_ivs)
        self.assertTrue(v2 in sm.fixed_ivs)
        self.assertEqual(sm.random_slopes, list())
        self.assertEqual(sm.random_intercepts, list())
        self.assertEqual(sm.interactions, list())
        self.assertEqual(sm.family, 'Gamma')
        self.assertIsNone(sm.link_func)

    @patch('tisane.smt.input_interface.InputInterface.ask_inclusion_prompt', return_value='y')
    def test_answer_inclusion_yes(self, input):
        self.assertTrue(InputInterface.ask_inclusion('subject'))

    @pytest.mark.skip(reason="Sanity check that the interaction loop works after testing all the individual components")
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
    
    @pytest.mark.skip(reason="Sanity check that the interaction loop works after testing all the individual components")
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
    
    @pytest.mark.skip(reason="Sanity check that the interaction loop works after testing all the individual components")
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

    @pytest.mark.skip(reason="Sanity check that the interaction loop works after testing all the individual components")
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