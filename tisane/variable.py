from tisane.data import Dataset, DataVector

import pandas as pd
from enum import Enum 
from typing import Any
from z3 import *


# Declare data type
Object = DeclareSort('Object')   

"""
Class for expressing (i) that there is a treatment and (ii) how there is a treatment (e.g., between-subjects, within-subjects)
Used within Class Design
"""
class Treatment(object): 
    unit: 'AbstractVariable'
    treatment: 'AbstractVariable'
    number_of_assignments: int # 1 means Between-subjects, >1 means Within-subjects
    # graph: Graph # TODO: Maybe? 

    def __init__(self, unit: 'AbstractVariable', treatment: 'AbstractVariable', number_of_assignments: int=1): 
        self.unit = unit
        self.treatment = treatment
        self.number_of_assignments = number_of_assignments

        # Maybe?
        # self.graph = Graph()
        # graph.treat(unit=unit, treatment=treatment)
        
        # TODO: Check that allocation is divisble? 
        # TODO: Assumption that treatment is categorical, not continuous? 
    
    # Default to between subjects
    def assign(self, number_of_assignments: int, unit: 'AbstractVariable'=None): 
        assert(unit is self.unit)
        self.number_of_assignments = number_of_assignments

        # TODO: Check if number_of_assignments < cardinality of treatment?

"""
Class for expressing Nesting relationship between variables (levels of independent variables in a design, statistical model)
"""
class Nest(object): 
    unit: 'AbstractVariable'
    group: 'AbstractVariable'
    # graph: Graph # TODO: Maybe? 

    def __init__(self, unit: 'AbstractVariable', group: 'AbstractVariable'): 
        self.unit = unit
        self.group = group
    
        # Maybe?
        # self.graph = Graph()
        # graph.treat(unit=unit, manipulation=manipulation)

"""
Class for expressing Repeated measures
"""
class RepeatedMeasure(object): 
    unit: 'AbstractVariable'
    response: 'AbstractVariable'
    number_of_measures: int
    # graph: Graph # TODO: Maybe? 

    def __init__(self, unit: 'AbstractVariable', response: 'AbstractVariable', number_of_measures: int): 
        self.unit = unit
        self.response = response
        self.number_of_measures = number_of_measures
    
        # Maybe?
        # self.graph = Graph()
        # graph.treat(unit=unit, manipulation=manipulation)


class AbstractVariable(object): 
    name: str 
    data : DataVector
    properties : dict
    transform : str

    const : Object # Z3 const 

    def __init__(self, name=str): 
        self.name = name
        self.const = Const(self.name, Object) # Z3 const

    # @returns True if AbstractVariable has data associated with it, False otherwise
    def hasData(self):
        return bool(self.data)

    # @return name
    def getName(self):  
        if self.data: 
            return self.data.name
        return None
    
    # @return data
    def getData(self): 
        ls = list()

        return ls

    # @param number_of_assignments indicates the number of times that the @param unit receives the treatment (self)
    # @param number_of_assignments default is 1 (between-subjects)
    # @return Treatment 
    def treat(self, unit: 'AbstractVariable', number_of_assignments: int=1) -> Treatment: 
        return Treatment(unit=unit, treatment=self, number_of_assignments=number_of_assignments)

    # @param group is the group (level 2) that self is nested under (level 1)
    # @return Nest
    def nested_under(self, group: 'AbstractVariable'): 
        return Nest(unit=self, group=group)

    # @param response is what is measured repeatedly
    # self is who/unit that provides the repeated measure
    # @return RepeatedMeasure
    def repeat(self, response: 'AbstractVariable', number_of_measures: int): 
        return RepeatedMeasure(unit=self, response=response, number_of_measures=number_of_measures)

    # Apply the @param transformation to the AbstractVariable
    def transform(self, transformation: str): 
        self.transform = transformation

    # TODO: May not need
    def assert_property(self, prop: str, val: Any) -> None: 
        key = prop.upper()
        self.properties[key] = val

    # TODO: May not need
    # Checks that the variable has the property even if not capitalized in the same way
    def has_property(self, prop: str) -> bool: 
        key = prop.upper()
        return key in self.properties.keys()

    # TODO: May not need
    def has_property_value(self, prop: str, val: Any) -> bool: 
        if self.has_property(prop):
            key = prop.upper()
            return self.properties[key] == val
        
        return False
    
    # TODO: May not need
    # @returns if variable has properties to assert
    def has_assertions(self) -> bool: 
        return bool(self.properties)

    # TODO: May not need
    # @returns variable properties
    def get_assertions(self) -> dict: 
        return self.properties


