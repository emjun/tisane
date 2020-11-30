import pandas as pd

# from enum import Enum 
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

class AbstractVariable(object): 
    data : pd.DataFrame 

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

class NominalVariable(AbstractVariable): 
    # categories = list
    
    def __init__(self, data=None, **kwargs): 
        # self.categories = cat_list
        self.data = data
    def __repr__(self): 
        return f"NominalVariable: data:{self.data}"
    def __str__(self): 
        raise NotImplementedError

class OrdinalVariable(AbstractVariable): 
    # categories = list
    ordered_cat = list
    
    def __init__(self, order: list=None, data=None, **kwargs): 
        # self.categories = cat_list
        self.ordered_cat = order
        self.data = data
    def __repr__(self): 
        return f"OrdinalVariable: ordered_cat: {self.ordered_cat}, data:{self.data}"
    def __str__(self): 
        raise NotImplementedError

class NumericVariable(AbstractVariable): 
    
    def __init__(self, data=None, **kwargs): 
        self.data = data
    def __repr__(self): 
        return f"NumericVariable: data:{self.data}"
    def __str__(self): 
        raise NotImplementedError
