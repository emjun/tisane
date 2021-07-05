import tisane as ts

import pandas as pd

# Load data
df = pd.read_csv("./demo/data/dietox.csv")

# Observed variables
pig = ts.Nominal("Pig", cardinality=69)
litter = ts.Nominal("Litter", cardinality=25)
weight = ts.Numeric("Weight")
time = ts.Nominal("Time", cardinality=12)

# Conceptual relationship
time.cause(weight)

# Data measurement relationships
pig.repeats(weight, according_to=time)
pig.nests_under(litter)

# Specify and execute query
design = ts.Design(dv=weight, ivs=[time]).assign_data(df)

ts.infer_statistical_model_from_design(design=design)
