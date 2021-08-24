
# Tisane inferred the following statistical model based on this query:  {}
import pandas as pd
from pymer4.models import Lmer # supports Generalized linear models with or without mixed effects


df = pd.read_csv('examples/Animal_Science/pigs.csv')


model = Lmer(formula='Weight ~ Time + (1|Time) + (1|Pig) + (1|Litter)', family="gaussian", data=df)
print(model.fit())
