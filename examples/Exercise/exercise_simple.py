import tisane as ts
import pandas as pd
import os

"""
Example from Cohen, Cohen, West, Aiken 2003. Chapter 7 

Background, from Cohen et al. 2003: "...we present an example in which physical
endurance of n = 245 adults is predicted form their age and the number of years
of vigorous physical exercise in which they have engaged."
"""

# Load data
dir = os.path.dirname(__file__)
df = pd.read_csv(os.path.join(dir, "exercise_simple.csv"))

# df = pd.read_csv("./exercise_simple.csv")

# Declare observed variables
pid = ts.Unit("case", cardinality=50)  # 50 participants
age = pid.numeric("age")  # participant age
exercise = pid.numeric("exercise")  # years of vigorous physical exercise
endurance = pid.numeric(
    "endurance"
)  # number of minutes of sustained jogging on a treadmill

# Declare conceptual relationships between the observed variables
exercise.causes(endurance)
age.associates_with(endurance)

# Query Tisane to infer a statistical model and generate a script
design = ts.Design(dv=endurance, ivs=[age, exercise]).assign_data(df)  # Load data
ts.infer_statistical_model_from_design(design=design)
