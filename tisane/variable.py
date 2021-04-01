from tisane.data import Dataset, DataVector

import pandas as pd
from enum import Enum 
from typing import Any, List, Union
import typing
from z3 import *


# Declare data type
Object = DeclareSort('Object')   

"""
Class for expressing (i) that there is a treatment and (ii) how there is a treatment (e.g., between-subjects, within-subjects)
Used within Class Design
"""
class Treatment(object): 
    treatment: 'AbstractVariable'
    unit: 'AbstractVariable'
    num_assignments: int # 1 means Between-subjects, >1 means Within-subjects
    # graph: Graph # TODO: Maybe? 

    def __init__(self, treatment: 'AbstractVariable', unit: 'AbstractVariable', num_assignments: int):
        self.treatment = treatment
        self.unit = unit
        self.num_assignments = num_assignments

        # TODO: Check that allocation is divisble? 
        # TODO: Assumption that treatment is categorical, not continuous? 
    
    # # Default to between subjects
    # def assign(self, number_of_assignments: int, unit: 'AbstractVariable'=None): 
    #     assert(unit is self.unit)
    #     self.number_of_assignments = number_of_assignments

    #     # TODO: Check if number_of_assignments < cardinality of treatment?

"""
Class for expressing Nesting relationship between variables (levels of independent variables in a design, statistical model)
"""
class Nest(object): 
    base: 'AbstractVariable'
    group: 'AbstractVariable'
    # graph: Graph # TODO: Maybe? 

    def __init__(self, base: 'AbstractVariable', group: 'AbstractVariable'): 
        self.base = base
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
    repetitions: 'AbstractVariable'
    # count_variable: 'AbstractVariable'
    # repetitions: int
    # graph: Graph # TODO: Maybe? 

    def __init__(self, unit: 'AbstractVariable', response: 'AbstractVariable', repetitions: 'AbstractVariable'): #, repetitions: int): 
        self.unit = unit
        self.response = response
        self.repetitions = repetitions
        # self.repetitions = repetitions
        # self.repetitions = self.count_variable.cardinality

"""
Class for Cause relationships
"""
class Cause(object):
    cause: 'AbstractVariable'
    effect: 'AbstractVariable'

    def __init__(self, cause: 'AbstractVariable', effect: 'AbstractVariable'):
        self.cause = cause
        self.effect = effect

"""
Class for Associate relationships
"""
class Associate(object):
    lhs: 'AbstractVariable'
    rhs: 'AbstractVariable'

    def __init__(self, lhs: 'AbstractVariable', rhs: 'AbstractVariable'):
        self.lhs = lhs
        self.rhs = rhs

"""
Class for Has relationships
"""
class Has(object):
    variable: 'AbstractVariable'
    measure: 'AbstractVariable'
    repetitions: int
    # repetitions: 'AbstractVariable'

    # Default is between subjects, only once
    def __init__(self, variable: 'AbstractVariable', measure: 'AbstractVariable', repetitions: int):
        self.variable = variable
        self.measure = measure
        self.repetitions = repetitions

