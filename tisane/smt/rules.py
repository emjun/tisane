from z3 import *
from typing import Dict, Any, Union


# Global Z3 free variables and functions
# Data type
Object = DeclareSort("Object")
# Free variables
x = Const("x", Object)
x0 = Const("x0", Object)
x1 = Const("x1", Object)
xs = Const("xs", SetSort(Object))
i = Const("i", SetSort(Object))

# Model explanation
Explains = Function("Explains", Object, SeqSort(Object), BoolSort())
Models = Function("Models", Object, SeqSort(Object), BoolSort())
Dependent = Function("Dependent", Object, BoolSort())
FixedEffect = Function("FixedEffect", Object, Object, BoolSort())
NoFixedEffect = Function("NoFixedEffect", Object, Object, BoolSort())
Interaction = Function("Interaction", SetSort(Object), BoolSort())
NoInteraction = Function("NoInteraction", SetSort(Object), BoolSort())
RandomSlopeEffect = Function("RandomSlopeEffect", Object, Object, BoolSort())
NoRandomSlopeEffect = Function("NoRandomSlopeEffect", Object, Object, BoolSort())
RandomInterceptEffect = Function("RandomInterceptEffect", Object, BoolSort())
NoRandomInterceptEffect = Function("NoRandomInterceptEffect", Object, BoolSort())
CorrelatedRandomSlopeInterceptEffects = Function(
    "CorrelatedRandomSlopeInterceptEffects", Object, Object, BoolSort()
)
UncorrelatedRandomSlopeInterceptEffects = Function(
    "UncorrelatedRandomSlopeInterceptEffects", Object, Object, BoolSort()
)

# TODO: Remove
MainEffect = Function("MainEffect", Object, Object, BoolSort())
NoMainEffect = Function("NoMainEffect", Object, Object, BoolSort())

# Variable Relationship Graph
# Cause = Function('Cause', Object, Object, BoolSort())
# Correlate = Function('Correlate', Object, Object, BoolSort())

# Data schema, data type
BinaryDataType = Function("BinaryDataType", Object, BoolSort())
MultinomialDataType = Function("MultinomialDataType", Object, BoolSort())
NominalDataType = Function("NominalDataType", Object, BoolSort())
OrdinalDataType = Function("OrdinalDataType", Object, BoolSort())
CategoricalDataType = Function("CategoricalDataType", Object, BoolSort())
NumericDataType = Function("NumericDataType", Object, BoolSort())

# Data transformations, link functions
Transformation = Function("Transformation", Object, BoolSort())
NoTransformation = Function("NoTransformation", Object, BoolSort())
NumericTransformation = Function("NumericTransformation", Object, BoolSort())
CategoricalTransformation = Function("CategoricalTransformation", Object, BoolSort())
IdentityTransform = Function("IdentityTransform", Object, BoolSort())
LogTransform = Function("LogTransform", Object, BoolSort())
CLogLogTransform = Function("CLogLogTransform", Object, BoolSort())
SquarerootTransform = Function("SquarerootTransform", Object, BoolSort())
InverseTransform = Function("InverseTransform", Object, BoolSort())
InverseSquaredTransform = Function("InverseSquaredTransform", Object, BoolSort())
PowerTransform = Function("PowerTransform", Object, BoolSort())
CauchyTransform = Function("CauchyTransform", Object, BoolSort())
LogLogTransform = Function("LogLogTransform", Object, BoolSort())
ProbitTransform = Function("ProbitTransform", Object, BoolSort())
LogitTransform = Function("LogitTransform", Object, BoolSort())
NegativeBinomialTransform = Function("NegativeBinomialTransform", Object, BoolSort())

# Variance functions
GaussianFamily = Function("GaussianFamily", Object, BoolSort())
InverseGaussianFamily = Function("InverseGaussianFamily", Object, BoolSort())
PoissonFamily = Function("PoissonFamily", Object, BoolSort())
GammaFamily = Function("GammaFamily", Object, BoolSort())
TweedieFamily = Function("TweedieFamily", Object, BoolSort())
BinomialFamily = Function("BinomialFamily", Object, BoolSort())
NegativeBinomialFamily = Function("NegativeBinomialFamily", Object, BoolSort())
MultinomialFamily = Function("MultinomialFamily", Object, BoolSort())

# TODO: Variance functions can only have certain link functions

# Data collection procedures
Between = Function("Between", Object, Object, BoolSort())
Within = Function("Within", Object, Object, BoolSort())

# Template facts
# template_graph_facts = [
#     Cause(x, y),
#     Correlate(x, y)
# ]
