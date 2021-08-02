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
