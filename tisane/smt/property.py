from tisane.concept import Concept
from tisane.variable import AbstractVariable, NominalVariable, OrdinalVariable, NumericVariable

from typing import Any

# tolerances
# weights
# TODO: each property should be able to verify itself
# TODO: should be able to provide some threshold for verifying each property

class Property(object):    
    name: str
    variables: list # variables to apply this property to
    description: str # description about this property 
    method: Any # TODO: should be a function type

    # @method must be a function that returns True if the property holds and False otherwise
    def __init__(self, name: str, description: str, method: Any, **kwargs): 
        self.name = name
        self.description = description 
        self.method = method

        assert(kwargs['variables'])
        variables = kwargs['variables']
        self.variables = variables 
    
    def verify(self) -> bool: 
        return self.method(self.variables)


# Pass lists to keep the signatures consistent
numeric_dv = None
# TODO Should we rename "vars" to be "cons"??
def check_var_type(vars: list, var_type: AbstractVariable): 
    assert(len(vars) == 1) # There is only one variable in the list of @param vars
    var = vars[0]
    assert(isinstance(var, Concept))
    return isinstance(var.variable, var_type)

def check_nominal_type(vars: list): 
    return check_var_type(vars, NominalVariable)

def check_ordinal_type(vars: list): 
    return check_var_type(vars, OrdinalVariable)

def check_numeric_type(vars: list): 
    return check_var_type(vars, NumericVariable)


def initialize_all_properties(ivs: list, dvs: list): 
    global numeric_dv, check_numeric_type

    numeric_dv = Property(name='Numeric DV', description='DV is numeric data type', method=check_numeric_type, variables=dvs)
    
    return {'numeric_dv': numeric_dv}

def destruct_all_properties(): 
    global numeric_dv

    numeric_dv = None

"""
Need a way to look up what the variables are for each list of variables (in each property)
Alternative: 
def dv(ivs: list, dvs: list): 
    return dvs

numeric_dv = Property(name='Numeric DV', description='DV is numeric data type', method=None, variables=dv())
"""