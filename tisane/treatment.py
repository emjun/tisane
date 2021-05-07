from tisane.variable import AbstractVariable
from typing import List, Union
from z3 import *

"""
Class for expressing (i) that there is a treatment and (ii) how there is a treatment (e.g., between-subjects, within-subjects)
Used within Class Design
"""


class Treatment(object):
    unit: AbstractVariable
    treatment: AbstractVariable
    number_of_assignments: int  # 1 means Between-subjects, >1 means Within-subjects
    # graph: Graph # TODO: Maybe?

    def __init__(
        self,
        unit: AbstractVariable,
        treatment: AbstractVariable,
        number_of_assignments: int = 1,
    ):
        self.unit = unit
        self.treatment = treatment
        self.number_of_assignments = number_of_assignments

        # Maybe?
        # self.graph = Graph()
        # graph.treat(unit=unit, treatment=treatment)

        # TODO: Check that allocation is divisble?
        # TODO: Assumption that treatment is categorical, not continuous?

    # Default to between subjects
    def assign(self, number_of_assignments: int, unit: AbstractVariable = None):
        assert unit is self.unit
        self.number_of_assignments = number_of_assignments

        # TODO: Check if number_of_assignments < cardinality of treatment?
