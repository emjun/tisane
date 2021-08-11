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
    @classmethod
    def create_family(cls, family_name: str): 
        if family_name.upper() == "GAUSSIAN": 
            pass
    
    @abstractmethod
    def simulate_data(self): 
        pass

    # TODO: Should this be an abstract super class method? 
    # @abstractmethod
    # def generate_code(self): 
    #     pass

class AbstractLink(ABC): 
    # @abstractmethod 
    # def transform(self): 
    #     pass
    @property
    def set_variable(self, variable: AbstractVariable): 
        self.variable = variable

class IdentityLink(AbstractLink): 
    def __init__(self, variable: AbstractVariable): 
        super().set_variable(variable)
    
class GaussianFamily(AbstractFamily): 
    default_link: IdentityLink
    def simulate_data(self): 
        pass

class InverseGaussianFamily(AbstractFamily): 
    default_link: InverseSquaredLink
    def simulate_data(self): 
        pass

class GammaFamily(AbstractFamily): 
    default_link: InverseLink
    def simulate_data(self): 
        pass

class TweedieFamily(AbstractFamily):
    default_link: LogLink
    def simulate_data(self): 
        pass
    
class PoissonFamily(AbstractFamily): 
    default_link: LogLink
    def simulate_data(self):
        pass

class BinomialFamily(AbstractFamily):
    default_link: LogitLink
    def simulate_data(self):
        pass 

class NegativeBinomialFamily(AbstractFamily): 
    default_link: LogLink
    def simulate_data(self):
        pass

class MultinomialFamily(AbstractFamily): 
    default_link: LogitLink
    def simulate_data(self):
        pass