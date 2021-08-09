import tisane as ts

import pandas as pd

"""
Example from Cohen, Cohen, West, Aiken 2003. Chapter 7 

Background, from Cohen et al. 2003: "...we present an example in which physical
endurance of n = 245 adults is predicted form their age and the number of years
of vigorous physical exercise in which they have engaged."
"""

# Load data
df = pd.read_csv("./examples/data/ccwa_ch7_1.csv")

# Declare observed variables
pid = ts.Nominal("case", cardinality=50)  # 50 participants
age = ts.Numeric("age")  # participant age
exercise = ts.Numeric("exercise")  # years of vigorous physical exercise
endurance = ts.Time(
    "endurance"
)  # number of minutes of sustained jogging on a treadmill

# Declare conceptual relationships between the observed variables
exercise.cause(endurance)
age.associates_with(endurance)

# Declare data measurement relationships between the observed variables
pid.has(age)
pid.has(exercise)
pid.has(endurance)

# Query Tisane to infer a statistical model and generate a script
design = ts.Design(dv=endurance, ivs=[age, exercise]).assign_data(df)  # Load data
ts.infer_statistical_model_from_design(design=design)
