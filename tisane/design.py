from tisane.variable import (
    Measure,
    Unit,
    AbstractVariable,
    Has,
    Associates,
    Causes,
    Moderates,
    Nests,
    Repeats,
)
from tisane.graph import Graph
from tisane.smt.rules import (
    MainEffect,
    NoMainEffect,
    Interaction,
    NoInteraction,
    NominalDataType,
    OrdinalDataType,
    NumericDataType,
    Transformation,
    NoTransformation,
    NumericTransformation,
    CategoricalTransformation,
    LogTransform,
    SquarerootTransform,
    LogLogTransform,
    ProbitTransform,
    LogitTransform,
)
from tisane.data import Dataset

import os
from typing import List
import typing  # to use typing.Union; Union is overloaded in z3
import pandas as pd
import pydot
from z3 import *

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

        if source is not None:
            self.dataset = Dataset(source)
        else:
            self.dataset = None

    # Associate this Study Design with a Dataset
    def assign_data(self, source: typing.Union[os.PathLike, pd.DataFrame]):
        self.dataset = Dataset(source)

        return self

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

    # @return dict of Z3 consts for variables in model
    def generate_const_from_fact(self, fact_dict: dict):
        # Declare data type
        Object = DeclareSort("Object")

        # Prepare variables
        var_names_to_variables = dict()
        for v in self.get_variables():
            var_names_to_variables[v.name] = v

        main_seq = None
        interaction_seq = None
        # Get variable names

        start_name = fact_dict["start"]
        end_name = fact_dict["end"]
        # Get variables
        start_var = var_names_to_variables[start_name]
        end_var = var_names_to_variables[end_name]

        if fact_dict["function"] == "MainEffect":
            assert end_var is self.dv

            if "main_effects" not in self.consts:
                main_seq = Unit(start_var.const)
            else:
                main_seq = self.consts["main_effects"]
                main_seq = Concat(Unit(start_var.const), main_seq)
            self.consts["main_effects"] = main_seq

        elif fact_dict["function"] == "NoMainEffect":
            main_seq = Empty(SeqSort(Object))

            # If there are no main effects so far, create an empty SeqSort
            if "main_effects" not in self.consts:
                self.consts["main_effects"] = main_seq
            # Else: If there are main effects already, do nothing

        elif fact_dict["function"] == "Interaction":
            # Create set for interaction
            interaction = EmptySet(Object)
            SetAdd(interaction, start_var.const)
            SetAdd(interaction, end_var.const)
            if "interactions" not in self.consts:
                interaction_seq = Unit(interaction)
            else:
                interaction_seq = self.consts["interactions"]
                interaction_seq = Concat(Unit(interaction), interaction_seq)
            self.consts["interactions"] = interaction_seq

        elif fact_dict["function"] == "NoInteraction":
            interaction = EmptySet(Object)

            # If there are no interactions so far, create a SeqSort of Sets
            if "interactions" not in self.consts:
                interaction_seq = Unit(interaction)
                self.consts["interactions"] = interaction_seq

            # Else: If there are interactions already, do nothing

        else:
            pass

    def generate_consts(self):
        # Declare data type
        Object = DeclareSort("Object")

        # If we haven't already generated consts from facts
        if "main_effects" not in self.consts:
            main_seq = None
            # Does not use self.ivs
            nodes = list(self.graph._graph.nodes(data=True))  # get list of edges

            for (n, data) in nodes:
                n_var = data["variable"]
                if n_var is not self.dv:
                    if main_seq is None:
                        main_seq = Unit(n_var.const)
                    else:
                        main_seq = Concat(Unit(n_var.const), main_seq)

            self.consts["main_effects"] = main_seq

        if "interactions" not in self.consts:
            interactions_seq = Unit(EmptySet(Object))
            self.consts["interactions"] = interactions_seq

    # @returns the set of logical facts that this Design "embodies"
    def compile_to_facts(self) -> List:
        facts = list()  # TODO: Should be a dict?

        nodes = list(self.graph._graph.nodes(data=True))  # get list of nodes
        for (n, data) in nodes:
            n_var = data["variable"]
            if isinstance(n_var, Nominal):
                facts.append(NominalDataType(n_var.const))
            elif isinstance(n_var, Ordinal):
                facts.append(OrdinalDataType(n_var.const))
            else:
                assert isinstance(n_var, Numeric)
                facts.append(NumericDataType(n_var.const))

        edges = self.graph.get_edges()  # get list of edges

        for (n0, n1, edge_data) in edges:
            edge_type = edge_data["edge_type"]
            n0_var = gr.get_variable(n0)
            n1_var = gr.get_variable(n1)
            if edge_type == "nests":
                pass
            elif edge_type == "treat":
                pass
            else:
                pass

        return facts

    def collect_ambiguous_effects_facts(
        self, main_effects: bool, interactions: bool
    ) -> List:
        facts = list()
        edges = self.graph.get_edges()  # get list of edges

        # Declare data type
        Object = DeclareSort("Object")

        # Do we care about Main Effects?
        if main_effects:
            # What Main Effects should we consider?
            for (n0, n1, edge_data) in edges:
                edge_type = edge_data["edge_type"]
                n0_var = gr.get_variable(n0)
                n1_var = gr.get_variable(n1)
                if edge_type == "nests":
                    pass
                elif edge_type == "treat":
                    pass
                elif edge_type == "contribute":
                    facts.append(MainEffect(n0_var.const, n1_var.const))
                    facts.append(NoMainEffect(n0_var.const, n1_var.const))

        if interactions:
            # What Interaction Effects should we consider?
            # Check if the edge does not include the DV
            incoming_edges = list(self.graph._graph.in_edges(self.dv.name, data=True))

            interactions_considered = list()
            for (ie, dv, data) in incoming_edges:
                ie_var = self.graph._graph.nodes[ie]["variable"]
                for (other, dv, data) in incoming_edges:
                    # Asks about interactions even if end-user does not want to
                    # include the corresponding main effects
                    other_var = self.graph._graph.nodes[other]["variable"]
                    if (ie is not other) and (
                        {ie, other} not in interactions_considered
                    ):
                        # TODO: Add all combinatorial interactions, should we ask end-user for some interesting ones?
                        i_set = EmptySet(Object)
                        i_set = SetAdd(i_set, ie_var.const)
                        i_set = SetAdd(i_set, other_var.const)

                        facts.append(Interaction(i_set))
                        facts.append(NoInteraction(i_set))

                        interactions_considered.append({ie, other})

        return facts

    # @return additional set of logical facts that needs disambiguation depending on @param desired output_obj
    def collect_ambiguous_facts(self, output: str) -> List:

        facts = list()
        edges = self.graph.get_edges()  # get list of edges

        # Iterate over edges
        for (n0, n1, edge_data) in edges:
            edge_type = edge_data["edge_type"]
            n0_var = gr.get_variable(n0)
            n1_var = gr.get_variable(n1)
            if edge_type == "contribute":
                if output.upper() == "VARIABLE RELATIONSHIP GRAPH":
                    # Induce UNSAT in order to get end-user clarification
                    facts.append(Cause(n0_var.const, n1_var.const))
                    facts.append(Correlate(n0_var.const, n1_var.const))
            elif edge_type == "treat":
                pass
            elif edge_type == "nests":
                # TODO: Mixed Effect
                raise NotImplementedError
            else:
                pass

        # Iterate over nodes
        if output == "STATISTICAL MODEL":
            nodes = list(self.graph._graph.nodes(data=True))
            for (n, data) in nodes:
                # Check if the variable is included as a main effect
                var = data["variable"]
                if is_true(
                    BoolVal(Contains(self.consts["main_effects"], Unit(var.const)))
                ):
                    # Induce UNSAT
                    facts.append(Transformation(var.const))
                    facts.append(NoTransformation(var.const))
                    # # Induce UNSAT
                    # Depending on variable data type, add more constraints for possible transformations
                    if isinstance(var, Numeric):
                        facts.append(NumericTransformation(var.const))
                        facts.append(LogTransform(var.const))
                        facts.append(SquarerootTransform(var.const))
                    elif isinstance(var, Nominal) or isinstance(var, Ordinal):
                        facts.append(CategoricalTransformation(var.const))
                        facts.append(LogLogTransform(var.const))
                        facts.append(ProbitTransform(var.const))
                        # facts.append(LogitTransform(var.const)) # TODO: Might only make sense for binary data??

                    # TODO: If update main effect variable and it is involved in interaction, ask about or propagate automatically?

        return facts

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
