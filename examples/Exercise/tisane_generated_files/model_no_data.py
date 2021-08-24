
# Tisane inferred the following statistical model based on this query:  {}

import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf


# There was no data assigned to the Design. Add data below. 
path = '' # Specify path to data if loading from a csv
df = pd.read_csv(path)
# If loading from a pandas Dataframe, alias dataframe with variable df
# df = <your pandas Dataframe>


model = smf.glm(formula='endurance ~ age + exercise', data=df, family=sm.families.Gaussian(sm.families.links.identity()))
res = model.fit()
print(res.summary())
