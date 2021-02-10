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


##### Dynamically generate the constants #####
# Declare constants
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
#####

# Declare functions for properties pertaining to model explanation
Explains = Function('Explains', Object, SeqSort(Object), BoolSort())
Models = Function('Models', Object, SeqSort(Object), BoolSort())
Dependent = Function('Dependent', Object, BoolSort())
MainEffect = Function('MainEffect', Object, BoolSort())
Interaction = Function('Interaction', Object, Object, BoolSort())

Cause = Function('Cause', Object, Object, BoolSort())
Correlate = Function('Correlate', Object, Object, BoolSort())

graph_rules = [
    ForAll([x], Implies(Contains(main_effects, Unit(x)), Xor(Cause(x, _y), Correlate(x, _y)))),
    ForAll([x0, x1, i], Implies(And(Contains(interactions, Unit(i)), And(IsMember(x0, i), IsMember(x1, i))), Xor(Cause(x0, x1), Correlate(x0, x1)))),
    # TODO: ADD RULE FOR CANT INTERACTION X with Y?
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
    ForAll([x], Implies(Categorical(x), Xor(Binary(x), Multinomial(x)))),
    ForAll([x], Implies(Binary(x), Categorical(x))),
    ForAll([x], Implies(Multinomial(x), Categorical(x))),
    ForAll([x], Implies(Nominal(x), Categorical(x))),
    ForAll([x], Implies(Ordinal(x), Categorical(x))),
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
# data transformation rules
data_transformation_rules = [
    # ForAll([x], Xor(Categorical(x), Numeric(x))), 
    # ForAll([x], Implies(Identity(x), Numeric(x))),
    ForAll([x], Implies(Log(x), Numeric(x))), 
    # ForAll([x], Implies(Sqrt(x), Numeric(x))), 
    ForAll([x], Implies(LogLog(x), Categorical(x))),
    # ForAll([x], Implies(LogLog(x), Categorical(x))),
    # ForAll([x], Implies(Probit(x), Categorical(x))), 
    # ForAll([x], Implies(Logit(x), Categorical(x)))
]

##### VARIANCE FUNCTIONS #####
# Declare functions for properties pertaining to variance functions of GLMs
Gaussian = Function('Gaussian', Object, BoolSort())
Inverse_Gaussian = Function('Inverse_Gaussian', Object, BoolSort())
Binomial = Function('Binomial', Object, BoolSort())
Multinomial = Function('Multinomial', Object, BoolSort())

# Declare constraints pertaining to variance functions of GLMs
variance_functions_rules = [
    ForAll([x], Implies(Gaussian(x), Numeric(x))),
    ForAll([x], Implies(Binomial(x), Binary(x))),
    ForAll([x], Implies(Multinomial(x), Categorical(x))),
]

all_rules = graph_rules + data_type_rules + data_transformation_rules + variance_functions_rules

##### STARTING STATE 

model_facts = [
    Models(sat_score, main_effects), 
    Dependent(sat_score),
]

graph_facts = [
    Cause(tutoring, sat_score), # Add both for each main effect and require end-user to pick one
    Correlate(tutoring, sat_score),
    Cause(intelligence, sat_score), # Add both for each main effect and require end-user to pick one
    Correlate(intelligence, sat_score),
]

data_type_facts = [
    Categorical(tutoring), # Add both, require user to disambiguate
    Numeric(tutoring),
    Categorical(intelligence), # Add both, require user to disambiguate
    Numeric(intelligence),
    Categorical(sat_score), # Add both, require user to disambiguate
    Numeric(sat_score),
]

link_facts = [
    Dependent(sat_score),
    # Identity(sat_score),
    Log(sat_score),
    LogLog(sat_score),
    
]

variance_facts = [
    Gaussian(sat_score),
    Binomial(sat_score)
]

# TODO: Might have to stage facts about Categorical vs. Numeric --> If categorical, nominal vs. ordinal && Binary or Multinomial
# all_facts = model_facts + graph_facts + data_type_facts + link_facts + variance_facts
# all_facts = model_facts + link_facts
all_facts = link_facts
# import pdb; pdb.set_trace()
# s.add(graph_rules)
# import pdb; pdb.set_trace()
s.add(data_type_rules)
# import pdb; pdb.set_trace()
s.add(data_transformation_rules)
# import pdb; pdb.set_trace()
# s.add(variance_functions_rules)
# import pdb; pdb.set_trace()
s = check_update_constraints(solver=s, assertions=all_facts)
# TODO: There are facts that are repeatedly added. 
import pdb; pdb.set_trace()

# At end of facts disambiguation, will have a complete set of facts for conceptual graph
# TODO: If add more facts about additional relationships (e.g., that might suggest interaction), what do we do? -- this is something we would have to take care of in sys architecture?
# TODO: Need to know which facts to add depending on query!!!
# Create separate sample programs for different queries and then figure out how to generate dynamically/connect up with rest of Tisane
# Query for variable relationship graph
# Query for data schema

# Output 
# Create Variable Relationship Graph
parse_and_create_variable_relationship_graph(solver=s)



# TODO: for data collection procedure
    # Something similar for Between vs. Within subjects?
    # Between subjects means occurs once per subject   