class Nominal(AbstractVariable):
    cardinality: int
    categories = list
    
    def __init__(self, name: str, data=None, **kwargs): 
        super(Nominal, self).__init__(name)
        self.data = data
        self.categories = None

        # TODO: May not need these:
        # self.properties = dict()
        # self.assert_property(prop="dtype", val="nominal")
        
        # for time being until incorporate DataVector class and methods
        if 'categories' in kwargs.keys(): 
            self.categories = kwargs['categories']
            num_categories = len(kwargs['categories'])
            assert(int(kwargs['cardinality']) == len(kwargs['categories']))
            if num_categories == 1: 
                self.assert_property(prop="cardinality", val="unary")
            elif num_categories == 2: 
                self.assert_property(prop="cardinality", val="binary")
            else: 
                assert(num_categories > 2)
                self.assert_property(prop="cardinality", val="multi")
            self.cardinality = num_categories
        
        else: 
            if 'cardinality' in kwargs: 
                self.cardinality = kwargs['cardinality'] 
            # TODO: What to do if cardinality not in kwargs?   

        # has data
        if self.data is not None: 
            num_categories = len(self.data.get_categories())
            if num_categories == 1: 
                self.assert_property(prop="cardinality", val="unary")
            elif num_categories == 2: 
                self.assert_property(prop="cardinality", val="binary")
            else: 
                assert(num_categories > 2)
                self.assert_property(prop="cardinality", val="multi")

    def __str__(self): 
        return f"NominalVariable: data:{self.data}"
    
    # @returns cardinality
    def get_cardinality(self): 
        return self.cardinality


class Ordinal(AbstractVariable): 
    cardinality: int
    ordered_cat: list

    def __init__(self, name: str, order: list=None, data=None, **kwargs): 
        super(Ordinal, self).__init__(name)
        self.ordered_cat = order
        self.data = data
        self.properties = dict()
        self.assert_property(prop="dtype", val="ordinal")

        if order is not None: 
            self.ordered_cat = order
            num_categories = len(self.ordered_cat)
            if num_categories == 1: 
                self.assert_property(prop="cardinality", val="unary")
            elif num_categories == 2: 
                self.assert_property(prop="cardinality", val="binary")
            else: 
                assert(num_categories > 2)
                self.assert_property(prop="cardinality", val="multi")
            self.cardinality = len(order)
        else: 
            if 'cardinality' in kwargs: 
                self.cardinality = kwargs['cardinality']
            # TODO: What to do if cardinality not in kwargs? 
    def __str__(self): 
        return f"OrdinalVariable: ordered_cat: {self.ordered_cat}, data:{self.data}"

    def get_cardinality(self): 
        return self.cardinality

class Numeric(AbstractVariable): 
    
    def __init__(self, name: str, data=None, **kwargs): 
        super(Numeric, self).__init__(name)
        self.data = data
        self.properties = dict()
        self.assert_property(prop="dtype", val="numeric")
    
    def __str__(self): 
        return f"NumericVariable: data:{self.data}"
    
    def get_cardinality(self): 
        # TODO: Does this make sense to do?
        raise NotImplementedError

# Wrapper around AbstractVariable class
class Variable(AbstractVariable): 
    def __init__(self, name: str): 
        super(Variable, self).__init__(name)