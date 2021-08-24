
# Tisane inferred the following statistical model based on this query:  {}

import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf


df = pd.read_csv('examples/Exercise/exercise_simple.csv')


model = smf.glm(formula='endurance ~ age + exercise', data=df, family=sm.families.Gaussian(sm.families.links.identity()))
res = model.fit()
print(res.summary())
