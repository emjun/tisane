import numpy as np

# import plotly.graph_objects as go
import tweedie

# from scipy.special import logit
# from scipy import stats
# import pandas as pd
import json
import argparse
import logging

log = logging.getLogger("")
log.setLevel(logging.ERROR)


def simulate_data_dist(
    family: str, dataMean: float = None, dataStdDev: float = None, dataSize: int = None
):
    size = dataSize or 1000

    if "GaussianFamily" == family:
        mean = dataMean or 0
        std = dataStdDev or 1

        return np.random.default_rng().normal(loc=mean, scale=std, size=size)
    elif "InverseGaussianFamily" == family:
        mean = dataMean or 1
        std = dataStdDev or 1

        return np.random.default_rng().wald(mean=mean, scale=std, size=size)
    elif "PoissonFamily" in str(family):
        lam = 1.0  # np default
        return np.random.default_rng().poisson(lam=lam, size=size)
    elif "GammaFamily" in str(family):
        shape = 2.0  # k, >= 0
        scale = 1.0  # theta, np default, >= 0

        return np.random.default_rng().gamma(shape=shape, scale=scale, size=size)
    elif "TweedieFamily" in str(family):
        mean = dataMean or 1.0
        p = 1.5  # Can be changed to update to other familiar distributions: https://en.wikipedia.org/wiki/Tweedie_distribution
        phi = 20  # this can be reset
        n = size
        return tweedie.tweedie(mu=mean, p=p, phi=phi).rvs(n)
    elif "BinomialFamily" in str(family) and "Negative" not in str(family):
        n = size  # number of trials  >= 0
        p = 0.5  # probability of success [0, 1]

        return np.random.default_rng().binomial(n=n, p=p, size=size)
    elif "NegativeBinomialFamily" in str(family):
        n = size  # number of successes, > 0
        p = 0.5  # probability of success [0, 1]

        return np.random.default_rng().negative_binomial(n=n, p=p, size=size)
    elif "MultinomialFamily" in str(family):
        cardinality = 3  # should be > 2
        n = size  # number of trials/experiments, > 0
        pvals = 1.0 / cardinality  # probability of each case

        return np.random.default_rng().multinomial(n=n, pvals=pvals, size=size)
    else:
        raise ValueError(f"Unknown distribution family: {family}")


def getTriggeredFromContext(ctx):
    if not ctx.triggered:
        return False
    return ctx.triggered[0]["prop_id"].split(".")[0]


def onlyAllowSupportedFamilyDistributions(supportedDistributions, inputDataTypes):
    def filterPred(v):
        return not ("family-options" in v and len(v["family-options"]) == 0)

    def alterAnswers(oldAnswers):
        log.info("Answers: {}".format(oldAnswers))
        alteredAnswers = {k: recCall(v) for k, v in oldAnswers.items()}

        log.info("Altered answers: {}".format(alteredAnswers))
        alteredAnswers = {k: v for k, v in alteredAnswers.items() if filterPred(v)}
        return alteredAnswers

    def recCall(inputTypes):
        if (
            "follow-up" in inputTypes
            and "answers" in inputTypes["follow-up"]
            and "question" in inputTypes["follow-up"]
        ):
            alteredAnswers = alterAnswers(inputTypes["follow-up"]["answers"])

            if len(alteredAnswers) == 1:
                return list(alteredAnswers.values())[0]
            return {
                "follow-up": {
                    "answers": alteredAnswers,
                    "question": inputTypes["follow-up"]["question"],
                }
            }
            pass
        elif "family-options" in inputTypes:
            familyOptions = [
                fo
                for fo in inputTypes["family-options"]
                if fo in supportedDistributions
            ]
            return {"family-options": familyOptions}
        elif "answers" in inputTypes and "question" in inputTypes:
            # Top-level
            alteredAnswers = alterAnswers(inputTypes["answers"])

            if len(alteredAnswers) == 1:
                # In this case, return nothing
                return {}
            return {"answers": alteredAnswers, "question": inputTypes["question"]}
        return inputTypes

    return recCall(inputDataTypes)
