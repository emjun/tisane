from pandas.core.frame import DataFrame
from tisane.variable import (
    AbstractVariable,
    Nominal,
    Ordinal,
    Has,
    Nests,
    Repeats,
)
from tisane.graph import Graph
from tisane.data import Dataset

import os
from typing import List
import typing  # to use typing.Union; Union is overloaded in z3
import pandas as pd
import pydot

"""
Class for expressing (i) data collection structure, (ii) that there is a manipulation and (iii) how there is a manipulation (e.g., between-subjects, within-subjects)
Relies on Class Treatment, Nests, Repeats
"""

interaction_effects = list()


class Design(object):
    dv: AbstractVariable
    ivs: List[AbstractVariable]
    graph: Graph  # IR
    dataset: Dataset

    def __init__(
        self,
        dv: AbstractVariable,
        ivs: List[AbstractVariable],
        source: typing.Union[os.PathLike, pd.DataFrame] = None,
    ):
        self.dv = dv

        self.ivs = ivs  # TODO: May want to replace this if move away from Design as Query object

        self.graph = Graph()  # empty graph

        # Add all variables to the graph
        # Add dv
        self._add_variable_to_graph(self.dv)
        # Add all ivs
        for v in ivs:
            self._add_variable_to_graph(v)

        # Add any nesting relationships involving IVs that may be implicit
        self._add_nesting_relationships_to_graph()

        # Add variables that the identifiers have
        self._add_identifiers_has_relationships_to_graph()

        if source is not None:
            self.dataset = Dataset(source)
        else:
            self.dataset = None

    # Calculates and assigns cardinality to variables if cardinality is not already specified
    # If calculated cardinality differs from cardinality estimated from the data, raises a ValueError
    def check_variable_cardinality(self):
        variables = self.graph.get_variables()

        for v in variables:
            if isinstance(v, Ordinal):
                assert self.dataset is not None
                assert isinstance(self.dataset, Dataset)
                calculated_cardinality = v.calculate_cardinality_from_data(
                    data=self.dataset
                )

                if calculated_cardinality > v.cardinality:
                    diff = calculated_cardinality - v.cardinality
                    raise ValueError(
                        f"Variable {v.name} is specified to have cardinality = {v.cardinality}. However, in the data provided, {v.name} has {calculated_cardinality} unique values. There appear to be {diff} more categories in the data than you expect."
                    )

    # Associate this Study Design with a Dataset
    def assign_data(self, source: typing.Union[os.PathLike, pd.DataFrame]):
        self.dataset = Dataset(source)

        self.check_variable_cardinality()

        return self

    def has_data(self) -> bool:
        return self.dataset is not None

    def get_data(self) -> pd.DataFrame:
        if self.dataset is not None:
            return self.dataset.get_data()
        # else
        return None

    def _add_variable_to_graph(self, variable: AbstractVariable):
        for r in variable.relationships:
            self.graph.add_relationship(relationship=r)

    def _add_nesting_relationships_to_graph(self):
        variables = self.graph.get_variables()

        for v in variables:
            relationships = v.relationships

            for r in relationships:
                if isinstance(r, Nests):
                    self.graph.add_relationship(relationship=r)

    def _add_identifiers_has_relationships_to_graph(self):
        identifiers = self.graph.get_identifiers()

        for unit in identifiers:
            # Does this unit have any other relationships/edges not already in the graph?
            relationships = unit.relationships

            for r in relationships:
                if isinstance(r, Has):
                    measure = r.measure
                    if not self.graph.has_edge(
                        start=unit, end=measure, edge_type="has"
                    ):
                        self.graph.add_relationship(relationship=r)

    # def _add_ivs(self, ivs: List[typing.Union[Treatment, AbstractVariable]]):

    #     for i in ivs:
    #         if isinstance(i, AbstractVariable):
    #             # TODO: Should the default be 'associate' instead of 'contribute'??
    #             self.graph.contribute(lhs=i, rhs=self.dv)

    #         elif isinstance(i, Treatment):
    #             unit = i.unit
    #             treatment = i.treatment

    #             self.graph.treat(unit=unit, treatment=treatment, treatment_obj=i)

    #             # Add treatment edge
    #             self.graph.contribute(lhs=treatment, rhs=self.dv)

    def _add_groupings(self, groupings: List[typing.Union[Nests, Repeats]]):
        for g in groupings:

            if isinstance(g, Nests):
                unit = g.unit
                group = g.group

                self.graph.nests(unit=unit, group=group, nest_obj=g)

            elif isinstance(g, Repeats):
                unit = g.unit
                response = g.response

                self.graph.repeat(unit=unit, response=response, repeat_obj=g)

    # TODO: Should be class method?
    # Create Design object from a @param Graph object
    # Useful for when moving between states Design - Graph - StatisticalModel
    # E.g., gr = infer_from(design, 'variable relationship graph') then infer_from (gr, 'statistical model')
    # TODO: Not sure if @param graph could be StatisticalModel as well...?
    def create_from(graph: Graph):
        raise NotImplementedError

        # Might have some logical facts "baked in" so would not have to ask for the same facts all the time...?
        # Could store some of this info in the edges? or as separate properties/piv?

        # TODO: Update rest of object in order to reflect updates to graph

    # @return IV and DV variables
    def get_variables(self):
        variables = list()
        variables = self.ivs + [self.dv]

        return variables

    def get_data_for_variable(self, variable: AbstractVariable):

        # Does design object have data?
        if self.dataset is not None:
            return self.dataset.get_column(variable.name)

        return None
        # Design object has no data, simulate data
        # return simulate_data(variable)

    # def _create_graph(self, ivs: List[AbstractVariable], dv: AbstractVariable):
    #     gr = Graph()
    #     for v in ivs:
    #         gr.contribute(v, dv)

    #     return gr

    # TODO: Any way to get rid of ivs list?
    # Add iv to self.ivs if iv is not already included
    def _add_iv(self, iv: AbstractVariable):
        if iv not in self.ivs:
            self.ivs.append(iv)
            self.graph.contribute(lhs=iv, rhs=self.dv)

    # Set self.dv to be @param dv
    # Assumes self.dv was None before
    def set_dv(self, dv: AbstractVariable):
        assert self.dv is None
        self.dv = dv
        self.graph._add_variable(dv)

    # @returns underlying graph IR
    def get_graph_ir(self):
        return self.graph

    def get_design_vis(self):
        graph = self.graph._get_graph_vis()

        edges = list(self.graph._graph.edges(data=True))  # get list of edges

        for (n0, n1, edge_data) in edges:
            edge_type = edge_data["edge_type"]
            if edge_type == "treat":
                graph.add_edge(pydot.Edge(n0, n1, style="dotted", color="blue"))
            elif edge_type == "nests":
                graph.add_edge(pydot.Edge(n0, n1, style="dotted", color="green"))
            else:
                pass
                # raise ValueError (f"Unsupported edge type: {edge_type}")

        return graph

    def visualize_design(self):
        p_graph = self.get_design_vis()

        p_graph.write_png("design_vis.png")

    # TODO: Update if move to more atomic API
    # @returns the number of levels involved in this study design
    def get_number_of_levels(self):
        identifiers = self.graph.get_identifiers()

        return len(identifiers)
