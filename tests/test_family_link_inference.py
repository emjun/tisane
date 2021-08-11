"""
Tests how family and link functions are inferred
NOTE: The tests are only to test, not to make any statements about how these variables relate in the real world
"""

from tisane.family import BinomialFamily, GammaFamily, GaussianFamily, InverseGaussianFamily, MultinomialFamily, NegativeBinomialFamily, PoissonFamily, TweedieFamily
import tisane as ts
from tisane import graph_inference
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
from tisane.statistical_model_inference import generate_family_functions
import unittest


class FamilyLinkInferenceTest(unittest.TestCase):
    def test_generates_families_numeric_dv(self):
        u0 = ts.Unit("Unit 0")
        m0 = u0.numeric("Measure 0")
        dv = u0.numeric("Dependent variable")

        design = ts.Design(dv=dv, ivs=[m0])
        gr = design.graph

        families = generate_family_functions(query=design)
        self.assertEqual(len(families), 8)
        for f in families: 
            f_type = type(f)
            self.assertIn(f_type, DataForTests.numeric_families_types)
    
    def test_generates_families_ordinal_dv(self):
        u0 = ts.Unit("Unit 0")
        m0 = u0.numeric("Measure 0")
        dv = u0.ordinal("Dependent variable", order=[1, 2, 3, 4, 5])

        design = ts.Design(dv=dv, ivs=[m0])
        gr = design.graph

        families = generate_family_functions(query=design)
        self.assertEqual(len(families), 8)
        for f in families: 
            f_type = type(f)
            self.assertIn(f_type, DataForTests.ordinal_families_types)

    def test_generates_families_nominal_binary_dv(self): 
        u0 = ts.Unit("Unit 0")
        m0 = u0.numeric("Measure 0")
        dv = u0.nominal("Dependent variable", cardinality=2)

        design = ts.Design(dv=dv, ivs=[m0])
        gr = design.graph

        families = generate_family_functions(query=design)
        self.assertEqual(len(families), 2)
        for f in families: 
            f_type = type(f)
            self.assertIn(f_type, DataForTests.nominal_binary_families_types)

    def test_generate_link_for_Gaussian_family(self): 
        pass
    
    def test_generate_link_for_InverseGaussian_family(self): 
        pass
    
    def test_generate_link_for_Gamma_family(self): 
        pass

    def test_generate_link_for_Tweedie_family(self): 
        pass

    def test_generate_link_for_Poisson_family(self): 
        pass

    def test_generate_link_for_Binomial_family(self): 
        pass

    def test_generate_link_for_NegativeBinomial_family(self): 
        pass

    def test_generate_link_for_Multinomial_family(self): 
        pass

    # TODO START HERE: 
    # 2. Write tests
    # 3. Gauge energy levels and todos 
    # 4. Implement family/link (could be evening thing)

class DataForTests: 
    numeric_families_types = [GaussianFamily, InverseGaussianFamily, GammaFamily, TweedieFamily, PoissonFamily, BinomialFamily, NegativeBinomialFamily, MultinomialFamily]
    ordinal_families_types = [GaussianFamily, InverseGaussianFamily, GammaFamily, TweedieFamily, PoissonFamily, BinomialFamily, NegativeBinomialFamily, MultinomialFamily]
    nominal_binary_families_types = [BinomialFamily, NegativeBinomialFamily]
    nominal_nary_families_types = [MultinomialFamily]

        