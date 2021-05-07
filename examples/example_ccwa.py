import tisane as ts

import pandas as pd
import numpy as np

"""
Example from Cohen, Cohen, West, Aiken 2003. 

Background, from Cohen et al. 2003: We assume that the data have been collected
from intact women's groups that have a focus on diet and weight control; the
groups meet regularly to discuss diet and weight control, and have some level of
cohesion. we may thus expect some correlation among the women within a group j
in both their motivation to lose weight and weight loss success. 

There are a total of 386 women in all distributed across the 40 groups. Group
size ranges from 5 to 15 women. There is substantial clustering in the data,
reflected in the fact that the groups differe substantially in mean pounds of
weight lost, from a low mean of 9.75 points lost to a high mean of 24.43 pounds
lost. 
"""

# Load data

df = pd.read_csv("./examples/data/ccwa_mlm_data.csv")

# Observed variables
group = ts.Nominal("group", cardinality=40)  # 40 groups
member = ts.Nominal("member", cardinality=386)  # 386 participants
treatment = ts.Nominal("treatment", cardinality=2)  # 2 treatment groups
motivation = ts.Ordinal(
    "motivation", order=[1, 2, 3, 4, 5, 6]
)  # Motivation score on a 6-point scale
pounds_lost = ts.Numeric("pounds_lost")

# Conceptual relationships between the observed variables
motivation.cause(pounds_lost)
treatment.causes(pounds_lost)

# Data measurement relationships between the observed variables
treatment.treats(
    group, num_assignments=1
)  # Each group receives one treatment condition
member.nests_under(group)  # Members are part of groups
member.has(motivation)  # Each member has motivation (self-motivation)

# Query Tisane to infer a statistical model and generate a script
design = ts.Design(dv=pounds_lost, ivs=[treatment, motivation]).assign_data(
    df
)  # Load data
ts.infer_statistical_model_from_design(design=design)

# Equivalent:
# treatment.treats(group, assignment='between')
# group.has(member, 'between') # Members are part of one group and one group only

# ts.infer_statistical_model(dv=pounds_lost, ivs=[treatment, motivation])
