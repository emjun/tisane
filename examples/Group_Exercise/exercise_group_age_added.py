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
data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "exercise_group_age_added.csv")

# Variable declarations
adult = ts.Unit("member", cardinality=386)
motivation_level = adult.ordinal(
    "motivation", order=[1, 2, 3, 4, 5, 6], number_of_instances=1
)
pounds_lost = adult.numeric("pounds_lost", number_of_instances=1)
age = adult.numeric("age", number_of_instances=1)
group = ts.Unit("group", cardinality=40)
condition = group.nominal(
    "treatment", cardinality=2, number_of_instances=1
)  # control vs. treatment

# Variable relationships
condition.causes(pounds_lost)
motivation_level.associates_with(pounds_lost)
age.associates_with(motivation_level)
age.associates_with(pounds_lost)
age.moderates(motivation_level, on=pounds_lost)
adult.nests_within(group)

# Query Tisane for a statistical model
design = ts.Design(dv=pounds_lost, ivs=[condition, motivation_level]).assign_data(
    data_path
)
ts.infer_statistical_model_from_design(design=design)
