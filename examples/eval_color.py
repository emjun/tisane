import tisane as ts
import pandas as pd

# Load data
df = pd.read_csv("./examples/data/color.csv")

# Observed variables
subject = ts.Nominal("subject", cardinality=56)
palette = ts.Nominal("palette", cardinality=4)
time = ts.Numeric("time")
ref = ts.Nominal("ref", cardinality=10)
baseline = ts.Nominal("baseline", cardinality=3)

# Conceptual relationship
palette.cause(time)
baseline.cause(time)

# Data measurement
# subject.repeats(time)  # todo
palette.treats(subject, num_assignments=4)
ref.treats(subject, num_assignments=10)  # ??
baseline.treats(subject, num_assignments=3)
subject.has(time)
ref.nest_under(palette)

design = ts.Design(dv=time, ivs=[palette, baseline]).assign_data(df)

ts.infer_statistical_model_from_design(design=design)
