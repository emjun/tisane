import tisane as ts

import pandas as pd

"""
Example from LME4 R dataset, used in Statsmodels example:
https://www.statsmodels.org/stable/examples/notebooks/generated/mixed_lm_example.html

Original source: Lauridsen, C., Højsgaard, S.,Sørensen, M.T. C. (1999) Influence of Dietary Rapeseed Oli, Vitamin E, and Copper on Performance and Antioxidant and Oxidative Status of Pigs. J. Anim. Sci.77:906-916 

Summary of source: https://vincentarelbundock.github.io/Rdatasets/doc/geepack/dietox.html
"""

# Load data
df = pd.read_csv('./examples/data/dietox.csv')

# Observed variables
pig_id = ts.Nominal('Pig', cardinality=69)
litter = ts.Nominal('Litter', cardinality=25)
weight = ts.Numeric('Weight')
time = ts.Nominal('Time', cardinality=12)

# Conceptual relationship
time.cause(weight)

# Data measurement
pig_id.repeats(weight, according_to=time)
pig_id.nests_under(litter)

design = ts.Design(
            dv = weight,
            ivs = [time, litter]
        ).assign_data(df)

ts.infer_statistical_model_from_design(design=design)

