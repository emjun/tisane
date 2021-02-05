from tisane.smt.helpers import *
from z3 import *

Object = DeclareSort('Object')

# Declare List data type with variable length
List = Datatype('List')
List.declare('cons', ('car', Object), ('cdr', List)) # Define ctor
# List.declare('cons', Object, ('cdr', List)) # Define ctor
List.declare('nil') # Define ctor
List = List.create() # Create Datatype

Explains = Function('Explains', Object, SeqSort(Object), BoolSort())
Models = Function('Models', Object, SeqSort(Object), BoolSort())
IsPredicted = Function('IsPredicted', Object, BoolSort())
IsPredictor = Function('IsPredictor', Object, BoolSort()) # TODO 
ArePredictors = Function('ArePredictors', SeqSort(Object), BoolSort()) # TODO

# Free variable
y = Const('y', Object)
# xs = Const('xs', List)
xs = Const('xs', SeqSort(Object))
x = Const('x', Object) # TODO: Want x to be in xss
x0 = Const('x0', Object) # TODO: Want x to be in xss
x1 = Const('x1', Object) # TODO: Want x to be in xss


# xs = Const('xs', SeqSort(Object)) 
# Create a sequence??
# s.add(Contains(oseq, Unit(IntVal(3))))

model_explanation = [
    ForAll([x, xs], Implies(Contains(xs, Unit(x)), IsPredictor(x))),
    ForAll([y, xs], Implies(Models(y, xs), Explains(y, xs))),
    ForAll([y, xs], Implies(Explains(y, xs), IsPredicted(y))),
    ForAll([y, xs], Implies(Explains(y, xs), ArePredictors(xs))), # TODO: Question of how to use IsPredictor for each IV? 
    # ForAll([x, xs], Implies(IsPredictor(x), ArePredictors(xs))), # TODO: Question of how to use IsPredictor for each IV? 
]

Cause = Function('Cause', Object, Object, BoolSort())
Correlate = Function('Correlate', Object, Object, BoolSort())
Cause_or_Correlate = Function('Cause_or_Correlate', Object, Object, BoolSort())
Interaction = Function('Interaction', Object, Object, Object, BoolSort())
HasEdge = Function('HasEdge', Object, Object, BoolSort())

conceptual_graph = [
    Xor(Correlate(x, y), Cause(x, y)),
    Implies(Cause(x, y), Cause_or_Correlate(x, y)), 
    Implies(Correlate(x, y), Cause_or_Correlate(x, y)), 
    
    # Interactions 
    Implies(Interaction(x0, x1, y), And(Cause_or_Correlate(x0, y), Cause_or_Correlate(x1, y))),
    Implies(Interaction(x0, x1, y), And(Cause_or_Correlate(x0, y), Cause_or_Correlate(x1, y))),
]

# Data types
Categorical = Function('Categorical', Object, BoolSort())
Numeric = Function('Numeric', Object, BoolSort())
Unknown_Datatype = Function('Unknown_Datatype', Object, BoolSort())
Has_Datatype = Function('Has_Datatype', Object, BoolSort())
Ordinal = Function('Ordinal', Object, BoolSort())
Binary = Function('Binary', Object, BoolSort())

data_types = [
    Implies(Categorical(x), Has_Datatype(x)),
    ForAll([x], Implies(Numeric(x), Has_Datatype(x))),
    # Xor(Has_Datatype(x), Unknown_Datatype(x)),
    ForAll([x], Implies(Has_Datatype(x), Not(Unknown_Datatype(x)))),
    ForAll([x], Has_Datatype(x)), # Ensure that all variables have a data type associated with them
    Implies(Binary(x), Categorical(x)),
    Implies(Ordinal(x), Categorical(x)),
    ForAll([x], Xor(Categorical(x), Numeric(x)))
    # ForAll([x], Implies(Has_Datatype(x), XOr(Categorical(x), Numeric(x)))),
    
]

