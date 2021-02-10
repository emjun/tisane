from z3 import *
from typing import Dict, Any, Union


# Global Z3 free variables and functions
# Data type
Object = DeclareSort('Object')
# Free variables 
x = Const('x', Object)
x0 = Const('x0', Object)
x1 = Const('x1', Object)
i = Const('x1', SetSort(Object))

# Model explanation
Explains = Function('Explains', Object, SeqSort(Object), BoolSort())
Models = Function('Models', Object, SeqSort(Object), BoolSort())
Dependent = Function('Dependent', Object, BoolSort())
MainEffect = Function('MainEffect', Object, BoolSort())
Interaction = Function('Interaction', Object, Object, BoolSort())

# Variable Relationship Graph
Cause = Function('Cause', Object, Object, BoolSort())
Correlate = Function('Correlate', Object, Object, BoolSort())

# Data schema, data type
Binary = Function('Binary', Object, BoolSort())
Multinomial = Function('Multinomial', Object, BoolSort())
Nominal = Function('Nominal', Object, BoolSort())
Ordinal = Function('Ordinal', Object, BoolSort())
Categorical = Function('Categorical', Object, BoolSort())
Numeric = Function('Numeric', Object, BoolSort())

# Data transformations, link functions
Identity = Function('Identity', Object, BoolSort())
Log = Function('Log', Object, BoolSort())
Sqrt = Function('Sqrt', Object, BoolSort())
LogLog = Function('LogLog', Object, BoolSort())
Probit = Function('Probit', Object, BoolSort())
Logit = Function('Logit', Object, BoolSort())

# Variance functions
Gaussian = Function('Gaussian', Object, BoolSort())
Inverse_Gaussian = Function('Inverse_Gaussian', Object, BoolSort())
Binomial = Function('Binomial', Object, BoolSort())
Multinomial = Function('Multinomial', Object, BoolSort())


# Template facts
# template_graph_facts = [
#     Cause(x, y), 
#     Correlate(x, y)
# ]