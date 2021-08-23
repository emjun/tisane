from abc import ABC, abstractmethod
from os import PRIO_PGRP
from tisane.variable import AbstractVariable
from tisane.data import Dataset, DataVector
from typing import Any, List
import typing  # for typing.Unit

"""
Abstract super class for all family functions.
"""


class AbstractFamily(ABC):
    variable: AbstractVariable

    def set_link(self, link: "AbstractLink"):
        self.link = link

    @abstractmethod
    def simulate_data(self):
        pass

    # TODO: Should this be an abstract super class method?
    # @abstractmethod
    # def generate_code(self):
    #     pass


class AbstractLink(ABC):
    variable: AbstractVariable

    def set_variable(self, variable: AbstractVariable):
        self.variable = variable

    @abstractmethod
    def transform_data(self, data):
        pass


class IdentityLink(AbstractLink):
    def __init__(self, variable: AbstractVariable):
        super().set_variable(variable)

    def transform_data(self, data):
        # return data
        pass


class InverseLink(AbstractLink):
    def __init__(self, variable: AbstractVariable):
        super().set_variable(variable)

    def transform_data(self, data):
        pass


class InverseSquaredLink(AbstractLink):
    def __init__(self, variable: AbstractVariable):
        super().set_variable(variable)

    def transform_data(self, data):
        # wrapper around python statsmodels?
        pass


class LogLink(AbstractLink):
    def __init__(self, variable: AbstractVariable):
        super().set_variable(variable)

    def transform_data(self, data):
        # return np.log(data)
        pass


class LogCLink(AbstractLink):
    def __init__(self, variable: AbstractVariable):
        super().set_variable(variable)

    def transform_data(self, data):
        # return np.log(data)
        pass


class LogitLink(AbstractLink):
    def __init__(self, variable: AbstractVariable):
        super().set_variable(variable)

    def transform_data(self, data):
        # wrapper around python statsmodels?
        # transformed_data = logit(data["data"])
        # return pd.DataFrame(data=transformed_data)
        pass


class ProbitLink(AbstractLink):
    def __init__(self, variable: AbstractVariable):
        super().set_variable(variable)

    def transform_data(self, data):
        # wrapper around python statsmodels?
        pass


class CauchyLink(AbstractLink):
    def __init__(self, variable: AbstractVariable):
        super().set_variable(variable)

    def transform_data(self, data):
        # wrapper around python statsmodels?
        pass


class CLogLogLink(AbstractLink):
    def __init__(self, variable: AbstractVariable):
        super().set_variable(variable)

    def transform_data(self, data):
        # wrapper around python statsmodels?
        pass


class PowerLink(AbstractLink):
    def __init__(self, variable: AbstractVariable):
        super().set_variable(variable)

    def transform_data(self, data):
        # wrapper around python statsmodels?
        # transformed_data = stats.boxcox(data["data"])[0]
        # return pd.DataFrame(data=transformed_data)
        pass


class SquarerootLink(AbstractLink):
    def __init__(self, variable: AbstractVariable):
        super().set_variable(variable)

    def transform_data(self, data):
        # wrapper around python statsmodels?
        # return sm.Power(power=.5) ??
        pass


class OPowerLink(AbstractLink):  # TODO: Is this implemented in statsmodels?
    def __init__(self, variable: AbstractVariable):
        super().set_variable(variable)

    def transform_data(self, data):
        # wrapper around python statsmodels?
        pass


class NegativeBinomialLink(AbstractLink):
    def __init__(self, variable: AbstractVariable):
        super().set_variable(variable)

    def transform_data(self, data):
        # wrapper around python statsmodels?
        pass


class LogLogLink(AbstractLink):
    def __init__(self, variable: AbstractVariable):
        super().set_variable(variable)

    def transform_data(self, data):
        # wrapper around python statsmodels?
        pass


class GaussianFamily(AbstractFamily):
    def __init__(self, variable: AbstractVariable):
        self.link = IdentityLink(variable)

    def simulate_data(self, data):
        # if "GaussianFamily" in str(fact) and "Inverse" not in str(fact):
        # if design.dataset is not None:
        #     mean = design.dataset.get_column(dv.name).mean()
        #     std = design.dataset.get_column(dv.name).std()  # np default = 1
        # else:
        #     mean = 0
        #     std = 1

        # return np.random.default_rng().normal(loc=mean, scale=std, size=size)
        pass


class InverseGaussianFamily(AbstractFamily):
    def __init__(self, variable: AbstractVariable):
        self.link = InverseSquaredLink(variable)

    def simulate_data(self):
        # if design.dataset is not None:
        #     mean = design.dataset.get_column(dv.name).mean()  # should be > 0
        #     std = design.dataset.get_column(dv.name).std()  # should be >= 0
        #     if mean <= 0 or std < 0:
        #         mean = 1
        #         std = 1

        # else:
        #     mean = 1
        #     std = 1

        # return np.random.default_rng().wald(mean=mean, scale=std, size=size)
        pass


class GammaFamily(AbstractFamily):
    def __init__(self, variable: AbstractVariable):
        self.link = InverseLink(variable)

    def simulate_data(self):
        # shape = 2.0  # k, >= 0
        # scale = 1.0  # theta, np default, >= 0

        # return np.random.default_rng().gamma(shape=shape, scale=scale, size=size)
        pass


class TweedieFamily(AbstractFamily):
    def __init__(self, variable: AbstractVariable):
        self.link = LogLink(variable)

    def simulate_data(self):
        # if design.dataset is not None:
        #     mean = design.dataset.get_column(dv.name).mean()
        # else:
        #     mean = 1.0
        # p = 1.5  # Can be changed to update to other familiar distributions: https://en.wikipedia.org/wiki/Tweedie_distribution
        # phi = 20  # this can be reset
        # n = size
        # return tweedie.tweedie(mu=mean, p=p, phi=phi).rvs(n)
        pass


class PoissonFamily(AbstractFamily):
    def __init__(self, variable: AbstractVariable):
        self.link = LogLink(variable)

    def simulate_data(self):
        # lam = 1.0  # np default
        # return np.random.default_rng().poisson(lam=lam, size=size)
        pass


class BinomialFamily(AbstractFamily):
    def __init__(self, variable: AbstractVariable):
        self.link = LogitLink(variable)

    def simulate_data(self):
        # elif "BinomialFamily" in str(fact) and "Negative" not in str(fact):
        # n = size  # number of trials  >= 0
        # p = 0.5  # probability of success [0, 1]

        # return np.random.default_rng().binomial(n=n, p=p, size=size)
        pass


class NegativeBinomialFamily(AbstractFamily):
    def __init__(self, variable: AbstractVariable):
        self.link = LogLink(variable)

    def simulate_data(self):
        # n = size  # number of successes, > 0
        # p = 0.5  # probability of success [0, 1]

        # return np.random.default_rng().negative_binomial(n=n, p=p, size=size)
        pass


class MultinomialFamily(AbstractFamily):
    def __init__(self, variable: AbstractVariable):
        self.link = LogitLink(variable)

    def simulate_data(self):
        # dv = design.dv
        # assert dv.cardinality > 2
        # n = size  # number of trials/experiments, > 0
        # pvals = 1.0 / dv.cardinality  # probability of each case

        # return np.random.default_rng().multinomial(n=n, pvals=pvals, size=size)
        # else:
        #     raise ValueError(f"Unknown distribution fact: {str(fact)}")
        pass
