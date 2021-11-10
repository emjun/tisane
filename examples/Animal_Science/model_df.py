# Tisane inferred the following statistical model based on this query:  {}

import pandas as pd
from pymer4.models import (
    Lmer,
)  # supports Generalized linear models with or without mixed effects
import matplotlib.pyplot as plt  # for visualizing residual plots to diagnose model fit


def fit_model():

    # Dataframe is stored in local file: data.csv
    # You may want to replace the data path with an existing data file you already have.
    # You may also set df equal to a pandas dataframe you are already working with.
    df = pd.read_csv(
        "/Users/emjun/Git/tisane/data.csv"
    )  # Make sure that the data path is correct

    model = Lmer(
        formula="Weight ~ Time + (1|Litter) + (1|Pig) + (1|Time)",
        family="gaussian",
        data=df,
    )
    print(model.fit())
    return model


# What should you look for in the plot?
# If there is systematic bias in how residuals are distributed, you may want to try a new link or family function. You may also want to reconsider your conceptual and statistical models.
# Read more here: https://sscc.wisc.edu/sscc/pubs/RegressionDiagnostics.html
def show_model_diagnostics(model):

    plt.scatter(model.fits, model.residuals)
    plt.title("Fitted values vs. Residuals")
    plt.xlabel("fitted values")
    plt.ylabel("residuals")
    plt.show()


if __name__ == "__main__":
    model = fit_model()
    show_model_diagnostics(model)
