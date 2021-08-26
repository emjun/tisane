
# Tisane inferred the following statistical model based on this query:  {}
import pandas as pd
from pymer4.models import Lmer # supports Generalized linear models with or without mixed effects
import altair as alt
import matplotlib.pyplot as plt

df = pd.read_csv('examples/Animal_Science/pigs.csv')


model = Lmer(formula='Weight ~ Time + (1|Time) + (1|Pig) + (1|Litter)', family="gaussian", data=df)
print(model.fit())

plt.scatter(model.fits, model.residuals)
plt.title("title")
plt.xlabel("fitted values")
plt.ylabel("residuals")
plt.show()

import pdb; pdb.set_trace()
source = pd.DataFrame({
    'fitted': model.fits,
    'residuals': model.residuals
})
# points = alt.Chart(source).mark_point().encode(
#     x='fitted:Q',
#     y='residual:Q'
# )

# text = points.mark_text(
#     align='left',
#     baseline='middle',
#     dx=7
# ).encode(
#     text='label'
# )

# points + text


alt.Chart(source).mark_point().encode(
    x='fitted',
    y='residuals',
).interactive()

