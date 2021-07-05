import tisane as ts

import pandas as pd

csv = pd.read_csv('./examples/data/tristan2.csv')

duration = ts.Numeric("Duration"))
name = ts.Nominal("Name")
executor = ts.Nominal("executor", cardinality=2)

executor.causes(duration)
name.causes(duration)

design = ts.Design(dv=duration, ivs=[executor, name]).assign_data(csv)

ts.infer_statistical_model_from_design(design=design)
