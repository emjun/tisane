
# Tisane inferred the following statistical model based on this query:  {}
import pandas as pd
from pymer4.models import Lmer # supports Generalized linear models with or without mixed effects


df = pd.read_csv('examples/Group_Exercise/exercise_group.csv')


model = Lmer(formula='pounds_lost ~ motivation + treatment + (1|group)', family="gaussian", data=df)
print(model.fit())
