import pandas as pd
import statsmodels as sm

df = pd.read_csv("data.csv") # This could be stored from assign data, --> Maybe Dataset should be from file, not in dataframe

model = smf.glm(formula=formula, data=dta, family=sm.families.Binomial()).fit()
print(model.summary())