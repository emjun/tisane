from tisane.smt.helpers import *
from z3 import *

s = Solver()
# s.set("core.minimize",True) # force min unsat core, may not need

# Declare data type
Object = DeclareSort('Object')

# Declare free variables 
x = Const('x', Object)
x0 = Const('x0', Object)
x1 = Const('x1', Object)
i = Const('x1', SetSort(Object))

##### MAIN EFFECTS ONLY : Y = X1 + X2
# Create objects for current statistical model
sat_score = Const('sat_score', Object)
_y = sat_score
intelligence = Const('intelligence', Object)
tutoring = Const('tutoring', Object)


# Create sequence of main effects
main_effects = Concat(Unit(tutoring), Unit(intelligence))

# Create set for interaction
tutoring_intelligence = EmptySet(Object)
tutoring_intelligence = SetAdd(tutoring_intelligence, tutoring)
tutoring_intelligence = SetAdd(tutoring_intelligence, intelligence)
interactions = Unit(tutoring_intelligence)

tutoring_sat = EmptySet(Object)
tutoring_sat = SetAdd(tutoring_sat, tutoring)
tutoring_sat = SetAdd(tutoring_sat, sat_score)
interactions = Concat(Unit(tutoring_sat), interactions)

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
    # ForAll([x0, x1], Implies(Interaction(x0, x1), Xor(Cause(x0, x1), Correlate(x0, x1)))),
    # Implies(Interaction(x0, x1), Xor(Cause(x0, x1), Correlate(x0, x1))),
    ForAll([x0, x1, i], Implies(And(Contains(interactions, Unit(i)), And(IsMember(x0, i), IsMember(x1, i))), Xor(Cause(x0, x1), Correlate(x0, x1)))),
    # ForAll([x0, x1], Implies(And(IsMember(x0, interactions), IsMember(x1, interactions)), Xor(Cause(x0, x1), Correlate(x0, x1))))
    # ADD RULE FOR CANT INTERACTION X with Y

    # ForAll([x], Implies(NoInteractions(_y, interactions), Length(interactions) == 1))
    # ForAll([xs], Implies(Contains(interactions, Unit(xs)), Xor(Cause(x, sat_score), Correlate(x, sat_score)))),
    # Something similar for Between vs. Within subjects?
    # Between subjects means occurs once per subject   
]

# starting state
facts = [
    Models(sat_score, main_effects), 
    Dependent(sat_score),
    # MainEffect(tutoring),
    Cause(tutoring, sat_score), # Add both for each main effect and require end-user to pick one
    Correlate(tutoring, sat_score),
    # MainEffect(intelligence),
    Cause(intelligence, sat_score), # Add both for each main effect and require end-user to pick one
    Correlate(intelligence, sat_score),
]

# At end of facts disambiguation, will have a complete set of facts for conceptual graph
# TODO: If add more facts about additional relationships (e.g., that might suggest interaction), what do we do? -- this is something we would have to take care of in sys architecture?
# TODO: Need to know which facts to add depending on query!!!
# Create separate sample programs for different queries and then figure out how to generate dynamically/connect up with rest of Tisane
# Query for variable relationship graph
# Query for data schema

s.add(rules)
s = check_update_constraints(solver=s, assertions=facts)

# Output 
# Create Variable Relationship Graph
parse_and_create_variable_relationship_graph(solver=s)
# s.consequences()
#s.eval()


##### INTERACTION EFFECTS : Y = X1 + X2 + X1*X2
# Need to add when instantiate interactions variable above, before rules using interactions
# interactions = SetAdd(interactions, tutoring)
# interactions = SetAdd(interactions, intelligence)

ixn_facts = [
    Models(sat_score, main_effects), 
    Dependent(sat_score),
    Cause(tutoring, sat_score), # main effect disambiguation
    Correlate(tutoring, sat_score),
    Cause(intelligence, sat_score), # main effect disambiguation
    Correlate(intelligence, sat_score),
    Cause(tutoring, intelligence), # Add both for each interaction effect and require end-user to pick one
    Correlate(tutoring, intelligence),
]

s1 = Solver()
s1.add(rules)
s1 = check_update_constraints(solver=s1, assertions=ixn_facts)
parse_and_create_variable_relationship_graph(solver=s1)
