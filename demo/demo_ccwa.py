import tisane as ts

import pandas as pd

"""
Example from Cohen, Cohen, West, Aiken 2013. Chapter 7 
"""

# Load data
df = pd.read_csv("./demo/data/ccwa.csv")

# Declare observed variables
pid = ts.Nominal("case", cardinality=245)  # 245 participants
age = ts.Numeric("age")  # participant age
exercise = ts.Numeric("exercise")  # years of vigorous physical exercise
endurance = ts.Numeric(
    "endurance"
)  # number of minutes of sustained jogging on a treadmill
sports = ts.Nominal(
    "child_sports_participation", cardinality=2
)  # Was this person enrolled in a sport

# Declare conceptual relationships between the observed variables
exercise.cause(endurance)
age.associates_with(endurance)
sports.associates_with(endurance)

# Declare data measurement relationships between the observed variables
pid.has(age)
pid.has(exercise)
pid.has(endurance)
pid.has(sports)

# Query Tisane to infer a statistical model and generate a script
design = ts.Design(dv=endurance, ivs=[age, exercise]).assign_data(df)  # Load data
ts.infer_statistical_model_from_design(design=design)
