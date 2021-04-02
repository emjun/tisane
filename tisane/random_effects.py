from tisane.variable import AbstractVariable, Nominal, Ordinal, Numeric

from typing import Union

class RandomEffect(object):
    groups: AbstractVariable
    # The _iv_ is allowed to vary per each group in _groups_

class RandomSlope(RandomEffect):
    iv: Union[AbstractVariable, int]
    def __init__(self, iv: Union[AbstractVariable, int], groups: AbstractVariable): 
        # Check if @param iv is 1? (meaning intercept)
        self.iv = iv
        self.groups = groups

class RandomIntercept(RandomEffect): 
    def __init__(self, groups: Union[AbstractVariable, int]):
        # Check if @param iv is 1? (meaning intercept)
        self.groups = groups
        
# By default, random slope and intercept are assumed to not be correlated?
class CorrelatedRandomSlopeAndIntercept(RandomEffect): 
    random_slope: RandomSlope
    random_intercept: RandomIntercept

    def __init__(self, iv: Union[AbstractVariable, int], groups: AbstractVariable): 
        self.random_slope = RandomSlope(iv=iv, groups=groups)
        self.random_intercept = RandomIntercept(iv=iv, groups=groups)

class UncorrelatedRandomSlopeandIntercept(RandomEffect): 
    random_slope: RandomSlope
    random_intercept: RandomIntercept

    def __init__(self, iv: Union[AbstractVariable, int], groups: AbstractVariable): 
        self.random_slope = RandomSlope(iv=iv, groups=groups)
        self.random_intercept = RandomIntercept(iv=iv, groups=groups)
    
    