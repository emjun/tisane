import tisane as ts
import pandas as pd

# Load data
df = pd.read_csv("./radon_data_combined.csv")

## Initialize variables
household = ts.Unit("household")
# Each household has 1 instance of a numeric y measure
radon = household.numeric("y", number_of_instances=1)
# Each household has 1 instance of a nominal x measure
is_first_floor = household.nominal("x", number_of_instances=1)
county = ts.Unit("county")
# Each county has 1 instance of a numeric u.full measure
uranium = county.numeric("u.full", number_of_instances=1)

## Conceptual relationships
is_first_floor.associates_with(radon)
uranium.associates_with(radon)

## Data measurement relationships
# Households are nested within counties
household.nests_within(county)

# Specify and execute query
design = ts.Design(dv=radon, ivs=[is_first_floor, uranium]).assign_data(df)

ts.infer_statistical_model_from_design(design=design)


## EXPERIMENT: Add "weights" to query 
# TODO: Look at Z3 hard/soft constraint/weighting API
design = ts.Design(dv=radon)
design.specify_must_have_iv(is_first_floor)
design.specify_must_have_iv(uranium)

design.specify_would_be_nice_to_have(is_first_floor)
design.specify_would_be_nice_to_have(uranium)

design = ts.Design(dv=radon, ivs={'must_have': [is_first_floor], 'would_be_nice_to_have': [uranium]})