# Link functions
Identity = Function('Identity', Object, BoolSort())
Log = Function('Log', Object, BoolSort())
Sqrt = Function('Sqrt', Object, BoolSort())
LogLog = Function('LogLog', Object, BoolSort())
Probit = Function('Probit', Object, BoolSort())
Logit = Function('Logit', Object, BoolSort())

link_functions = [
    ForAll([y], Implies(Identity(y), Numeric(y))), # could change y to x?
    ForAll([y], Implies(Log(y), Numeric(y))), # could change y to x?
    ForAll([y], Implies(Sqrt(y), Numeric(y))), # could change y to x?
    ForAll([y], Implies(LogLog(y), Categorical(y))), # could change y to x?
    ForAll([y], Implies(Probit(y), Categorical(y))), # could change y to x?
    ForAll([y], Implies(Logit(y), Categorical(y))), # could change y to x?
]

# Variance functions
Gaussian = Function('Gaussian', Object, BoolSort())
Inverse_Gaussian = Function('Inverse_Gaussian', Object, BoolSort())
Binomial = Function('Binomial', Object, BoolSort())
Multinomial = Function('Multinomial', Object, BoolSort())

variance_functions = [
    ForAll([y], Implies(Binomial(y), Binary(y))),
    ForAll([y], Implies(Multinomial(y), Categorical(y))),
]


s = Solver()

# Create objects to test with 
sat_score = Const('sat_score', Object)
intelligence = Const('intelligence', Object)
tutoring = Const('tutoring', Object)
# Create list of IVs
# TODO: Sequence
ivs = Empty(SeqSort(Object))
ivs = Concat(ivs, Unit(intelligence))
ivs = Concat(ivs, Unit(tutoring))

# Add model
s.add(Models(sat_score, ivs))

# Add constraints
s.add(And(model_explanation))

if (s.check() == unsat): 
    import pdb; pdb.set_trace()
s.push()

# Add constraints
s.add(And(conceptual_graph))
s.push()

# Add user assertions
input_conceptual_graph_assertions = [
    Cause(tutoring, sat_score), 
    Interaction(tutoring, intelligence, sat_score),
    # Correlate(tutoring, sat_score)
]
verify_update_constraints(solver=s, assertions=input_conceptual_graph_assertions)


# TODO: Could we represent conceptual tree in logic??

# state_cg = s.check(input_conceptual_graph_assertions)
# state_cg_unsat_core = s.unsat_core() 

# # This is a process that I want to repeat for each "chunk" of queries. 
# if (state_cg == unsat):
#     assert(len(state_cg_unsat_core) > 0)

#     s.push() # save state before add user input

#     # Ask user for input
#     keep_clause = elicit_user_input(s.assertions(), state_cg_unsat_core)
#     # Modifies input_conceptual_graph_assertions (first @param)
#     updated_clauses = update_clauses(input_conceptual_graph_assertions, state_cg_unsat_core, keep_clause)
#     input_conceptual_graph_assertions = updated_clauses

#     # Double check that the new_clauses do not cause UNSAT
#     s.add(input_conceptual_graph_assertions)
#     assert(s.check() == sat)
# elif (state_cg == sat): 
#     # Add input_conceptual_graph_assertions
#     s.add(input_conceptual_graph_assertions)
# else: 
#     raise ValueError(f"State of solver after adding user input conceptual graph constraints is {state_cg}")

import pdb; pdb.set_trace()

s.add(data_types)
input_data_type_assertions = [
    # TODO: by default, have to make sure that all the variables involved have a datatype if declared, otherwise, Unknown
    Numeric(sat_score),
    Binary(tutoring),
    Numeric(intelligence)
]
s.add(input_data_type_assertions)

if s.check(input_data_type_assertions) == unsat: 
    print(s.unsat_core())
    import pdb; pdb.set_trace()

print(s.check()) 

s.add(link_functions)
print(s.check())

s.add(variance_functions)
print(s.check())

mdl =  s.model()
import pdb; pdb.set_trace()
print(s.model()) # assumes s.check() is SAT

# TODO: In order to create output, need to get list of all final derived (from user-input SM)+ input constraints to stringify and parse...

### Questions? 
# How to use Sequence Sort? -- how to add 