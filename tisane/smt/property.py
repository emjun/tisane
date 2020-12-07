from tisane.concept import Concept
from tisane.variable import AbstractVariable, NominalVariable, OrdinalVariable, NumericVariable
from tisane.smt.results import StatisticalTestResult
from tisane.smt.statistical_variable import StatVar

from typing import Any, Dict, List, Union
from collections import namedtuple

from scipy import stats # Stats library used
import z3

# tolerances
# weights
# TODO: each property should be able to verify itself
# TODO: should be able to provide some threshold for verifying each property

class Property(object):    
    name: str
    # variables: list # variables to apply this property to
    description: str # description about this property 
    method: Any # TODO: should be a function type
    __z3__: z3.BoolSort

    # @method must be a function that returns True if the property holds and False otherwise
    def __init__(self, name: str, description: str, method: Any, arity=3, **kwargs): 
        self.name = name
        self.description = description 
        self.method = method
        self.arity = arity # TODO: update this!

        # assert('variables' in kwargs)
        # variables = kwargs['variables']
        # self.variables = variables 

        z3_args = list()
        for _ in range(self.arity):
            z3_args.append(z3.BoolSort())
        z3_args.append(z3.BoolSort())
        # import pdb; pdb.set_trace()
        self.__z3__ = z3.Function(self.name, *z3_args)  # e.g. continuous(x)
        
        # self.__cache__ = {}
    
    # def __apply__(self): 
    #     self.properties = prop.__z3__(*z3_args)

    def __str__(self):
        return f"Property:{self.name}"

    def __repr__(self):
        return f"Property({self.name})"

    def __eq__(self, other):
    
        return self.arity == self.arity and self.name == other.name and self.method == other.method

    def __hash__(self):
        return hash((self.name, self.method))
    
    def __call__(self, *var_names):
        # import pdb; pdb.set_trace()
        # if len(var_names) != self.arity:
        #     raise Exception(f"{self.name} property has arity {self.arity} " \
        #                     f"found {len(var_names)} arguments")
        # cached = self.__cache__.get(tuple(var_names))
        # if cached:
            # return cached
        
        ap = AppliedProperty(self, var_names)
        # self.__cache__[tuple(var_names)] = ap
        return ap

    # Only used when the property must be changed depending on input data
    def _update(self, arity):
        self.arity = arity
        self.reset()

    def reset(self):
        args = []
        for _ in range(self.arity):
            args.append(z3.BoolSort())
        args.append(z3.BoolSort())
        self.__z3__ = z3.Function(self.name, *args)  # e.g. continuous(x)
    
    # def query(self): 
    #     args = list()
    #     for v in self.variables: 
    #         args.append(v)
    #     args.append(z3.BoolSort()) 
    #     self.__z3__ = z3.Function(self.name, *args)  # e.g. continuous(x)

    #     return self.__z3__

    # TODO: May not need to store verification result
    def verify(self): 
        
        is_satisfied = self.method(self.variables)
        self.__z3__ = z3.BoolVal(is_satisfied)

        return self.__z3__

class AppliedProperty(object):    
    property: Property

    def __init__(self, prop, pvars):
        # global __property_var_map__
        self.property = prop  # e.g. continuous
        self.vars = pvars  
        z3_args = []
        for tv in pvars:
            # Allows for unique identification of prop -> var, but not looking up from model because that refs prop name
            z3_args.append(tv.__z3__)
        self._name = self.property.name  # "continuous"
        self.__z3__ = prop.__z3__(*z3_args)  # e.g. continuous(x)

        # if self._name not in __property_var_map__.keys():
        #     __property_var_map__[self._name] = []

        # # TODO: When does __property_var_map__ need to be cleared?
        # __property_var_map__[self._name].append(self.vars)

        self.property_test_results = None

    def __str__(self):
        return f"property_for_var:{self._name}"

    def __repr__(self):
        return f"AppliedProperty({self._name})"
    
    def __eq__(self, other):
        return self.property == other.property and self.vars == other.vars

    # @staticmethod
    # def get_by_z3_var(name):
    #     global __property_var_map__
    #     return __property_var_map__.get(name)


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

normal_distribution_residuals = None
def check_normal_distribution(vars: list): 
    assert(len(vars) == 1) 
    var = vars[0]
    # Must be cont
    # umeric_type(vars))
    
    # Get data
    # TODO: What happens if don't have data!
    data = None
    if isinstance(var, Concept): 
        data = var.getVariable().getData() 
        
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

not_multicollinearity_ivs = None
def check_not_multicollinearity(ivs: list, dvs: list):
    return True

# @param tolerance for lower and upper bound for interpreting results of tests checking for properties
def interpret(st_res: StatisticalTestResult): 
    return True
    
    # Check that the statistical result is with a tolerance range and then return result based on the allowed tolerance
    return st_res.p_value < 0.05 # Would need access to user-defined .05, Could also use range of values instead of p_value?

def initialize_all_properties(sv_ivs: List[StatVar], sv_dvs: List[StatVar]): 
    global numeric_dv, check_numeric_type, residual_normal_distribution, check_normal_distribution, homoscedasticity, check_homoscedasticty, not_multicollinearity, check_not_multicollinearity
    
    numeric_dv = Property(name='Numeric DV', description='DV is numeric data type', method=check_numeric_type, variables=sv_dvs)
    not_multicollinearity_ivs = Property(name='Absence of Multicollinearity', description='IVs are not multicollinear', method=check_not_multicollinearity, variables=sv_ivs)

    # TODO: calculate residuals
    residuals = sv_dvs
    normal_distribution_residuals = Property(name='Normal Distribution', description='Variable is normally distributed', method=check_normal_distribution, variables=residuals)
    homoscedastic_residuals = Property(name='Homoscedasticity', description='Variable/Residual is homoscedastic', method=check_homoscedasticity, variables=residuals)
    
    return {'numeric_dv': numeric_dv, 
            'not_multicollinearity_ivs': not_multicollinearity_ivs,
            'normal_distribution_residuals': normal_distribution_residuals,
            'homoscedastic_residuals': homoscedastic_residuals}

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