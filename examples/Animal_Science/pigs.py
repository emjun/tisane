import tisane as ts
import pandas as pd

df = pd.read_csv("./examples/data/dietox.csv")

## Initialize variables with data
# Bind measures to units at the time of declaration
week = ts.Setup("Time", data=df["time"], cardinality=12)
pig = ts.Unit("Pig", data=df["pig id"])
litter = ts.Unit("Litter", data=df["litter"])
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

## With cardinality info, don't pass data
# pig = ts.Unit("Pig", cardinality=82)
# litter = ts.Unit("Litter", cardinality=22)
# week = ts.Control("Week", cardinality=12)

## Conceptual relationships
time.causes(weight)

## Data measurement relationships
# Pigs are nested within litters
pig.nests_within(litter)
# Pigs are nested within litters with at most 25 pigs per litter
# pig.nests_within(litter, number_of_instances=ts.at_most(25))


## Specify and execute query
design = ts.Design(dv=weight, ivs=[time]).assign_data(df)

ts.infer_statistical_model_from_design(design=design)
