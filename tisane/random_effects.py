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
    groups: AbstractVariable # Each group can have a different random intercept
    iv: AbstractVariable # Each group in groups is allowed to have a different slope along iv (random slope)

    def __init__(self, iv: Union[AbstractVariable, int], groups: AbstractVariable): 
        self.groups = groups
        self.iv = iv

class UncorrelatedRandomSlopeAndIntercept(RandomEffect): 
    groups: AbstractVariable # Each group can have a different random intercept
    iv: AbstractVariable # Each group in groups is allowed to have a different slope along iv (random slope)

    def __init__(self, iv: Union[AbstractVariable, int], groups: AbstractVariable): 
        self.groups = groups
        self.iv = iv
    
    