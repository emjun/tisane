import tisane as ts 
from tisane.smt.rules import *
from tisane.smt.input_interface import InputInterface
from tisane.smt.synthesizer import Synthesizer

import unittest
from unittest.mock import patch
from unittest.mock import Mock
import pytest
from random import randrange

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
    
    def test_generate_family_numeric_dv(self): 
        global dv, gaussian_family, gamma_family

        inverse_gaussian_family = InverseGaussianFamily(dv.const)
        poisson_family = PoissonFamily(dv.const)
        
        design = ts.Design(
            dv = dv, 
            ivs = ts.Level(identifier='id', measures=[v1, v2])
        )

        synth = Synthesizer()
        family_facts = synth.generate_family(design=design)
        self.assertEqual(len(family_facts), 5)
        self.assertTrue(gaussian_family in family_facts)
        self.assertTrue(inverse_gaussian_family in family_facts)
        self.assertTrue(poisson_family in family_facts)
        self.assertTrue(gamma_family in family_facts)

    def test_generate_family_ordinal_binary_dv(self): 
        o_dv = ts.Ordinal('Ordinal DV', cardinality=2)

        o_gaussian_family = GaussianFamily(o_dv.const)
        o_gamma_family = GammaFamily(o_dv.const)
        inverse_gaussian_family = InverseGaussianFamily(o_dv.const)
        poisson_family = PoissonFamily(o_dv.const)
        binomial_family = BinomialFamily(o_dv.const)
        negative_binomial_family = NegativeBinomialFamily(o_dv.const)
        multinomial_family = MultinomialFamily(o_dv.const)
        
        design = ts.Design(
            dv = o_dv, 
            ivs = ts.Level(identifier='id', measures=[v1, v2])
        )

        synth = Synthesizer()
        family_facts = synth.generate_family(design=design)
        self.assertEqual(len(family_facts), 7)
        self.assertTrue(o_gaussian_family in family_facts)
        self.assertTrue(inverse_gaussian_family in family_facts)
        self.assertTrue(poisson_family in family_facts)
        self.assertTrue(o_gamma_family in family_facts)
        self.assertTrue(binomial_family in family_facts)
        self.assertTrue(negative_binomial_family in family_facts)
        self.assertFalse(multinomial_family in family_facts)
    
    def test_generate_family_ordinal_multi_dv(self): 
        n = randrange(3, 1000)
        o_dv = ts.Ordinal('Ordinal DV', cardinality=n)

        o_gaussian_family = GaussianFamily(o_dv.const)
        o_gamma_family = GammaFamily(o_dv.const)
        inverse_gaussian_family = InverseGaussianFamily(o_dv.const)
        poisson_family = PoissonFamily(o_dv.const)
        binomial_family = BinomialFamily(o_dv.const)
        negative_binomial_family = NegativeBinomialFamily(o_dv.const)
        multinomial_family = MultinomialFamily(o_dv.const)
        
        design = ts.Design(
            dv = o_dv, 
            ivs = ts.Level(identifier='id', measures=[v1, v2])
        )

        synth = Synthesizer()
        family_facts = synth.generate_family(design=design)
        self.assertEqual(len(family_facts), 6)
        self.assertTrue(o_gaussian_family in family_facts)
        self.assertTrue(inverse_gaussian_family in family_facts)
        self.assertTrue(poisson_family in family_facts)
        self.assertTrue(o_gamma_family in family_facts)
        self.assertFalse(binomial_family in family_facts)
        self.assertFalse(negative_binomial_family in family_facts)
        self.assertTrue(multinomial_family in family_facts)

    def test_generate_family_nominal_binary_dv(self): 
        n_dv = ts.Nominal('Nominal DV', cardinality=2)

        n_gaussian_family = GaussianFamily(n_dv.const)
        n_gamma_family = GammaFamily(n_dv.const)
        inverse_gaussian_family = InverseGaussianFamily(n_dv.const)
        poisson_family = PoissonFamily(n_dv.const)
        binomial_family = BinomialFamily(n_dv.const)
        negative_binomial_family = NegativeBinomialFamily(n_dv.const)
        multinomial_family = MultinomialFamily(n_dv.const)
        
        design = ts.Design(
            dv = n_dv, 
            ivs = ts.Level(identifier='id', measures=[v1, v2])
        )

        synth = Synthesizer()
        family_facts = synth.generate_family(design=design)
        self.assertEqual(len(family_facts), 2)
        self.assertFalse(n_gaussian_family in family_facts)
        self.assertFalse(inverse_gaussian_family in family_facts)
        self.assertFalse(poisson_family in family_facts)
        self.assertFalse(n_gamma_family in family_facts)
        self.assertTrue(binomial_family in family_facts)
        self.assertTrue(negative_binomial_family in family_facts)
        self.assertFalse(multinomial_family in family_facts)
    
    def test_generate_family_nominal_multi_dv(self): 
        n = randrange(3, 1000)
        n_dv = ts.Nominal('Nominal DV', cardinality=n)

        n_gaussian_family = GaussianFamily(n_dv.const)
        n_gamma_family = GammaFamily(n_dv.const)
        inverse_gaussian_family = InverseGaussianFamily(n_dv.const)
        poisson_family = PoissonFamily(n_dv.const)
        binomial_family = BinomialFamily(n_dv.const)
        negative_binomial_family = NegativeBinomialFamily(n_dv.const)
        multinomial_family = MultinomialFamily(n_dv.const)
        
        design = ts.Design(
            dv = n_dv, 
            ivs = ts.Level(identifier='id', measures=[v1, v2])
        )

        synth = Synthesizer()
        family_facts = synth.generate_family(design=design)
        self.assertEqual(len(family_facts), 1)
        self.assertFalse(n_gaussian_family in family_facts)
        self.assertFalse(inverse_gaussian_family in family_facts)
        self.assertFalse(poisson_family in family_facts)
        self.assertFalse(n_gamma_family in family_facts)
        self.assertFalse(binomial_family in family_facts)
        self.assertFalse(negative_binomial_family in family_facts)
        self.assertTrue(multinomial_family in family_facts)

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