class AbstractVariable(object): 
    name: str 
    data : DataVector
    properties : dict
    transform : str
    relationships: List[typing.Union[Associate, Cause, Has, Nest, Treatment, RepeatedMeasure]]

    const : Object # Z3 const 

    def __init__(self, name=str): 
        self.name = name
        self.const = Const(self.name, Object) # Z3 const

        self.relationships = list()

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

    def has(self, measure: 'AbstractVariable', **kwargs):
        if 'repetitions' in kwargs:
            rep = int(kwargs['repetitions'])
            if rep > 1: 
                self.has_multiple(measure=measure, repetitions=rep)
            else: 
                self.has_unique(measure=measure)    
        else: 
            self.has_unique(measure=measure)

    # Update both variables
    def has_unique(self, measure: 'AbstractVariable'):
        has_relat = Has(variable=self, measure=measure, repetitions=1)
        self.relationships.append(has_relat)
        measure.relationships.append(has_relat)
    
    # Update both variables
    def has_multiple(self, measure: 'AbstractVariable', repetitions: int): 
        has_relat = Has(variable=self, measure=measure, repetitions=repetitions)
        self.relationships.append(has_relat)
        measure.relationships.append(has_relat)

    # @param associated with this variable
    def _associate(self, rhs: 'AbstractVariable'):
        assoc = Associate(lhs=self, rhs=rhs)
        self.relationships.append(assoc)
    
    def associates_with(self, variable: 'AbstractVariable'):
        # Update both variables
        self._associate(variable)
        
        variable._associate(self)

    # @param number_of_assignments indicates the number of times that the @param unit receives the treatment (self)
    # @param number_of_assignments default is 1 (between-subjects)
    # @return Treatment 
    def treat(self, variable: 'AbstractVariable', **kwargs): #, repetitions: int=None): 
        rep = None
        if 'assignment' in kwargs: 
            assign = kwargs['assignment']
            if assign.upper() == 'BETWEEN':
                # TODO: check? 
                rep = 1
            elif assign.upper() == 'WITHIN': 
                # TODO: check? 
                rep = self.cardinality
            else: 
                raise ValueError(f"Invalid description of how {self.name} treats {variable.name} in terms of assignment: {assign}! Accepted values: BETWEEEN or WITHIN.")
        elif 'num_assignments' in kwargs: 
            assign = int(kwargs['num_assignments'])
            # Between subjects? 
            if assign == 1: 
                rep = 1
            # Full within-subjects design? 
            elif assign == self.cardinality: 
                rep = self.cardinality 
            # Partial within-subjects design
            else: 
                if assign < cardinality: 
                    rep = assign 
                else: 
                    raise ValueError(f"Invalid number of assignments of {self.name} to {variable.name}. Specified number of assignments ({assign}) is greater than cardinality of {self.name} ({self.cardinality})")
            
        variable.has(measure=self, repetitions=rep)
        treatment = Treatment(treatment=self, unit=variable, num_assignments=rep)
        self.relationships.append(treatment)
        variable.relationships.append(treatment)
        
        # if repetitions is not None:
        #     variable.has(measure=self, repetitions=self.cardinality)
        # else: 
        #     variable.has(measure=self)

    def treats(self, variable: 'AbstractVariable', **kwargs): # repetitions: int=None): 
        self.treat(variable, kwargs)

    # @param group is the group (level 2) that self is nested under (level 1)
    # Add nested relationships to this variable
    def nest_under(self, group: 'AbstractVariable'): 
        # Update both variables
        nest_relat = Nest(base=self, group=group)
        self.relationships.append(nest_relat)
        group.relationships.append(nest_relat)
        # return Nest(unit=self, group=group)
    
    # Provide alternative that might read nicer grammatically
    def nests_under(self, group: 'AbstractVariable'): 
        self.nest_under(group)

    # @param response is what is measured repeatedly
    # self is who/unit that provides the repeated measure
    # @return RepeatedMeasure
    def repeat(self, response: 'AbstractVariable', according_to: 'AbstractVariable'): 
        repeat_relat = RepeatedMeasure(unit=self, response=response, according_to=according_to)
        
    
    def repeats(self, response: 'AbstractVariable', according_to: 'AbstractVariable'):
        return RepeatedMeasure(unit=self, response=response, according_to=according_to)

    # @param effect the variable causes
    def cause(self, effect: 'AbstractVariable'):
        # Update both variables
        cause_relat = Cause(cause=self, effect=effect)
        self.relationships.append(cause_relat)
        effect.relationships.append(cause_relat)

    # Provide multiple function names for 'CAUSE' that might read more correctly 
    def causes(self, effect: 'AbstractVariable'): 
        self.cause(effect=effect)
        
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
            if 'cardinality' in kwargs.keys(): 
                self.cardinality = kwargs['cardinality'] 
            else: 
                self.cardinality = None

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
        raise NotImplementedError

class Count(AbstractVariable): 
    def __init(self, name: str, data=None, **kwargs): 
        super(Count, self).__init__(name)
        self.data = data 

class Time(AbstractVariable): 
    def __init(self, name: str, data=None, **kwargs): 
        super(Time, self).__init__(name)
        self.data = data 


class Unit(Nominal):
    def __init__(self, name: str):
        super(Unit, self).__init__(name)

# Wrapper around AbstractVariable class
class Variable(AbstractVariable): 
    def __init__(self, name: str): 
        super(Variable, self).__init__(name)