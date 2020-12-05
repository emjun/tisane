from tisane.concept import Concept
from tisane.variable import AbstractVariable, NominalVariable, OrdinalVariable, NumericVariable

from typing import Any, Dict, List, Union
from collections import namedtuple

from scipy import stats # Stats library used

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

class StatisticalTestResult(object): 
    name: str
    test_statistic_name: str
    test_statistic_value: float
    p_value: float 

    def __init__(self, name: str, test_statistic_name: str, test_statistic_value: float, p_value: float): 
        self.name = name
        self.test_statistic_name = test_statistic_name
        self.test_statistic_value = test_statistic_value
        self.p_value = p_value


# Pass lists to keep the signatures consistent
numeric_dv = None
not_multicollinearity = None
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

residual_normal_distribution = None
def check_normal_distribution(vars: list): 
    assert(len(vars) == 1) 
    var = vars[0]
    # Must be continuous to be normally distributed
    assert(check_numeric_type(vars))
    
    # Get data
    # TODO: What happens if don't have data!
    data = None
    if isinstance(var, Concept): 
        data = var.variable.data() 
        
        # FOR DEBUGGING: 
        if not data: 
            return True
    # TODO: what happens if we have residuals??
    # elif isinstance(var, Num): 
    #     pass
    else: 
        raise NotImplementedError

    w, p_val = stats.shapiro(data)
    
    st_res = StatisticalTestResult(name='Shapiro-Wilk test for Normality', test_statistic_name='W', test_statistic_value=w, p_value=p_val)
    
    return interpret(st_res)

homoscedasticity = None
def check_homoscedasticity(ivs: list, dvs: list): 
    # TODO: figure out homoscedasticity
    
    return True


# @param tolerance for lower and upper bound for interpreting results of tests checking for properties
def interpret(st_res: StatisticalTestResult): 
    return True
    
    # Check that the statistical result is with a tolerance range and then return result based on the allowed tolerance
    return st_res.p_value < 0.05 # Would need access to user-defined .05, Could also use range of values instead of p_value?

def initialize_all_properties(ivs: list, dvs: list): 
    global numeric_dv, check_numeric_type, \
           residual_normal_distribution, check_normal_distribution

    numeric_dv = Property(name='Numeric DV', description='DV is numeric data type', method=check_numeric_type, variables=dvs)

    # TODO: calculate residuals
    residuals = dvs
    residual_normal_distribution = Property(name='Normal Distribution', description='Variable is normally distributed', method=check_normal_distribution, variables=residuals)
    
    return {'numeric_dv': numeric_dv, 
            'residual_normal_distribution': residual_normal_distribution}

def destruct_all_properties(): 
    global numeric_dv, residual_normal_distribution

    numeric_dv = None
    residual_normal_distribution = None

"""
Need a way to look up what the variables are for each list of variables (in each property)
Alternative: 
def dv(ivs: list, dvs: list): 
    return dvs

numeric_dv = Property(name='Numeric DV', description='DV is numeric data type', method=None, variables=dv())
"""