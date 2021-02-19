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
MainEffect = Function('MainEffect', Object, Object, BoolSort())
NoMainEffect = Function('NoMainEffect', Object, Object, BoolSort())
Interaction = Function('Interaction', Object, Object, BoolSort())
NoInteraction = Function('NoInteraction', Object, Object, BoolSort())

# Variable Relationship Graph
Cause = Function('Cause', Object, Object, BoolSort())
Correlate = Function('Correlate', Object, Object, BoolSort())

# Data schema, data type
BinaryDataType = Function('BinaryDataType', Object, BoolSort())
MultinomialDataType = Function('MultinomialDataType', Object, BoolSort())
NominalDataType = Function('NominalDataType', Object, BoolSort())
OrdinalDataType = Function('OrdinalDataType', Object, BoolSort())
CategoricalDataType = Function('CategoricalDataType', Object, BoolSort())
NumericDataType = Function('NumericDataType', Object, BoolSort())

# Data transformations, link functions
Transformation = Function('Transformation', Object, BoolSort())
NoTransformation = Function('NoTransformation', Object, BoolSort())
NumericTransformation = Function('NumericTransformation', Object, BoolSort())
CategoricalTransformation = Function('CategoricalTransformation', Object, BoolSort())
IdentityTransform = Function('IdentityTransform', Object, BoolSort())
LogTransform = Function('LogTransform', Object, BoolSort())
SquarerootTransform = Function('SquarerootTransform', Object, BoolSort())
LogLogTransform = Function('LogLogTransform', Object, BoolSort())
ProbitTransform = Function('ProbitTransform', Object, BoolSort())
LogitTransform = Function('LogitTransform', Object, BoolSort())

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