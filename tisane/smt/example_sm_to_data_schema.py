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
x = sat_score
intelligence = Const('intelligence', Object)
tutoring = Const('tutoring', Object)


# Create sequence of main effects
main_effects = Concat(Unit(tutoring), Unit(intelligence))

# Create set for interaction
tutoring_intelligence = EmptySet(Object)
tutoring_intelligence = SetAdd(tutoring_intelligence, tutoring)
tutoring_intelligence = SetAdd(tutoring_intelligence, intelligence)
interactions = Unit(tutoring_intelligence)

# tutoring_sat = EmptySet(Object)
# tutoring_sat = SetAdd(tutoring_sat, tutoring)
# tutoring_sat = SetAdd(tutoring_sat, sat_score)
# interactions = Concat(Unit(tutoring_sat), interactions)

# Declare functions for properties pertaining to model explanation
Explains = Function('Explains', Object, SeqSort(Object), BoolSort())
Models = Function('Models', Object, SeqSort(Object), BoolSort())
Dependent = Function('Dependent', Object, BoolSort())
MainEffect = Function('MainEffect', Object, BoolSort())
NoInteractions = Function('No Interaction', Object, SeqSort(Object), BoolSort())
Interaction = Function('Interaction', Object, Object, BoolSort())

Cause = Function('Cause', Object, Object, BoolSort())
Correlate = Function('Correlate', Object, Object, BoolSort())

rules = [
    ForAll([x], Implies(Contains(main_effects, Unit(x)), Xor(Cause(x, x), Correlate(x, x)))),
    ForAll([x0, x1, i], Implies(And(Contains(interactions, Unit(i)), And(IsMember(x0, i), IsMember(x1, i))), Xor(Cause(x0, x1), Correlate(x0, x1)))),
    # ForAll([x0, x1], Implies(And(IsMember(x0, interactions), IsMember(x1, interactions)), Xor(Cause(x0, x1), Correlate(x0, x1))))
    # ADD RULE FOR CANT INTERACTION X with Y

    # ForAll([x], Implies(NoInteractions(x, interactions), Length(interactions) == 1))
    # ForAll([xs], Implies(Contains(interactions, Unit(xs)), Xor(Cause(x, sat_score), Correlate(x, sat_score)))),
    # Something similar for Between vs. Within subjects?
    # Between subjects means occurs once per subject   
]


Binary = Function('Binary', Object, BoolSort())
Multinomial = Function('Multinomial', Object, BoolSort())
Nominal = Function('Nominal', Object, BoolSort())
Ordinal = Function('Ordinal', Object, BoolSort())
Categorical = Function('Categorical', Object, BoolSort())
Numeric = Function('Numeric', Object, BoolSort())

data_type_rules = [
    ForAll([x], Xor(Categorical(x), Numeric(x))), 
    ForAll([x], Implies(Categorical(x), Xor(Ordinal(x), Nominal(x)))),
    ForAll([x], Or(Ordinal(x), Nominal(x))),
    # ForAll([x], Implies(Categorical(x), Xor(Binary(x), Multinomial(x)))),
    # ForAll([x], Implies(Binary(x), Categorical(x))),
    # ForAll([x], Implies(Multinomial(x), Categorical(x))),
    # ForAll([x], Implies(Nominal(x), Categorical(x))),
    # ForAll([x], Implies(Ordinal(x), Categorical(x))),
]

# starting state
facts = [
    Models(sat_score, main_effects), 
    Dependent(sat_score),
    Cause(tutoring, sat_score), # Add both for each main effect and require end-user to pick one
    Correlate(tutoring, sat_score),
    Cause(intelligence, sat_score), # Add both for each main effect and require end-user to pick one
    Correlate(intelligence, sat_score),
]

data_type_facts = [
    # Ordinal(tutoring),
    # Nominal(tutoring),
    Categorical(tutoring),
    Numeric(intelligence),
    Numeric(sat_score)
]
# TODO: Might have to stage facts about Categorical vs. Numeric --> If categorical, nominal vs. ordinal && Binary or Multinomial

s.add(data_type_rules)
s = check_update_constraints(solver=s, assertions=data_type_facts)
# import pdb; pdb.set_trace()

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

    # ForAll([x], Implies(And(Dependent(x), Identity(x)), Numeric(x))),
    ForAll([x], Implies(Identity(x), Numeric(x))),
    # Implies(Log(x), Numeric(x)), #could change y to x?
    # Implies(Sqrt(x), Numeric(x)), # could change y to x?
    ForAll([x], Implies(LogLog(x), Categorical(x))),
    # Implies(LogLog(x), Categorical(x)), # could change y to x?
    # Implies(Probit(x), Categorical(x)), # could change y to x?
    # Implies(Logit(x), Categorical(x)), # could change y to x?
]

link_facts = [
    Dependent(sat_score),
    Identity(sat_score),
    LogLog(sat_score)
]

s.add(link_functions_rules)
s = check_update_constraints(solver=s, assertions=link_facts)
import pdb; pdb.set_trace()

##### VARIANCE FUNCTIONS #####
# Declare functions for properties pertaining to variance functions of GLMs
Gaussian = Function('Gaussian', Object, BoolSort())
Inverse_Gaussian = Function('Inverse_Gaussian', Object, BoolSort())
Binomial = Function('Binomial', Object, BoolSort())
Multinomial = Function('Multinomial', Object, BoolSort())

# Declare constraints pertaining to variance functions of GLMs
variance_functions_rules = [
    Implies(Gaussian(x), Numeric(x)),
    Implies(Binomial(x), Binary(x)),
    Implies(Multinomial(x), Categorical(x)),
]

variance_facts = [
    Gaussian(sat_score),
    Binomial(sat_score)
]

s.add(variance_functions_rules)
s = check_update_constraints(solver=s, assertions=variance_facts)
import pdb; pdb.set_trace()

# At end of facts disambiguation, will have a complete set of facts for conceptual graph
# TODO: If add more facts about additional relationships (e.g., that might suggest interaction), what do we do? -- this is something we would have to take care of in sys architecture?
# TODO: Need to know which facts to add depending on query!!!
# Create separate sample programs for different queries and then figure out how to generate dynamically/connect up with rest of Tisane
# Query for variable relationship graph
# Query for data schema

s.add(data_type_rules)
s = check_update_constraints(solver=s, assertions=data_type_facts)
import pdb; pdb.set_trace()

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
