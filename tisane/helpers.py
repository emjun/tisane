from tisane.variable import AbstractVariable 
from tisane.design import Design
from tisane.smt.rules import *

import numpy as np
import pandas as pd
from scipy import stats
from scipy.special import logit
import tweedie
from typing import List

from z3 import *

def generate_data_dist_from_facts(fact: z3.BoolRef, design: Design):
    size = design.dataset.get_length()
    if 'GaussianFamily' in str(fact) and 'Inverse' not in str(fact):
        mean = 0.0
        std = 1.0
        return np.random.default_rng().normal(loc=mean, scale=std, size=size)
    elif 'InverseGaussianFamily' in str(fact):
        mean = .5 # TODO 
        std = 1.0
        
        return np.random.default_rng().wald(mean=mean, scale=std, size=size)
    elif 'PoissonFamily' in str(fact):
        lam = 1.0
        
        return np.random.default_rng().poisson(lam=lam, size=size)
    elif 'GammaFamily' in str(fact):
        shape = 2.0 # Can calculate from mean? 
        scale = 1.0 # Can calculate from std?
        
        return np.random.default_rng().gamma(shape=shape, scale=scale, size=size)
    elif 'TweedieFamily' in str(fact):
        mean = 10 # These are random values
        p = 1.5 # These are random values
        phi = 20 # These are random values
        n = 1000
        return tweedie.tweedie(mu=mean, p=p, phi=phi).rvs(n)
    elif 'BinomialFamily' in str(fact) and 'Negative' not in str(fact):
        n = 1000 # number of trials 
        p = .5 # probability of success
        
        return np.random.default_rng().binomial(n=n, p=p, size=size)
    elif 'NegativeBinomialFamily' in str(fact):
        n = 1000 # number of successes
        p = .5 # probability of success
        
        return np.random.default_rng().negative_binomial(n=n, p=p, size=size)
    elif 'MultinomialFamily' in str(fact):
        dv = design.dv
        assert(dv.cardinality > 2)
        n = 1000 # number of trials/experiments
        pvals = (1./dv.cardinality) # probability of each case 
        
        return np.random.default_rng().multinomial(n=n, pvals=pvals, size=size)
    else: 
        raise ValueError(f'Unknown distribution fact: {str(fact)}')

def transform_data_from_fact(data: pd.DataFrame, link_fact: z3.BoolRef):
    if 'IdentityTransform' in str(link_fact): 
        # Do nothing
        return data
    elif 'LogTransform' in str(link_fact) and 'CLogLog' not in str(link_fact): 
        return np.log(data)
    elif 'CLogLogTransform' in str(link_fact): 
        raise NotImplementedError
    elif 'SquarerootTransform' in str(link_fact): 
        return np.sqrt(data)
    elif 'InverseTransform' in str(link_fact): 
        raise NotImplementedError
    elif 'InverseSquaredTransform' in str(link_fact): 
        raise NotImplementedError
    elif 'PowerTransform' in str(link_fact): 
        transformed_data = stats.boxcox(data['data'])[0]
        return pd.DataFrame(data=transformed_data)
    elif 'CauchyTransform' in str(link_fact): 
        raise NotImplementedError
    elif 'LogLogTransform' in str(link_fact):
        raise NotImplementedError
    elif 'ProbitTransform' in str(link_fact): 
        raise NotImplementedError
    elif 'LogitTransform' in str(link_fact): 
        # TODO: make sure that the values are numbers
        transformed_data = logit(data['data'])
        return pd.DataFrame(data=transformed_data)
    elif 'NegativeBinomialTransform' in str(link_fact): 
        raise NotImplementedError
        
def simulate_data_for_variable(variable: AbstractVariable): 
    if isinstance(variable, Numeric): 
        # TODO: Need to know upper and lower bounds
        data = np.random.randn(1000)
    elif isinstance(variable, Nominal): 
        pass
    elif isinstance(variable, Ordinal): 
        pass
    # TODO
    elif isisntance(variable, Count): 
        raise NotImplementedError
    else: 
        # Should never make it here
        raise ValueError(f'Unknown variable type: {type(variable)}')
