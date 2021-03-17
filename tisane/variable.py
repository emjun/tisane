import pandas as pd

from enum import Enum 
from typing import Any

class Dataset(object): 
    data_vectors: dict


class DataVector(object): 
    name: str
    values: pd.DataFrame 

    # def __init__(self, name: str, values: pd.DataFrame): 
    #     self.name = name
    #     self.values = values

    def get_cardinality(self): 
        pass
     

class AbstractVariable(object): 
    data : DataVector
    properties : dict

    @classmethod
    def create(cls, **kwargs):
        """
        Creates a Variable according to type of data
        """

        if "dtype" in kwargs.keys(): 
            dtype = kwargs["dtype"].upper()

            if dtype == 'NOMINAL': 
                # remove item from kwargs
                return NominalVariable(**kwargs)
            elif dtype == 'ORDINAL': 
                return OrdinalVariable(**kwargs)
            elif dtype == 'NUMERIC': 
                return NumericVariable(**kwargs)
            else: 
                raise ValueError(f"Data type {dtype} not supported! Try NOMINAL, ORDINAL, or NUMERIC")
                
        else: 
            raise ValueError(f"Please specify a data type for the Concept! Try NOMINAL, ORDINAL, or NUMERIC")
    
    def getData(self): 
        ls = list()

        return ls
    
    def hasData(self):
        return bool(self.data)

    def getName(self):
        if self.data: 
            return self.data.name
        return None

    def assert_property(self, prop: str, val: Any) -> None: 
        key = prop.upper()
        self.properties[key] = val

    # Checks that the variable has the property even if not capitalized in the same way
    def has_property(self, prop: str) -> bool: 
        key = prop.upper()
        return key in self.properties.keys()

    def has_property_value(self, prop: str, val: Any) -> bool: 
        if self.has_property(prop):
            key = prop.upper()
            return self.properties[key] == val
        
        return False
    
    # @returns if variable has properties to assert
    def has_assertions(self) -> bool: 
        return bool(self.properties)

    # @returns variable properties
    def get_assertions(self) -> dict: 
        return self.properties

class NominalVariable(AbstractVariable): 
    # categories = list
    
    def __init__(self, data=None, **kwargs): 
        # self.categories = cat_list
        self.data = data
        self.properties = dict()
        self.assert_property(prop="dtype", val="nominal")
        
        # for time being until incorporate DataVector class and methods
        if 'categories' in kwargs.keys(): 
            num_categories = len(kwargs['categories'])
            if num_categories == 1: 
                self.assert_property(prop="cardinality", val="unary")
            elif num_categories == 2: 
                self.assert_property(prop="cardinality", val="binary")
            else: 
                assert(num_categories > 2)
                self.assert_property(prop="cardinality", val="multi")

        # has data
        if self.data: 
            num_categories = len(self.data.get_categories())
            if num_categories == 1: 
                self.assert_property(prop="cardinality", val="unary")
            elif num_categories == 2: 
                self.assert_property(prop="cardinality", val="binary")
            else: 
                assert(num_categories > 2)
                self.assert_property(prop="cardinality", val="multi")
    # def __repr__(self): 
    #     return f"NominalVariable: data:{self.data}"
    def __str__(self): 
        return f"NominalVariable: data:{self.data}"

class OrdinalVariable(AbstractVariable): 
    # categories = list
    ordered_cat = list
    
    def __init__(self, order: list=None, data=None, **kwargs): 
        # self.categories = cat_list
        self.ordered_cat = order
        self.data = data
        self.properties = dict()
        self.assert_property(prop="dtype", val="ordinal")

        num_categories = len(self.ordered_cat)
        if num_categories == 1: 
            self.assert_property(prop="cardinality", val="unary")
        elif num_categories == 2: 
            self.assert_property(prop="cardinality", val="binary")
        else: 
            assert(num_categories > 2)
            self.assert_property(prop="cardinality", val="multi")
    # def __repr__(self): 
    #     return f"OrdinalVariable: ordered_cat: {self.ordered_cat}, data:{self.data}"
    def __str__(self): 
        return f"OrdinalVariable: ordered_cat: {self.ordered_cat}, data:{self.data}"


class NumericVariable(AbstractVariable): 
    
    def __init__(self, data=None, **kwargs): 
        self.data = data
        self.properties = dict()
        self.assert_property(prop="dtype", val="numeric")
    # def __repr__(self): 
    #     return f"NumericVariable: data:{self.data}"
    def __str__(self): 
        return f"NumericVariable: data:{self.data}"
