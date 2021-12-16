
# Tisane inferred the following statistical model based on this query:  {}

import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt # for visualizing residual plots to diagnose model fit

 
def fit_model(): 

    df = pd.read_csv('examples/Exercise/exercise_simple.csv')


    model = smf.glm(formula='endurance ~ age + exercise', data=df, family=sm.families.Gaussian(sm.families.links.identity()))

    res = model.fit()
    print(res.summary())
    return model


# What should you look for in the plot? 
# If there is systematic bias in how residuals are distributed, you may want to try a new link or family function. You may also want to reconsider your conceptual and statistical models. 
# Read more here: https://sscc.wisc.edu/sscc/pubs/RegressionDiagnostics.html
def show_model_diagnostics(model): 

    res = model.fit()
    plt.clf()
    plt.grid(True)
    plt.axhline(y=0, color='r', linestyle='-')
    plt.plot(res.predict(linear=True), res.resid_pearson, 'o')
    plt.xlabel("Linear predictor")
    plt.ylabel("Residual")
    plt.show()


if __name__ == "__main__":
    model = fit_model()
    show_model_diagnostics(model)
