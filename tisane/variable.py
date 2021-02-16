import pandas as pd

from enum import Enum 
from typing import Any
# class DTYPE(Enum): 
#     NOMINAL = 1
#     ORDINAL = 2
#     NUMERIC = 3
    
#     @classmethod
#     def createDTYPE(self, type_str:str): 
#         if type_str.upper() == 'NOMINAL':
#             return DTYPE.NOMINAL
#         elif type_str.upper() == 'ORDINAL': 
#             return DTYPE.ORDINAL
#         elif type_str.upper() == "NUMERIC": 
#             return DTYPE.NUMERIC
#         else: 
#             raise ValueError(f"Data type {type_str} not supported! Try NOMINAL, ORDINAL, or NUMERIC")

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
    name: str 
    data : DataVector
    properties : dict

    def __init__(self, name=str): 
        self.name = name

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

class Nominal(AbstractVariable): 
    # categories = list
    cardinality: int
    
    def __init__(self, name: str, data=None, **kwargs): 
        # self.categories = cat_list
        super(Nominal, self).__init__(name)
        self.data = data
        self.properties = dict()
        self.assert_property(prop="dtype", val="nominal")
        
        # for time being until incorporate DataVector class and methods
        if 'categories' in kwargs.keys(): 
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
        
        self.cardinality = kwargs['cardinality']

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
    # def __repr__(self): 
    #     return f"NominalVariable: data:{self.data}"
    def __str__(self): 
        return f"NominalVariable: data:{self.data}"

class Ordinal(AbstractVariable): 
    # categories = list
    ordered_cat = list
    
    def __init__(self, name: str, order: list=None, data=None, **kwargs): 
        super(Ordinal, self).__init__(name)
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


class Numeric(AbstractVariable): 
    
    def __init__(self, name: str, data=None, **kwargs): 
        super(Numeric, self).__init__(name)
        self.data = data
        self.properties = dict()
        self.assert_property(prop="dtype", val="numeric")
    # def __repr__(self): 
    #     return f"NumericVariable: data:{self.data}"
    def __str__(self): 
        return f"NumericVariable: data:{self.data}"

# Wrapper around AbstractVariable class
class Variable(AbstractVariable): 
    def __init__(self, name: str): 
        super(Variable, self).__init__(name)

