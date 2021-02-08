from tisane.smt.declare_constraints import *
from tisane.smt.helpers import *
from z3 import *

s = Solver()

# TODO: Depending on query (for data schema, for data collection procedure, for power, etc.) change the facts that are considered and how (order)??
# TODO: generic way to create and use objects (ivs and y) depending on statistical model input from end-user


# Create objects for current statistical model
sat_score = Const('sat_score', Object)
intelligence = Const('intelligence', Object)
tutoring = Const('tutoring', Object)

# Create sequence of IVs -- should be only Main effects?
ivs = Concat(Unit(tutoring), Unit(intelligence))

# Create sequence of Interaction effects 
ixn = Concat(Unit(intelligence), Unit(tutoring))

##### MODEL EXPLANATION #####
# Add rules
s.add(And(model_explanation_rules))

# Add facts (implied/asserted by user)
facts_model_explanation = [
    Models(sat_score, ivs)
]
verify_update_constraints(solver=s, assertions=facts_model_explanation)
s.push()

##### CONCEPTUAL GRAPH #####
# Add rules
s.add(And(conceptual_graph_rules))

# Add facts (implied/asserted by user)
facts_conceptual_graph = [
    Cause(tutoring, sat_score), 
    Correlate(intelligence, sat_score),
    # Interaction(ixn, sat_score),
]
verify_update_constraints(solver=s, assertions=facts_conceptual_graph)
s.push()

##### DATA SCHEMA/TYPE #####
# Add rules
s.add(data_schema_rules)

# Add facts (implied/asserted by user)
# TODO: by default, have to make sure that all the variables involved have a datatype if declared, otherwise, Unknown
facts_data_schema = [
    Numeric(sat_score), 
    Numeric(intelligence), 
    Binary(tutoring)
]
verify_update_constraints(solver=s, assertions=facts_data_schema)
s.push()

##### LINK FUNCTIONS #####
# Add rules
s.add(link_functions_rules)

# Add facts (implied/asserted by user)
facts_link_functions = [
    
]
verify_update_constraints(solver=s, assertions=facts_link_functions)
s.push()

##### VARIANCE FUNCTIONS #####
# Add rules
s.add(variance_functions_rules)

# Add facts (implied/asserted by user)
facts_variance_functions = [
    
]
verify_update_constraints(solver=s, assertions=facts_variance_functions)
s.push()

mdl =  s.model()
import pdb; pdb.set_trace()
print(s.model()) # assumes s.check() is SAT

### Questions? 
# TODO: Could we represent conceptual tree in logic??
# TODO: In order to create output, need to get list of all final derived (from user-input SM)+ input constraints to stringify and parse...
# TODO: Depending on reasoning direction (SM -> ED/ED -> SM ), should add the constraints in a different order?
# TODO: verify that all info is provided or inferred


# Horn logic
# Definite clauses (implications)
# Facts (Assume <some constraint> holds/is true)
# Goal clause (all clauses hold) -- combination of all definite clauses?