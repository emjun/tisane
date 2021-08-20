import tisane as ts

import pandas as pd
import numpy as np
import os

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
dir = os.path.dirname(__file__)
df = pd.read_csv(os.path.join(dir, "exercise_group.csv"))
# df = pd.read_csv("./exercise_groups.csv")

# Observed variables
adult = ts.Unit("member", cardinality=386)  # 386 adults
# Each adult has a value for motivation, which is ordinal
motivation_level = adult.ordinal("motivation", order=[1, 2, 3, 4, 5, 6])
pounds_lost = adult.numeric("pounds_lost")
group = ts.Unit("group", cardinality=40)  # 40 groups
# Each group has one of two approaches to weight loss they promote
# Note: By default, number_of_instances equals 1. The parameter value is explicitly set below for clarity.
treatment_approach = group.nominal(
    "treatment", cardinality=2, number_of_instances=1
)  # 2 approaches to weight loss ("Control" and "Treatment")

# Conceptual relationships between the observed variables
motivation_level.causes(pounds_lost)
treatment_approach.causes(pounds_lost)

# Data measurement relationships
# Declare nesting relationship
adult.nests_within(group)  # Members are part of groups

# Query Tisane to infer a statistical model and generate a script
design = ts.Design(dv=pounds_lost, ivs=[treatment_approach, motivation_level]).assign_data(
    df
)  # Load data
ts.infer_statistical_model_from_design(design=design)

# Equivalent:
# treatment.treats(group, assignment='between')
# group.has(member, 'between') # Members are part of one group and one group only

# ts.infer_statistical_model(dv=pounds_lost, ivs=[treatment, motivation])
