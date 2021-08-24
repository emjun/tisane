"""
Tests how family and link functions are inferred
NOTE: The tests are only to test, not to make any statements about how these variables relate in the real world
"""

from os import link
from tisane import data
from tisane.family import (
    BinomialFamily,
    CauchyLink,
    GammaFamily,
    GaussianFamily,
    IdentityLink,
    InverseGaussianFamily,
    MultinomialFamily,
    NegativeBinomialFamily,
    PoissonFamily,
    TweedieFamily,
    IdentityLink,
    InverseLink,
    InverseSquaredLink,
    LogLink,
    LogitLink,
    ProbitLink,
    CLogLogLink,
    PowerLink,
    SquarerootLink,
    OPowerLink,
    NegativeBinomialLink,
    LogLogLink,
)
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
from tisane.family_link_inference import (
    infer_family_functions,
    infer_link_functions,
)
import unittest


class FamilyLinkInferenceTest(unittest.TestCase):
    def test_generates_families_numeric_dv(self):
        u0 = ts.Unit("Unit 0")
        m0 = u0.numeric("Measure_0")
        dv = u0.numeric("Dependent_variable")

        design = ts.Design(dv=dv, ivs=[m0])
        gr = design.graph

        families = infer_family_functions(query=design)
        self.assertEqual(len(families), len(DataForTests.numeric_families_types))
        for f in families:
            f_type = type(f)
            self.assertIn(f_type, DataForTests.numeric_families_types)

    def test_generates_families_ordinal_dv(self):
        u0 = ts.Unit("Unit 0")
        m0 = u0.numeric("Measure_0")
        dv = u0.ordinal("Dependent_variable", order=[1, 2, 3, 4, 5])

        design = ts.Design(dv=dv, ivs=[m0])
        gr = design.graph

        families = infer_family_functions(query=design)
        self.assertEqual(len(families), len(DataForTests.ordinal_families_types))
        for f in families:
            f_type = type(f)
            self.assertIn(f_type, DataForTests.ordinal_families_types)

    def test_generates_families_nominal_binary_dv(self):
        u0 = ts.Unit("Unit 0")
        m0 = u0.numeric("Measure_0")
        dv = u0.nominal("Dependent_variable", cardinality=2)

        design = ts.Design(dv=dv, ivs=[m0])
        gr = design.graph

        families = infer_family_functions(query=design)
        self.assertEqual(len(families), len(DataForTests.nominal_binary_families_types))
        for f in families:
            f_type = type(f)
            self.assertIn(f_type, DataForTests.nominal_binary_families_types)

    def test_generates_families_nominal_multiple_categories_dv(self):
        u0 = ts.Unit("Unit 0")
        m0 = u0.numeric("Measure_0")
        dv = u0.nominal("Dependent_variable", cardinality=10)

        design = ts.Design(dv=dv, ivs=[m0])
        gr = design.graph

        families = infer_family_functions(query=design)
        self.assertEqual(len(families), len(DataForTests.nominal_nary_families_types))
        for f in families:
            f_type = type(f)
            self.assertIn(f_type, DataForTests.nominal_nary_families_types)

    def test_generate_link_for_Gaussian_family_numeric_dv(self):
        u0 = ts.Unit("Unit 0")
        m0 = u0.numeric("Measure_0")
        dv = u0.numeric("Dependent_variable")

        design = ts.Design(dv=dv, ivs=[m0])
        gr = design.graph

        family = GaussianFamily(dv)
        self.assertIsInstance(family.link, IdentityLink)
        link_candidates = infer_link_functions(query=design, family=family)

        self.assertEqual(len(link_candidates), len(DataForTests.gaussian_links))
        for l in link_candidates:
            l_type = type(l)
            self.assertIn(l_type, DataForTests.gaussian_links)

    def test_generate_link_for_InverseGaussian_family_numeric_dv(self):
        u0 = ts.Unit("Unit 0")
        m0 = u0.numeric("Measure_0")
        dv = u0.numeric("Dependent_variable")

        design = ts.Design(dv=dv, ivs=[m0])
        gr = design.graph

        family = InverseGaussianFamily(dv)
        self.assertIsInstance(family.link, InverseSquaredLink)
        link_candidates = infer_link_functions(query=design, family=family)

        self.assertEqual(len(link_candidates), len(DataForTests.inverse_gaussian_links))
        for l in link_candidates:
            l_type = type(l)
            self.assertIn(l_type, DataForTests.inverse_gaussian_links)

    def test_generate_link_for_Gamma_family_numeric_dv(self):
        u0 = ts.Unit("Unit 0")
        m0 = u0.numeric("Measure_0")
        dv = u0.numeric("Dependent_variable")

        design = ts.Design(dv=dv, ivs=[m0])
        gr = design.graph

        family = GammaFamily(dv)
        self.assertIsInstance(family.link, InverseLink)
        link_candidates = infer_link_functions(query=design, family=family)

        self.assertEqual(len(link_candidates), len(DataForTests.gamma_links))
        for l in link_candidates:
            l_type = type(l)
            self.assertIn(l_type, DataForTests.gamma_links)

    def test_generate_link_for_Tweedie_family_numeric_dv(self):
        u0 = ts.Unit("Unit 0")
        m0 = u0.numeric("Measure_0")
        dv = u0.numeric("Dependent_variable")

        design = ts.Design(dv=dv, ivs=[m0])
        gr = design.graph

        family = TweedieFamily(dv)
        self.assertIsInstance(family.link, LogLink)
        link_candidates = infer_link_functions(query=design, family=family)

        self.assertEqual(len(link_candidates), len(DataForTests.tweedie_links))
        for l in link_candidates:
            l_type = type(l)
            self.assertIn(l_type, DataForTests.tweedie_links)

    def test_generate_link_for_Poisson_family_numeric_dv(self):
        u0 = ts.Unit("Unit 0")
        m0 = u0.numeric("Measure_0")
        dv = u0.numeric("Dependent_variable")

        design = ts.Design(dv=dv, ivs=[m0])
        gr = design.graph

        family = PoissonFamily(dv)
        self.assertIsInstance(family.link, LogLink)
        link_candidates = infer_link_functions(query=design, family=family)

        self.assertEqual(len(link_candidates), len(DataForTests.poisson_links))
        for l in link_candidates:
            l_type = type(l)
            self.assertIn(l_type, DataForTests.poisson_links)

    def test_generate_link_for_Gaussian_family_ordinal_dv(self):
        u0 = ts.Unit("Unit 0")
        m0 = u0.numeric("Measure_0")
        dv = u0.ordinal("Dependent_variable", order=[1, 2, 3])

        design = ts.Design(dv=dv, ivs=[m0])
        gr = design.graph

        family = GaussianFamily(dv)
        self.assertIsInstance(family.link, IdentityLink)
        link_candidates = infer_link_functions(query=design, family=family)

        self.assertEqual(len(link_candidates), len(DataForTests.gaussian_links))
        for l in link_candidates:
            l_type = type(l)
            self.assertIn(l_type, DataForTests.gaussian_links)

    def test_generate_link_for_InverseGaussian_family_ordinal_dv(self):
        u0 = ts.Unit("Unit 0")
        m0 = u0.numeric("Measure_0")
        dv = u0.ordinal("Dependent_variable", order=[1, 2, 3])

        design = ts.Design(dv=dv, ivs=[m0])
        gr = design.graph

        family = InverseGaussianFamily(dv)
        self.assertIsInstance(family.link, InverseSquaredLink)
        link_candidates = infer_link_functions(query=design, family=family)

        self.assertEqual(len(link_candidates), len(DataForTests.inverse_gaussian_links))
        for l in link_candidates:
            l_type = type(l)
            self.assertIn(l_type, DataForTests.inverse_gaussian_links)

    def test_generate_link_for_Gamma_family_ordinal_dv(self):
        u0 = ts.Unit("Unit 0")
        m0 = u0.numeric("Measure_0")
        dv = u0.ordinal("Dependent_variable", order=[1, 2, 3])

        design = ts.Design(dv=dv, ivs=[m0])
        gr = design.graph

        family = GammaFamily(dv)
        self.assertIsInstance(family.link, InverseLink)
        link_candidates = infer_link_functions(query=design, family=family)

        self.assertEqual(len(link_candidates), len(DataForTests.gamma_links))
        for l in link_candidates:
            l_type = type(l)
            self.assertIn(l_type, DataForTests.gamma_links)

    def test_generate_link_for_Tweedie_family_ordinal_dv(self):
        u0 = ts.Unit("Unit 0")
        m0 = u0.numeric("Measure_0")
        dv = u0.ordinal("Dependent_variable", order=[1, 2, 3])

        design = ts.Design(dv=dv, ivs=[m0])
        gr = design.graph

        family = TweedieFamily(dv)
        self.assertIsInstance(family.link, LogLink)
        link_candidates = infer_link_functions(query=design, family=family)

        self.assertEqual(len(link_candidates), len(DataForTests.tweedie_links))
        for l in link_candidates:
            l_type = type(l)
            self.assertIn(l_type, DataForTests.tweedie_links)

    def test_generate_link_for_Poisson_family_ordinal_dv(self):
        u0 = ts.Unit("Unit 0")
        m0 = u0.numeric("Measure_0")
        dv = u0.ordinal("Dependent_variable", order=[1, 2, 3])

        design = ts.Design(dv=dv, ivs=[m0])
        gr = design.graph

        family = PoissonFamily(dv)
        self.assertIsInstance(family.link, LogLink)
        link_candidates = infer_link_functions(query=design, family=family)

        self.assertEqual(len(link_candidates), 3)
        for l in link_candidates:
            l_type = type(l)
            self.assertIn(l_type, DataForTests.poisson_links)

    def test_generate_link_for_Binomial_family_ordinal_dv(self):
        u0 = ts.Unit("Unit 0")
        m0 = u0.numeric("Measure_0")
        dv = u0.ordinal("Dependent_variable", order=[1, 2, 3])

        design = ts.Design(dv=dv, ivs=[m0])
        gr = design.graph

        family = BinomialFamily(dv)
        self.assertIsInstance(family.link, LogitLink)
        link_candidates = infer_link_functions(query=design, family=family)

        self.assertEqual(len(link_candidates), len(DataForTests.binomial_links))
        for l in link_candidates:
            l_type = type(l)
            self.assertIn(l_type, DataForTests.binomial_links)

    def test_generate_link_for_NegativeBinomial_family_ordinal_dv(self):
        u0 = ts.Unit("Unit 0")
        m0 = u0.numeric("Measure_0")
        dv = u0.ordinal("Dependent_variable", order=[1, 2, 3])

        design = ts.Design(dv=dv, ivs=[m0])
        gr = design.graph

        family = NegativeBinomialFamily(dv)
        self.assertIsInstance(family.link, LogLink)
        link_candidates = infer_link_functions(query=design, family=family)

        self.assertEqual(len(link_candidates), len(DataForTests.negative_binomial_links))
        for l in link_candidates:
            l_type = type(l)
            self.assertIn(l_type, DataForTests.negative_binomial_links)

    def test_generate_link_for_Multinomial_family_ordinal_dv(self):
        u0 = ts.Unit("Unit 0")
        m0 = u0.numeric("Measure_0")
        dv = u0.ordinal("Dependent_variable", order=[1, 2, 3])

        design = ts.Design(dv=dv, ivs=[m0])
        gr = design.graph

        family = MultinomialFamily(dv)
        self.assertIsInstance(family.link, LogitLink)
        link_candidates = infer_link_functions(query=design, family=family)

        self.assertEqual(len(link_candidates), 4)
        for l in link_candidates:
            l_type = type(l)
            self.assertIn(l_type, DataForTests.multinomial_links)

    def test_generate_link_for_Binomial_family_nominal_dv(self):
        u0 = ts.Unit("Unit 0")
        m0 = u0.numeric("Measure_0")
        dv = u0.nominal("Dependent_variable", cardinality=2)

        design = ts.Design(dv=dv, ivs=[m0])
        gr = design.graph

        family = BinomialFamily(dv)
        self.assertIsInstance(family.link, LogitLink)
        link_candidates = infer_link_functions(query=design, family=family)

        self.assertEqual(len(link_candidates), len(DataForTests.binomial_links))
        for l in link_candidates:
            l_type = type(l)
            self.assertIn(l_type, DataForTests.binomial_links)

    def test_generate_link_for_NegativeBinomial_family_nominal_dv(self):
        u0 = ts.Unit("Unit 0")
        m0 = u0.numeric("Measure_0")
        dv = u0.nominal("Dependent_variable", cardinality=3)

        design = ts.Design(dv=dv, ivs=[m0])
        gr = design.graph

        family = NegativeBinomialFamily(dv)
        self.assertIsInstance(family.link, LogLink)
        link_candidates = infer_link_functions(query=design, family=family)

        self.assertEqual(len(link_candidates), len(DataForTests.negative_binomial_links))
        for l in link_candidates:
            l_type = type(l)
            self.assertIn(l_type, DataForTests.negative_binomial_links)

    def test_generate_link_for_Multinomial_family_nominal_dv(self):
        u0 = ts.Unit("Unit 0")
        m0 = u0.numeric("Measure_0")
        dv = u0.nominal("Dependent_variable", cardinality=5)

        design = ts.Design(dv=dv, ivs=[m0])
        gr = design.graph

        family = MultinomialFamily(dv)
        self.assertIsInstance(family.link, LogitLink)
        link_candidates = infer_link_functions(query=design, family=family)

        self.assertEqual(len(link_candidates), 4)
        for l in link_candidates:
            l_type = type(l)
            self.assertIn(l_type, DataForTests.multinomial_links)


