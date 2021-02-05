from z3 import *

# Declare data type
Object = DeclareSort('Object')

# Declare free variables 
y = Const('y', Object)
xs = Const('xs', SeqSort(Object))
x = Const('x', Object) 
xs_sub = Const('xs_sub', SeqSort(Object))
x0 = Const('x0', Object) 
x1 = Const('x1', Object) 


##### MODEL EXPLANATION #####
# Declare functions for properties pertaining to model explanation
Explains = Function('Explains', Object, SeqSort(Object), BoolSort())
Models = Function('Models', Object, SeqSort(Object), BoolSort())
IsPredicted = Function('IsPredicted', Object, BoolSort())
IsPredictor = Function('IsPredictor', Object, BoolSort())
ArePredictors = Function('IsPredictor', SeqSort(Object), BoolSort())

# Declare constraints for model explanation 
model_explanation_rules = [
    ForAll([y, xs], Implies(Models(y, xs), Explains(y, xs))),
    ForAll([y, xs], Implies(Explains(y, xs), IsPredicted(y))),
    ForAll([x, xs], Implies(Contains(xs, Unit(x)), IsPredictor(x))),
    # The below cause the solver to return unknown. 
    # ForAll([xs, y], Implies(Explains(y, xs), Implies(Contains(xs, Unit(x)), IsPredictor(x)))),
    # ForAll([x, xs], Implies(ArePredictors(xs), And(Contains(xs, Unit(x)), IsPredictor(x)))),
]

##### CONCEPTUAL GRAPH #####
# Declare functions for properties pertaining to conceptual graphs
Cause = Function('Cause', Object, Object, BoolSort())
Correlate = Function('Correlate', Object, Object, BoolSort())
Cause_or_Correlate = Function('Cause_or_Correlate', Object, Object, BoolSort())
Interaction = Function('Interaction', SeqSort(Object), Object, BoolSort())
HasEdge = Function('HasEdge', Object, Object, BoolSort())

# Declare constraints for conceptual graphs
conceptual_graph_rules = [
    ForAll([x, y], Xor(Correlate(x, y), Cause(x, y))),
    ForAll([x, y], Implies(Cause(x, y), Cause_or_Correlate(x, y))), 
    ForAll([x, y], Implies(Correlate(x, y), Cause_or_Correlate(x, y))), 
    
    # Interactions TODO: Come back to more complicated interactions!
    # TODO: May want to support more than 2-way interactions by making x0, x1 a SeqSort() that is a subset of ivs
    # ForAll([xs_sub, xs, y], Implies(Interaction(xs_sub, y), Contains(xs, xs_sub))),
    # ForAll([xs_sub, xs, y], Implies(Contains(xs, xs_sub), Interaction(xs_sub, y))),

    # ForAll([x0, x1, xs, y], Implies(Interaction(x0, x1, y), Contains(xs, Unit(x1)))),
    # ForAll([x, xs_sub, y], Implies(Interaction(xs_sub, y), (Cause_or_Correlate(x0, y), Cause_or_Correlate(x1, y))),
]

##### DATA SCHEMA / TYPES #####
# Declare functions for properties pertaining to data schema/types
Categorical = Function('Categorical', Object, BoolSort())
Numeric = Function('Numeric', Object, BoolSort())
Unknown_Datatype = Function('Unknown_Datatype', Object, BoolSort())
Has_Datatype = Function('Has_Datatype', Object, BoolSort())
Ordinal = Function('Ordinal', Object, BoolSort())
Binary = Function('Binary', Object, BoolSort())

# Declare constraints pertaining to data schema/types
data_schema_rules = [
    Implies(Categorical(x), Has_Datatype(x)),
    ForAll([x], Implies(Numeric(x), Has_Datatype(x))),
    ForAll([x], Implies(Has_Datatype(x), Not(Unknown_Datatype(x)))),
    ForAll([x], Has_Datatype(x)), # Ensure that all variables have a data type associated with them
    Implies(Binary(x), Categorical(x)),
    Implies(Ordinal(x), Categorical(x)),
    ForAll([x], Xor(Categorical(x), Numeric(x)))
    # ForAll([x], Implies(Has_Datatype(x), XOr(Categorical(x), Numeric(x)))),
    
]

##### LINK FUNCTIONS ######
# Declare functions for properties pertaining to link functions of GLMs
Identity = Function('Identity', Object, BoolSort())
Log = Function('Log', Object, BoolSort())
Sqrt = Function('Sqrt', Object, BoolSort())
LogLog = Function('LogLog', Object, BoolSort())
Probit = Function('Probit', Object, BoolSort())
Logit = Function('Logit', Object, BoolSort())

# Declare constraints pertaining to link functions of GLMs
link_functions_rules = [
    ForAll([y], Implies(Identity(y), Numeric(y))), # could change y to x?
    ForAll([y], Implies(Log(y), Numeric(y))), # could change y to x?
    ForAll([y], Implies(Sqrt(y), Numeric(y))), # could change y to x?
    ForAll([y], Implies(LogLog(y), Categorical(y))), # could change y to x?
    ForAll([y], Implies(Probit(y), Categorical(y))), # could change y to x?
    ForAll([y], Implies(Logit(y), Categorical(y))), # could change y to x?
]

##### VARIANCE FUNCTIONS #####
# Declare functions for properties pertaining to variance functions of GLMs
Gaussian = Function('Gaussian', Object, BoolSort())
Inverse_Gaussian = Function('Inverse_Gaussian', Object, BoolSort())
Binomial = Function('Binomial', Object, BoolSort())
Multinomial = Function('Multinomial', Object, BoolSort())

# Declare constraints pertaining to variance functions of GLMs
variance_functions_rules = [
    ForAll([y], Implies(Binomial(y), Binary(y))),
    ForAll([y], Implies(Multinomial(y), Categorical(y))),
]