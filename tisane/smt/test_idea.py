from tisane.smt.helpers import *
from z3 import *

Object = DeclareSort('Object')

# Declare List data type with variable length
List = Datatype('List')
List.declare('cons', ('car', Object), ('cdr', List)) # Define ctor
# List.declare('cons', Object, ('cdr', List)) # Define ctor
List.declare('nil') # Define ctor
List = List.create() # Create Datatype

Explains = Function('Explains', Object, List, BoolSort())
Models = Function('Models', Object, List, BoolSort())
IsPredicted = Function('IsPredicted', Object, BoolSort())
IsPredictor = Function('IsPredictor', Object, BoolSort()) # TODO 
ArePredictors = Function('ArePredictors', List, BoolSort()) # TODO

# Free variable
y = Const('y', Object)
xs = Const('xs', List)
x = Const('x', Object) # TODO: Want x to be in xss
# xs = Const('xs', SeqSort(Object)) 

# assert 3 is somewhere in this sequence
# s.add(Contains(oseq, Unit(IntVal(3))))

model_explanation = [
    ForAll([y, xs], Implies(Models(y, xs), Explains(y, xs))),
    ForAll([y, xs], Implies(Explains(y, xs), IsPredicted(y))),
    ForAll([y, xs], Implies(Explains(y, xs), ArePredictors(xs))), # TODO: Question of how to use IsPredictor for each IV? 
    # ForAll([x, xs], Implies(IsPredictor(x), ArePredictors(xs))), # TODO: Question of how to use IsPredictor for each IV? 
]

Cause = Function('Cause', Object, Object, BoolSort())
Correlate = Function('Correlate', Object, Object, BoolSort())
Cause_or_Correlate = Function('Cause_or_Correlate', Object, Object, BoolSort())
HasEdge = Function('HasEdge', Object, Object, BoolSort())

conceptual_graph = [
    # ForAll([x, y], Implies(Cause(x, y), HasEdge(x, y))),
    # ForAll([x, y], Implies(Correlate(x, y), HasEdge(x, y))),
    # ForAll([x, y], Implies(HasEdge(x, y), (Or(Cause(x, y), Correlate(x, y))))),
    # Implies(Cause(x,y), HasEdge(x, y)),
    # Implies(Correlate(x,y), HasEdge(x, y)),
    
    # Implies(Cause_or_Correlate(x, y), ForAll([x, y], Xor(Correlate(x, y), Cause(x, y)))),
    ForAll([x, y], Xor(Correlate(x, y), Cause(x, y))),
    # Xor(Cause(x, y), Correlate(x, y)),
]


s = Solver()

# Create objects to test with 
sat_score = Const('sat_score', Object)
intelligence = Const('intelligence', Object)
tutoring = Const('tutoring', Object)
# Create list of IVs
ivs = List.cons(tutoring, List.nil)
ivs = List.cons(intelligence, ivs) 

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
    Correlate(tutoring, sat_score)
]
state_cg = s.check(input_conceptual_graph_assertions)
state_cg_unsat_core = s.unsat_core() 

if (state_cg == unsat):
    assert(len(state_cg_unsat_core) > 0)

    s.push() # save state before add user input

    # Ask user for input
    keep_clause = elicit_user_input(s.assertions(), state_cg_unsat_core)
    # Modifies input_conceptual_graph_assertions (first @param)
    updated_clauses = update_clauses(input_conceptual_graph_assertions, state_cg_unsat_core, keep_clause)
    input_conceptual_graph_assertions = updated_clauses

    # Double check that the new_clauses do not cause UNSAT
    s.add(input_conceptual_graph_assertions)
    assert(s.check() == sat)
elif (state_cg == sat): 
    pass
else: 
    raise ValueError(f"State of solver after adding user input conceptual graph constraints is {state_cg}")

print(s.check()) 
print(s.model()) # assumes s.check() is SAT

### Questions? 
# How to use Sequence Sort? -- how to add 