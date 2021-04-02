import tisane as ts

import pandas as pd
import numpy as np
import random
"""
Example from Barr et al. 2012: 'Keep it Maximal'
"""

rt = ts.Time('Reaction time')
condition = ts.Nominal('Condition', cardinality=2) # A or B
item = ts.Nominal('Item', cardinality=2) # 1, 2, 3, or 4
subject = ts.Nominal('Subject', cardinality=24) # 24 subjects

# Conceptual relationship
condition.associates_with(rt)
# Data measurement
# condition.treat(item) # condition is treated to each item
item.has_unique(condition) # condition is treated to each item
# condition.treat(subject, condition) # subjects see two conditions
condition.treat(subject, num_assignments=2) # subjects see two conditions

design = ts.Design(
            dv = rt,
            ivs = [condition]
        )
        # .assign_data('data.csv')
identifiers = design.graph.get_identifiers()

ts.synthesize_statistical_model(design=design)

# TODO: 
# 1. Check for conceptual relationships IVs to DV
# 2. Check that DV not conceptuall cause/associate with IV