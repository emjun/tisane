from tisane.variable import AbstractVariable
from tisane.family import AbstractFamily, AbstractLink
from tisane.data import Dataset
from typing import Set
import typing  # for Union
import os
import pandas as pd


class StatisticalModel:
    dependent_variable: AbstractVariable
    main_effects: Set[AbstractVariable]
    interaction_effects: Set[AbstractVariable]
    random_effects: Set[AbstractVariable]
    family_function: AbstractFamily
    link_function: AbstractLink
    dataset: Dataset

    def __init__(
        self,
        dependent_variable: AbstractVariable,
        main_effects: Set[AbstractVariable],
        interaction_effects: Set[AbstractVariable],
        random_effects: Set[AbstractVariable],
        family_function: AbstractFamily,
        link_function: AbstractLink,
    ):
        self.dependent_variable = dependent_variable
        self.main_effects = main_effects
        self.interaction_effects = interaction_effects
        self.random_effects = random_effects
        self.family_function = family_function
        self.link_function = link_function
        self.dataset = None  # Default is that there is no data until assigned

    def get_independent_variables(self):
        ivs = set()
        ivs = ivs.union(self.main_effects)
        ivs = ivs.union(self.interaction_effects)
        ivs = ivs.union(self.random_effects)

        return ivs

    def get_dependent_variable(self):
        return self.dependent_variable

    # @returns this statistical model's data
    def get_data(self):

        return self.dataset

    # Add data to this statistical model
    def assign_data(self, source: typing.Union[os.PathLike, pd.DataFrame]):
        if isinstance(source, Dataset):
            self.dataset = source
        else:
            self.dataset = Dataset(source)

        return self

    # @returns bool val if self.dataset is not None
    def has_data(self):
        return self.dataset is not None

    def has_random_effects(self):
        return len(self.random_effects) > 0
