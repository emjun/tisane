import tisane as ts
import pandas as pd
import os

os.chdir(os.path.dirname(__file__))
os.chdir("..")

df = pd.read_csv("./Animal_Science/pigs.csv")

## Initialize variables with data
# Bind measures to units at the time of declaration
week = ts.SetUp("Time", cardinality=12)
pig = ts.Unit("Pig", cardinality=82) # 82 pigs
litter = ts.Unit("Litter", cardinality=22) # 22 litters
# Each pig has 1 instance of an ordinal Evit measure
vitamin_e = pig.ordinal(
    "Evit", order=["Evit000", "Evit100", "Evit200"], number_of_instances=1
)
# Each pig has 1 instance of an ordinal Cu measure
copper = pig.ordinal("Cu", order=["Cu000", "Cu035", "Cu175"], number_of_instances=1)
# Each pig has for each value of week 1 instance of a numeric Weight measure
# Also: Each pig has 1 instance of a Weight measure corresponding to each week
weight = pig.numeric("Weight", number_of_instances=week)
# Each pig has for each value of week 1 instance of a numeric Feed consumption measure
feed = pig.numeric("Feed consumption", number_of_instances=week)

## Conceptual relationships
week.causes(weight)

## Data measurement relationships
# Pigs are nested within litters
pig.nests_within(litter)

## Specify and execute query
design = ts.Design(dv=weight, ivs=[week]).assign_data(df)

ts.infer_statistical_model_from_design(design=design)