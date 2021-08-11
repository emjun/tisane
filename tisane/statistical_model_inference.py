"""
Inferring candidnate statistical models from the IR (model effects structures) and DV (family and link functions)
"""

from abc import abstractmethod
from tisane.og_variable import Numeric, Ordinal, Nominal
from tisane.family import AbstractFamily, GaussianFamily, InverseGaussianFamily, GammaFamily, TweedieFamily, PoissonFamily, BinomialFamily, NegativeBinomialFamily, MultinomialFamily
from tisane import variable
from tisane.variable import AbstractVariable, Numeric, Has, Moderates, NumberValue
from tisane.random_effects import RandomSlope, RandomIntercept
from tisane.graph import Graph
from tisane.design import Design
from tisane.graph_inference import infer_main_effects, infer_interaction_effects, infer_random_effects
from itertools import chain, combinations
from typing import Dict, List, Set, Any, Tuple
import typing # for Union

# Family functions are members of the exponential family of probability distributions that are widely used and implemented in statsmodels, the target backend for code generation
# https://www.statsmodels.org/stable/generated/statsmodels.genmod.generalized_linear_model.GLM.html#statsmodels.genmod.generalized_linear_model.GLM
def generate_family_functions(query: Design) -> Set[AbstractFamily]: 
    family_candidates = set() 

    dv = query.dv
    if isinstance(dv, Numeric): 
        family_candidates.add(GaussianFamily())    
        family_candidates.add(InverseGaussianFamily())    
        family_candidates.add(GammaFamily())
        family_candidates.add(TweedieFamily())
        family_candidates.add(PoissonFamily())
    elif isinstance(dv, Ordinal): 
        # Treats ordinal data as continuous
        family_candidates.add(GaussianFamily())    
        family_candidates.add(InverseGaussianFamily())    
        family_candidates.add(GammaFamily())
        family_candidates.add(TweedieFamily())
        family_candidates.add(PoissonFamily())
        # Treats ordinal data as discrete
        family_candidates.add(BinomialFamily())
        family_candidates.add(NegativeBinomialFamily())
        family_candidates.add(MultinomialFamily())
    else: 
        assert(isinstance(dv, Nominal))
        if dv.get_cardinality() == 2: 
            family_candidates.add(BinomialFamily())
            family_candidates.add(NegativeBinomialFamily())
        else: 
            assert(dv.get_cardinality() > 2)
            family_candidates.add(MultinomialFamily())

    return family_candidates

def generate_link_functions(query: Design, family: AbstractFamily): 
    link_candidates = set()
    # TODO: Identify which of these is actually implemented in Statsmodels
    if isinstance(family, GaussianFamily): 
        link_candidates.add(IdentityLink())
        link_candidates.add(LogLink())
        link_candidates.add(LogitLink())
        link_candidates.add(ProbitLink())
        link_candidates.add(CLogLogLink())
        link_candidates.add(PowerLink())
        link_candidates.add(OPowerLink())
        link_candidates.add(NegativeBinomialLink())
        link_candidates.add(LogLogLink())
    elif isinstance(family, InverseGaussianFamily): 
        link_candidates.add(IdentityLink())
        link_candidates.add(LogLink())
        link_candidates.add(PowerLink())
    elif isinstance(family, GammaFamily): 
        link_candidates.add(IdentityLink())
        link_candidates.add(LogLink())
        link_candidates.add(PowerLink())
    elif isinstance(family, TweedieFamily): 
        link_candidates.add(IdentityLink())
        link_candidates.add(LogLink())
        link_candidates.add(PowerLink())
    elif isinstance(family, PoissonFamily): 
        link_candidates.add(IdentityLink())
        link_candidates.add(LogLink())
        link_candidates.add(PowerLink())
    elif isinstance(family, BinomialFamily): 
        link_candidates.add(IdentityLink())
        link_candidates.add(LogLink())
        link_candidates.add(LogitLink())
        link_candidates.add(ProbitLink())
        link_candidates.add(CLogLogLink())
        link_candidates.add(PowerLink())
        link_candidates.add(OPowerLink())
        link_candidates.add(LogLogLink())
        link_candidates.add(LogCLink())
    elif isinstance(family, NegativeBinomialFamily): 
        link_candidates.add(IdentityLink())
        link_candidates.add(LogLink())
        link_candidates.add(PowerLink())
        link_candidates.add(NegativeBinomialLink())
    else: 
        assert(isinstance(family, MultinomialFamily))
        link_candidates.add(IdentityLink())
        link_candidates.add(LogLink())
        link_candidates.add(LogitLink())
        link_candidates.add(ProbitLink())

# Combine all the main effects, interaction effects, and random effects
# TODO: In order to make it easy to populate the GUI/disambiguation questions and react to analysts' selections, what should the right data structure be?
def generate_all_candidate_model_effects_structures(gr: Graph, query: Design): 
    pass

# TODO: In order to make it easy to populate the GUI/disambiguation questions and react to analysts' selections, what should the right data structure be?
def generate_all_statistical_model_candidates(gr: Graph, query: Design): 
    pass