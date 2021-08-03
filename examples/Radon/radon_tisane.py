import tisane as ts

import pandas as pd

# Load data
df = pd.read_csv("./radon_data_combined.csv")

# Observed variables
household = ts.Unit("household")
radon = household.numeric("y")
is_first_floor = household.nominal("x")
county = ts.Unit("county")
uranium = county.numeric("u.full")

# Conceptual relationship
is_first_floor.associates_with(radon)
uranium.associates_with(radon)

# Data measurement relationships
household.nests_within(county)

# Specify and execute query
design = ts.Design(dv=radon, ivs=[is_first_floor, uranium]).assign_data(df)

ts.infer_statistical_model_from_design(design=design)


design = ts.Design(dv=radon)

design.specify_must_have_iv(is_first_floor)
design.specify_must_have_iv(uranium)

design.specify_would_be_nice_to_have(is_first_floor)
design.specify_would_be_nice_to_have(uranium)


design = ts.Design(dv=radon, ivs={'must_have': [is_first_floor], 'would_be_nice_to_have': [uranium]})

# TODO: Look at Z3 hard/soft constraint/weighting API

# Implement the updated variable API just for nested and repeated measures
# Write test cases and implement the main, interaction, and random effects generation functions
# Write test cases and implement the family/link function generation functions
# [start here tomorrow] Write function for generating all combinations of model effects + family/link
# Sketch through GUI again
