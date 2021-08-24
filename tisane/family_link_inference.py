"""
Inferring candidnate statistical models from the IR (model effects structures) and DV (family and link functions)
"""

from abc import abstractmethod
from tisane.family import (
    AbstractFamily,
    AbstractLink,
    BinomialFamily,
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
    LogCLink,
    LogitLink,
    ProbitLink,
    CauchyLink,
    CLogLogLink,
    PowerLink,
    SquarerootLink,
    OPowerLink,
    NegativeBinomialLink,
    LogLogLink,
)
from tisane import variable
from tisane.variable import (
    AbstractVariable,
    Numeric,
    Nominal,
    Ordinal,
    Has,
    Moderates,
    NumberValue,
)
from tisane.random_effects import RandomSlope, RandomIntercept
from tisane.graph import Graph
from tisane.design import Design
from itertools import chain, combinations
from typing import Dict, List, Set, Any, Tuple
import typing  # for Union

# Family functions are members of the exponential family of probability distributions that are widely used and implemented in statsmodels, the target backend for code generation
# https://www.statsmodels.org/stable/generated/statsmodels.genmod.generalized_linear_model.GLM.html#statsmodels.genmod.generalized_linear_model.GLM
def infer_family_functions(query: Design) -> Set[AbstractFamily]:
    family_candidates = set()

    dv = query.dv
    if isinstance(dv, Numeric):
        family_candidates.add(GaussianFamily(dv))
        family_candidates.add(InverseGaussianFamily(dv))
        family_candidates.add(GammaFamily(dv))
        family_candidates.add(TweedieFamily(dv))
        family_candidates.add(PoissonFamily(dv))
    elif isinstance(dv, Ordinal):
        # Treats ordinal data as continuous
        family_candidates.add(GaussianFamily(dv))
        family_candidates.add(InverseGaussianFamily(dv))
        family_candidates.add(GammaFamily(dv))
        family_candidates.add(TweedieFamily(dv))
        family_candidates.add(PoissonFamily(dv))
        # Treats ordinal data as discrete
        family_candidates.add(BinomialFamily(dv))
        family_candidates.add(NegativeBinomialFamily(dv))
        # Not implemented in statsmodels or pymer4
        # family_candidates.add(MultinomialFamily(dv))
    else:
        assert isinstance(dv, Nominal)

        if dv.get_cardinality() == 2:
            family_candidates.add(BinomialFamily(dv))
        else:
            assert dv.get_cardinality() > 2
            family_candidates.add(NegativeBinomialFamily(dv))
            # Not implemented in statsmodels or pymer4
            # family_candidates.add(MultinomialFamily(dv))

    return family_candidates


def infer_link_functions(query: Design, family: AbstractFamily) -> Set[AbstractLink]:
    link_candidates = set()

    dv = query.dv
    if isinstance(family, GaussianFamily):
        link_candidates.add(IdentityLink(dv))
        link_candidates.add(LogLink(dv))
        link_candidates.add(LogitLink(dv))
        link_candidates.add(ProbitLink(dv))
        link_candidates.add(CLogLogLink(dv))
        link_candidates.add(PowerLink(dv))
        # Not currently implemented in statsmodels
        # link_candidates.add(OPowerLink(dv))
        link_candidates.add(NegativeBinomialLink(dv))
        # Not currently implemented in statsmodels
        # link_candidates.add(LogLogLink(dv))
        # Included in statsmodels implementation as options for Families, but not included in table (https://www.statsmodels.org/stable/generated/statsmodels.genmod.generalized_linear_model.GLM.html#statsmodels.genmod.generalized_linear_model.GLM)
        link_candidates.add(InverseLink(dv))
    elif isinstance(family, InverseGaussianFamily):
        link_candidates.add(IdentityLink(dv))
        link_candidates.add(LogLink(dv))
        # Included in statsmodels implementation as options for Families, but not included in table (https://www.statsmodels.org/stable/generated/statsmodels.genmod.generalized_linear_model.GLM.html#statsmodels.genmod.generalized_linear_model.GLM)
        link_candidates.add(InverseLink(dv))
        # Included in statsmodels implementation as options for Families, but not included in table (https://www.statsmodels.org/stable/generated/statsmodels.genmod.generalized_linear_model.GLM.html#statsmodels.genmod.generalized_linear_model.GLM)
        link_candidates.add(InverseSquaredLink(dv))
    elif isinstance(family, GammaFamily):
        link_candidates.add(IdentityLink(dv))
        link_candidates.add(LogLink(dv))
        # Not currently implemented in statsmodels
        # link_candidates.add(PowerLink(dv))
        # Included in statsmodels implementation as options for Families, but not included in table (https://www.statsmodels.org/stable/generated/statsmodels.genmod.generalized_linear_model.GLM.html#statsmodels.genmod.generalized_linear_model.GLM)
        link_candidates.add(InverseLink(dv))
    elif isinstance(family, TweedieFamily):
        # link_candidates.add(IdentityLink(dv))
        link_candidates.add(LogLink(dv))
        link_candidates.add(PowerLink(dv))
    elif isinstance(family, PoissonFamily):
        link_candidates.add(IdentityLink(dv))
        link_candidates.add(LogLink(dv))
        # Included in statsmodels implementation as options for Families, but not included in table (https://www.statsmodels.org/stable/generated/statsmodels.genmod.generalized_linear_model.GLM.html#statsmodels.genmod.generalized_linear_model.GLM)
        # Sqrt is implemented as Power(power=.5)
        link_candidates.add(SquarerootLink(dv))
    elif isinstance(family, BinomialFamily):
        # Not currently implemented in statsmodels
        # link_candidates.add(IdentityLink(dv))
        link_candidates.add(LogLink(dv))
        link_candidates.add(LogitLink(dv))
        link_candidates.add(ProbitLink(dv))
        link_candidates.add(CauchyLink(dv))
        link_candidates.add(CLogLogLink(dv))
        # link_candidates.add(PowerLink(dv))
        # Not currently implemented in statsmodels
        # link_candidates.add(OPowerLink(dv))
        # Not currently implemented in statsmodels
        # link_candidates.add(LogLogLink(dv))
        # Not currently implemented in statsmodels
        # link_candidates.add(LogCLink(dv))
    elif isinstance(family, NegativeBinomialFamily):
        link_candidates.add(IdentityLink(dv))
        link_candidates.add(LogLink(dv))
        link_candidates.add(PowerLink(dv))
        link_candidates.add(NegativeBinomialLink(dv))
        # Included in statsmodels implementation as options for Families, but not included in table (https://www.statsmodels.org/stable/generated/statsmodels.genmod.generalized_linear_model.GLM.html#statsmodels.genmod.generalized_linear_model.GLM)
        link_candidates.add(CLogLogLink(dv))
    else:
        # Not implemented in statsmodels or pymer4
        assert isinstance(family, MultinomialFamily)
        link_candidates.add(IdentityLink(dv))
        link_candidates.add(LogLink(dv))
        link_candidates.add(LogitLink(dv))
        link_candidates.add(ProbitLink(dv))

    return link_candidates
