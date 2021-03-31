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

# The values are default values that can be manipulated/updated in the UI
def generate_data_dist_from_facts(fact: z3.BoolRef, design: Design):
    dv = design.dv
    size = design.dataset.get_length()

    if 'GaussianFamily' in str(fact) and 'Inverse' not in str(fact):
        if design.dataset is not None: 
            mean = design.dataset.get_column(dv.name).mean()
            std = design.dataset.get_column(dv.name).std() # np default = 1
        else: 
            mean = 0 
            std = 1

        return np.random.default_rng().normal(loc=mean, scale=std, size=size)
    elif 'InverseGaussianFamily' in str(fact):
        if design.dataset is not None: 
            mean = design.dataset.get_column(dv.name).mean() # should be > 0
            std = design.dataset.get_column(dv.name).std() # should be >= 0
            if mean <= 0 or std < 0: 
                mean = 1
                std = 1
                
        else: 
            mean = 1
            std = 1

        return np.random.default_rng().wald(mean=mean, scale=std, size=size)
    elif 'PoissonFamily' in str(fact):
        lam = 1.0 # np default
        return np.random.default_rng().poisson(lam=lam, size=size)
    elif 'GammaFamily' in str(fact):
        shape = 2.0 # k, >= 0
        scale = 1.0 # theta, np default, >= 0 
        
        return np.random.default_rng().gamma(shape=shape, scale=scale, size=size)
    elif 'TweedieFamily' in str(fact):
        mean = design.dataset.get_column(dv.name).mean()
        p = 1.5 # Can be changed to update to other familiar distributions: https://en.wikipedia.org/wiki/Tweedie_distribution
        phi = 20 # this can be reset
        n = size
        return tweedie.tweedie(mu=mean, p=p, phi=phi).rvs(n)
    elif 'BinomialFamily' in str(fact) and 'Negative' not in str(fact):
        n = size # number of trials  >= 0
        p = .5 # probability of success [0, 1]
        
        return np.random.default_rng().binomial(n=n, p=p, size=size)
    elif 'NegativeBinomialFamily' in str(fact):
        n = size # number of successes, > 0 
        p = .5 # probability of success [0, 1]
        
        return np.random.default_rng().negative_binomial(n=n, p=p, size=size)
    elif 'MultinomialFamily' in str(fact):
        dv = design.dv
        assert(dv.cardinality > 2)
        n = size # number of trials/experiments, > 0 
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
