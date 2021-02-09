from tisane.smt.helpers import *
from z3 import *

s = Solver()
# s.set("core.minimize",True) # force min unsat core, may not need
# TODO: Interaction effects 

# Declare data type
Object = DeclareSort('Object')
# Declare free variables 
x = Const('x', Object)

##### MAIN EFFECTS ONLY
# Create objects for current statistical model
sat_score = Const('sat_score', Object)
_y = sat_score
intelligence = Const('intelligence', Object)
tutoring = Const('tutoring', Object)

# Create sequence of main effects
main_effects = Concat(Unit(tutoring), Unit(intelligence))
# interactions = Unit(IntVal(0))

# Declare functions for properties pertaining to model explanation
Explains = Function('Explains', Object, SeqSort(Object), BoolSort())
Models = Function('Models', Object, SeqSort(Object), BoolSort())
Dependent = Function('Dependent', Object, BoolSort())
MainEffect = Function('MainEffect', Object, BoolSort())
NoInteractions = Function('No Interaction', Object, SeqSort(Object), BoolSort())
Interaction = Function('Interaction', Object, Object, BoolSort())

# IsPredicted = Function('IsPredicted', Object, BoolSort())
# IsPredictor = Function('IsPredictor', Object, BoolSort())
# ArePredictors = Function('IsPredictor', SeqSort(Object), BoolSort())

Cause = Function('Cause', Object, Object, BoolSort())
Correlate = Function('Correlate', Object, Object, BoolSort())

rules = [
    ForAll([x], Implies(Contains(main_effects, Unit(x)), Xor(Cause(x, _y), Correlate(x, _y)))),
    # ForAll([x], Implies(NoInteractions(_y, interactions), Length(interactions) == 1))
    # ForAll([xs], Implies(Contains(interactions, Unit(xs)), Xor(Cause(x, sat_score), Correlate(x, sat_score)))),
    # Something similar for Between vs. Within subjects?
    # Between subjects means occurs once per subject   
]

facts = [
    Models(sat_score, main_effects), 
    Dependent(sat_score),
    MainEffect(tutoring),
    Cause(tutoring, sat_score), # Add both for each main effect and require end-user to pick one
    Correlate(tutoring, sat_score),
    MainEffect(intelligence),
    Cause(intelligence, sat_score), # Add both for each main effect and require end-user to pick one
    Correlate(intelligence, sat_score),
]

# At end of facts disambiguation, will have a complete set of facts for conceptual graph
# TODO: If add more facts about additional relationships (e.g., that might suggest interaction), what do we do? -- this is something we would have to take care of in sys architecture?
# TODO: START HERE: Read advanced webpage (incremental)
# Create separate sample programs for different queries and then figure out how to generate dynamically/connect up with rest of Tisane
# Query for variable relationship graph
# Query for data schema

s.add(rules)
s = check_update_constraints(solver=s, assertions=facts)

# Output 
# Create Variable Relationship Graph
parse_and_create_variable_relationship_graph(solver=s)


# TODO: Need to know which facts to add depending on query!!!

# s.consequences()
#s.eval()