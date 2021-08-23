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
    data: Dataset

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
        self.data = None  # Default is that there is no data until assigned

    def get_independent_variables(self):
        ivs = set()
        ivs = ivs.union(self.main_effects)
        ivs = ivs.union(self.interaction_effects)
        ivs = ivs.union(self.random_effects)

        return ivs

    def get_dependent_variable(self):
        return self.dependent_variable

    # Add data to this statistical model
    def assign_data(self, source: typing.Union[os.PathLike, pd.DataFrame]):
        self.dataset = Dataset(source)

        return self

    def has_random_effects(self):
        return len(self.random_effects) > 0
