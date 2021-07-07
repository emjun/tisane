import tisane as ts

import pandas as pd
import numpy as np
import random

"""
Example from Barr et al. 2012: 'Keep it Maximal'
"""

rt = ts.Time("Reaction time")
condition = ts.Nominal("Condition", cardinality=2)  # A or B
item = ts.Nominal("Item", cardinality=2)  # 1, 2, 3, or 4
subject = ts.Nominal("Subject", cardinality=24)  # 24 subjects

# Conceptual relationship
condition.associates_with(rt)

# Data measurement
# condition.treat(item) # condition is treated to each item
item.has_unique(condition)  # condition is treated to each item
# condition.treat(subject, condition) # subjects see two conditions
condition.treat(subject, num_assignments=2)  # subjects see two conditions

item.has(condition, 1) # item has a unique condition 
subject.has(condition, 2) # subjects see two conditions
# Reasonable to assume item and subject are of type Unit? 
# Seems reasonable to assume subject is of type Unit, less sure about item as Unit. 
# If not, can Item be inferred as/to be a Unit? 
# But maybe a domain expert would easily name Item as a Unit? 

condition.has(subject, 24) # condition has up to 24 subjects ??

design = ts.Design(dv=rt, ivs=[condition])
# .assign_data('data.csv')
identifiers = design.graph.get_identifiers()

ts.infer_statistical_model_from_design(design=design)

# TODO:
# 1. Check for conceptual relationships IVs to DV
# 2. Check that DV not conceptuall cause/associate with IV
