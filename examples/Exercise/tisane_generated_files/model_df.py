
# Tisane inferred the following statistical model based on this query:  {}

import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf


# Dataframe is stored in local file: data.csv
# You may want to replace the data path with an existing data file you already have.
# You may also set df equal to a pandas dataframe you are already working with. 
df = pd.read_csv('data.csv') # Make sure that the data path is correct


model = smf.glm(formula='endurance ~ age + exercise', data=df, family=sm.families.Gaussian(sm.families.links.identity()))
res = model.fit()
print(res.summary())
