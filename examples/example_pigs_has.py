import tisane as ts
import pandas as pd

# Load data
df = pd.read_csv("./examples/data/dietox.csv")

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

# Instead of repeats
pig.has(weight)
time.has(weight, 1)  # already know that pig has weight
# If not specify Time as Unit, could still infer that time is effectively a unit?
# Check that multiple has point to weight and then infer random effect from that?
# The above check might also apply to Barr example, too. --> TODO: Is there an example where this inference would be incorrect?

# Instead of nests_under
pig.has(litter, 1)  # Each pig has 1 litter
litter.has(pig, 30)  # Each litter has 30 pigs
# Detect units that have mutual has relationships pointing to each other

# Have a unit variable type:
pig = ts.Unit("Pig", cardinality=69)  # 69 pigs
litter = ts.Unit("Litter", cardinality=25)
weight = ts.Numeric("Weight")
time = ts.Nominal("Time", cardinality=12)
# A separate Unit variable type makes has statements less ambiguous?  And checks can ensure that there are relationships/edges pointing in both directions between units.
# If use has and require #, what if not complete factorial design. I.e., different numbers of pigs in each litter

# Specify and execute query
design = ts.Design(dv=weight, ivs=[time]).assign_data(df)

ts.infer_statistical_model_from_design(design=design)
