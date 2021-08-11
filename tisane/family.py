from abc import ABC, abstractmethod
from os import PRIO_PGRP
from tisane.og_variable import AbstractVariable
from tisane.data import Dataset, DataVector
from typing import Any, List
import typing  # for typing.Unit

"""
Abstract super class for all family functions. 
"""
class AbstractFamily(ABC): 
    variable: AbstractVariable

    @abstractmethod
    def simulate_data(self): 
        pass

    def set_link(self, link: "AbstractLink"):
        self.link = link

    # TODO: Should this be an abstract super class method? 
    # @abstractmethod
    # def generate_code(self): 
    #     pass

class AbstractLink(): 
    # @abstractmethod 
    # def transform(self): 
    #     pass
    variable: AbstractVariable

    def set_variable(self, variable: AbstractVariable): 
        self.variable = variable

class IdentityLink(AbstractLink): 
    def __init__(self, variable: AbstractVariable): 
        super().set_variable(variable)
    
    def set_variable(self, variable: AbstractVariable):
        super().set_variable(variable)

class InverseLink(AbstractLink): 
    def __init__(self, variable: AbstractVariable): 
        super().set_variable(variable)

class InverseSquaredLink(AbstractLink): 
    def __init__(self, variable: AbstractVariable): 
        super().set_variable(variable)

class LogLink(AbstractLink): 
    def __init__(self, variable: AbstractVariable): 
        super().set_variable(variable)

class LogitLink(AbstractLink): 
    def __init__(self, variable: AbstractVariable): 
        super().set_variable(variable)

class ProbitLink(AbstractLink): 
    def __init__(self, variable: AbstractVariable): 
        super().set_variable(variable)

class CLogLogLink(AbstractLink): 
    def __init__(self, variable: AbstractVariable): 
        super().set_variable(variable)

class PowerLink(AbstractLink): 
    def __init__(self, variable: AbstractVariable): 
        super().set_variable(variable)

class OPowerLink(AbstractLink): 
    def __init__(self, variable: AbstractVariable): 
        super().set_variable(variable)

class NegativeBinomialLink(AbstractLink): 
    def __init__(self, variable: AbstractVariable): 
        super().set_variable(variable)

class LogLogLink(AbstractLink): 
    def __init__(self, variable: AbstractVariable): 
        super().set_variable(variable)

class GaussianFamily(AbstractFamily): 

    def __init__(self, variable: AbstractVariable):
        self.link = IdentityLink(variable)

    def simulate_data(self): 
        pass

class InverseGaussianFamily(AbstractFamily): 

    def __init__(self, variable: AbstractVariable):
        self.link = InverseSquaredLink(variable)

    def simulate_data(self): 
        pass

class GammaFamily(AbstractFamily): 
    
    def __init__(self, variable: AbstractVariable):
        self.link = InverseLink(variable)

    def simulate_data(self): 
        pass

class TweedieFamily(AbstractFamily):
    
    def __init__(self, variable: AbstractVariable):
        self.link = LogLink(variable)
    
    def simulate_data(self): 
        pass
    
class PoissonFamily(AbstractFamily): 

    def __init__(self, variable: AbstractVariable):
        self.link = LogLink(variable)

    def simulate_data(self):
        pass

class BinomialFamily(AbstractFamily):

    def __init__(self, variable: AbstractVariable):
        self.link = LogitLink(variable)

    def simulate_data(self):
        pass 

class NegativeBinomialFamily(AbstractFamily): 

    def __init__(self, variable: AbstractVariable):
        self.link = LogLink(variable)

    def simulate_data(self):
        pass

class MultinomialFamily(AbstractFamily): 
    
    def __init__(self, variable: AbstractVariable):
        self.link = LogitLink(variable)

    def simulate_data(self):
        pass