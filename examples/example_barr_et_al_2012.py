import tisane as ts

import pandas as pd
import numpy as np
import random

"""
Example from Barr et al. 2013: 'Keep it Maximal'
"""

## Load data
# df = pd.read_csv("./linguistics.csv")

## Declare observed variables
# Subjects are an experimental unit.
subject = ts.Unit("Subject", cardinality=12)

# Words are also an experimental/observational unit.
word = ts.Unit("Word", cardinality=4)

# Each subject has a two values for condition, which is nominal.
# Verbose: Each instance of subject has two instances of a nominal variable condition.
# Informally: Each subjects sees two (both) conditions.
condition = subject.nominal("Word type", cardinality=2, number_of_instances=2)

# Repeated measures
# Each subject has a measure reaction time, which is numeric, for each instance of a word
# Verbose: Each instance of subject has one instance of a numeric variable weight for each value of word.
# Informally: Each subject has a reaction time for each word.
reaction_time = subject.numeric("Time", number_of_instances=word)

# Each condition has/is comprised of two words.
condition.has(word, number_of_instances=2)
# # ALTERNATIVELY, we could do something like the below (not implemented). It is a bit more complicated to calculate the number of instances, but still doable I think.
# # Each word has one value for condition (already defined above as a measure of subject)
# word.has(condition, number_of_instances=1) # Condition has two units

condition.causes(reaction_time)

## Query relatioships to infer a statistical model and generate a script
design = ts.Design(dv=reaction_time, ivs=[condition])
ts.infer_statistical_model_from_design(design=design)