class DataForTests:
    numeric_families_types = [
        GaussianFamily,
        InverseGaussianFamily,
        GammaFamily,
        TweedieFamily,
        PoissonFamily,
    ]
    ordinal_families_types = [
        GaussianFamily,
        InverseGaussianFamily,
        GammaFamily,
        TweedieFamily,
        PoissonFamily,
        BinomialFamily,
        NegativeBinomialFamily,
        # Not implemented in statsmodels or pymer4
        # MultinomialFamily,
    ]
    nominal_binary_families_types = [BinomialFamily]
    nominal_nary_families_types = [
        # Not implemented in statsmodels or pymer4
        # MultinomialFamily,
        NegativeBinomialFamily
    ]

    gaussian_links = [
        IdentityLink,
        LogLink,
        LogitLink,
        ProbitLink,
        CLogLogLink,
        PowerLink,
        # Not currently implemented in statsmodels
        # OPowerLink,
        NegativeBinomialLink,
        # Not currently implemented in statsmodels
        # LogLogLink,
        # Included in statsmodels implementation as options for Families, but not included in table (https://www.statsmodels.org/stable/generated/statsmodels.genmod.generalized_linear_model.GLM.html#statsmodels.genmod.generalized_linear_model.GLM)
        InverseLink,
    ]
    inverse_gaussian_links = [
        IdentityLink,
        LogLink,
        # Included in statsmodels implementation as options for Families, but not included in table (https://www.statsmodels.org/stable/generated/statsmodels.genmod.generalized_linear_model.GLM.html#statsmodels.genmod.generalized_linear_model.GLM)
        InverseLink,
        # Included in statsmodels implementation as options for Families, but not included in table (https://www.statsmodels.org/stable/generated/statsmodels.genmod.generalized_linear_model.GLM.html#statsmodels.genmod.generalized_linear_model.GLM)
        InverseSquaredLink
    ]
    gamma_links = [
        IdentityLink,
        LogLink,
        # Not currently implemented in statsmodels
        # PowerLink,
        # Included in statsmodels implementation as options for Families, but not included in table (https://www.statsmodels.org/stable/generated/statsmodels.genmod.generalized_linear_model.GLM.html#statsmodels.genmod.generalized_linear_model.GLM)
        InverseLink,
    ]
    tweedie_links = [LogLink, PowerLink]
    poisson_links = [IdentityLink, LogLink, SquarerootLink]
    binomial_links = [
        # Not currently implemented in statsmodels
        # IdentityLink,
        LogLink,
        LogitLink,
        ProbitLink,
        CauchyLink,
        CLogLogLink,
        # Not currently implemented in statsmodels
        # OPowerLink,
        # Not currently implemented in statsmodels
        # LogLogLink,
    ]
    negative_binomial_links = [IdentityLink, LogLink, PowerLink, NegativeBinomialLink, CLogLogLink]
    multinomial_links = [IdentityLink, LogLink, LogitLink, ProbitLink]
