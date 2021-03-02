from tisane.variable import AbstractVariable
from typing import List, Union
from z3 import *
    
"""
Class for expressing Nesting relationship between variables (levels of independent variables in a design, statistical model)
"""
class Nest(object): 
    unit: AbstractVariable
    group: AbstractVariable
    # graph: Graph # TODO: Maybe? 

    def __init__(self, unit: AbstractVariable, group: AbstractVariable): 
        self.unit = unit
        self.group = group
    
        # Maybe?
        # self.graph = Graph()
        # graph.treat(unit=unit, manipulation=manipulation)

"""
Class for expressing Repeated measures
"""
class RepeatedMeasure(object): 
    unit: AbstractVariable
    response: AbstractVariable
    number_of_measures: int
    # graph: Graph # TODO: Maybe? 

    def __init__(self, unit: AbstractVariable, response: AbstractVariable, number_of_measures: int): 
        self.unit = unit
        self.response = response
        self.number_of_measures = number_of_measures
    
        # Maybe?
        # self.graph = Graph()
        # graph.treat(unit=unit, manipulation=manipulation)