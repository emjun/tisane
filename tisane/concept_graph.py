from tisane.concept import Concept
from tisane.statistical_model import StatisticalModel
from tisane.effect_set import EffectSet, MainEffect, InteractionEffect, MixedEffect

from enum import Enum
from typing import List, Union, Dict
from more_itertools import powerset
from collections import namedtuple
import copy
import pandas as pd
import networkx as nx


class CONCEPTUAL_RELATIONSHIP(Enum):
    CAUSE = 1
    CORRELATION = 2

    @classmethod
    def cast(self, type_str: str):
        if type_str.upper() == (
            "CAUSE"
        ):  # TODO: may want to allow for more string variability (.contains("CAUS"))
            return CONCEPTUAL_RELATIONSHIP.CAUSE
        elif type_str.upper() == "CORRELATE":
            return CONCEPTUAL_RELATIONSHIP.CORRELATION
        else:
            raise ValueError(
                f"Conceptual relationship type {type_str} not supported! Try CAUSE or CORRELATE"
            )


class ConceptGraph(object):
    _graph: nx.MultiDiGraph
    # dict of concepts in the _graph.
    # We use this rather than store concepts directly in the graph because Python passes-by-object-reference.
    # This means that the Concepts in ConceptGraph will reflect changes made to the Concept objects externally
    # _concepts : Dict[str, Concept]

    def __init__(self):
        self._graph = nx.MultiDiGraph()
        # self._concepts = dict()

    def __repr__(self):
        return str(self._graph.__dict__)

    def __str__(self):
        nodes = [n for n in self._graph.nodes()]
        edges = [e for e in self._graph.edges()]
        return f"Nodes: {str(nodes)} has {len(nodes)} concepts. Edges: {str(edges)} has {len(edges)} relationships."

    # @param gr is a MultiDiGraph to replace the underlying _graph
    def _updateGraph(self, gr: nx.MultiDiGraph):
        self._graph = gr

    def addNode(
        self, con: Concept
    ):  # concepts are indexed by their names. Concepts must have unique names.
        if not self._graph:
            self._graph = nx.MultiDiGraph()
        self._graph.add_node(con.name, concept=con)
        # self._concepts[con.name] = con

    def addEdge(self, start_con: Concept, end_con: Concept, edge_type: str):
        start_node = None
        end_node = None

        if not self.hasConcept(start_con):
            self.addNode(start_con)
        start_node = self.getConceptNode(start_con)

        if not self.hasConcept(end_con):
            self.addNode(end_con)
        end_node = self.getConceptNode(end_con)

        # Assert the start and end nodes are not None
        assert start_node
        assert end_node
        # Add edges between concept names, use the concept names later to look up the actual concept objects
        # This assumes that each concept has a unique name
        self._graph.add_edge(start_node[0], end_node[0], edge_type=edge_type)

    def hasConcept(self, con: Concept):
        return self._graph.has_node(con.name)

    # @returns handle to Node that represents the @param con Concept
    # @returns None if @param con Concept is not found in the graph
    def getConceptNode(self, con: Concept):
        for n in self._graph.nodes("concept"):
            if n[0] == con.name:
                return n
        return None

    # @returns Concept with concept_name in this conceptual graph
    def getConcept(self, concept_name: str) -> Concept:
        #

        for n in self._graph.nodes("concept"):
            if n[0] == concept_name:
                assert isinstance(n[1], Concept)
                # return self._concepts[n[0]]
                return n[1]

        return None

    def getRelationships(self, dv: Concept, relationship_type: CONCEPTUAL_RELATIONSHIP):
        tc = nx.transitive_closure(
            self._graph, reflexive=None
        )  # do not create any self loops
        return tc

    # Infer main effects from conceptual graph
    # @param set_tc is a set of edges from the transitive closure of self.graph
    def infer_main_effects(self, dv: Concept, set_tc: set):
        # Filter the transitive closure to only include those that end in @param dv
        main_effects = list()
        for relat in set_tc:
            # Check that each edge has only 2 nodes
            assert len(relat) == 2
            # Check that @param dv is the "receiving" edge
            if dv.name == relat[1]:
                # Add relationship/edge into list of possible main effects
                m_e = relat[0]
                main_effects.append(m_e)

        return main_effects

    # Infer interaction effects based on conceptual graph
    # @param set_tc is a set of edges from the transitive closure of self.graph
    def infer_interaction_effects(self, dv: Concept, set_tc: set):
        interaction_effects = list()
        for relat in set_tc:
            # Check that each edge has only 2 nodes
            assert len(relat) == 2
            # Check that @param dv is not in the edge at all
            # Would not make sense for @param dv to be in the "sending" edge for an interaction effect
            if not dv.name in relat:
                interaction_effects.append(relat)

        # TODO Get effects based on study design

        return interaction_effects

    # @param effects is a list of effects lists
    def get_all_effects_combinations(self, dv: Concept, powerset_lists: dict):

        all_effects_set = set()

        if len(powerset_lists) != 2:
            raise NotImplementedError

        assert "main" in powerset_lists.keys()
        assert "interaction" in powerset_lists.keys()
        main_effects = powerset_lists["main"]
        interaction_effects = powerset_lists["interaction"]

        for m in main_effects:
            for i in interaction_effects:
                if not m.effect and not i.effect:
                    pass
                else:
                    # set_effects = frozenset({m, i})
                    set_effects = EffectSet(dv=dv, main=m, interaction=i)
                    all_effects_set.add(set_effects)

        # TODO: check length, ALSO add as a test case
        return all_effects_set

    def cast(self, effect_type: str, effect_powerset: tuple):
        # MainEffect = namedtuple('MainEffect', 'effect')
        # InteractionEffect = namedtuple('InteractionEffect', 'effect')

        cast_effect_list = list()
        for eff in list(effect_powerset):
            if effect_type.upper() == "MAIN":
                if not eff:
                    cast_effect_list.append(MainEffect(None))
                else:
                    cast_effect_list.append(MainEffect(eff))
            elif effect_type.upper() == "INTERACTION":
                if not eff:
                    cast_effect_list.append(InteractionEffect(None))
                else:
                    cast_effect_list.append(InteractionEffect(eff))
            else:
                raise ValueError(
                    f"Effect type {effect_type} not supported! Try MAIN or INTERACTION"
                )
        return cast_effect_list

    def generate_effects_sets(self, dv: Concept):
        # Get the transitive closure of the graph (all edges)
        tc = self.getRelationships(
            dv=dv, relationship_type=CONCEPTUAL_RELATIONSHIP.CAUSE
        )
        set_tc = set(
            tc.edges()
        )  # do not get multiples, only get set of edges in the transitive closure

        # Get the main and interaction effects
        main_effects = self.infer_main_effects(dv, set_tc)
        interaction_effects = self.infer_interaction_effects(dv, set_tc)

        # Create sets of main and interaction effects
        main_powerset = powerset(main_effects)
        interaction_powerset = powerset(interaction_effects)
        main_cast = self.cast(effect_type="main", effect_powerset=main_powerset)
        interaction_cast = self.cast(
            effect_type="interaction", effect_powerset=interaction_powerset
        )
        all_effects_set = self.get_all_effects_combinations(
            dv=dv, powerset_lists={"main": main_cast, "interaction": interaction_cast}
        )

        return all_effects_set

    # @returns a subgraph (type ConceptGraph) of this ConceptGraph that treats the dv as the final "sinking" node
    def _prune_graph_for_effects_sets_generation(self, dv: Concept):
        # Create sub-graph such that dv does not have any outgoing edges
        sub_graph = self._graph.__class__()
        outer_nodes = set()  # should not exist in the subgraph
        # TODO: There might a name for this: a type of cut??
        for edge in self._graph.edges(data="edge_type"):
            out_node, in_node, edge_type = edge
            # Is it a causal relationship?
            if edge_type == CONCEPTUAL_RELATIONSHIP.CAUSE:
                # If so, exclude any edges where the DV is the cause/exogenous variable
                if dv.name == out_node:
                    # Keep track of the nodes that the DV reaches so we can remove them at a later step
                    outer_nodes.add(in_node)
                # If the DV is the receiving variable or the edge involves other causes, include
                # We will do a nother pass over the subgraph to remove any edges that involve variables the DV could cause
                else:
                    sub_graph.add_edge(out_node, in_node, edge_type=edge_type)
            else:
                assert edge_type == CONCEPTUAL_RELATIONSHIP.CORRELATION
                sub_graph.add_edge(out_node, in_node, edge_type=edge_type)

        # Do another pass to get rid of any edges that involve the DV as the cause
        edges_to_remove = list()
        for edge in sub_graph.edges(data="edge_type"):
            out_node, in_node, edge_type = edge

            # Does this edge involve nodes that should be outside the scope of this subgraph?
            if out_node in outer_nodes or in_node in outer_nodes:
                edges_to_remove.append((out_node, in_node))
        sub_graph.remove_edges_from(edges_to_remove)
        assert len(list(sub_graph.out_edges(dv.name))) == 0
        assert len(list(self._graph.out_edges(dv.name))) >= 0

        # Get the transitive closure of the sub_graph
        sub = ConceptGraph()
        sub._updateGraph(sub_graph)

        return sub

    def generate_effects_sets_with_ivs(self, ivs: List[Concept], dv: Concept):

        # Prune graph/Take subgraph from which to generate possible sets of effects
        sub = self._prune_graph_for_effects_sets_generation(dv=dv)

        # Generate effects sets
        sub.generate_effects_sets(dv=dv)

        # Filter effects sets to only include those that involve the IVs

        return sub.generate_effects_sets(dv=dv)
        # TODO: What ahppens if the ivs contain variables that receive edges from DV?  --> should check that the model is possible, raise error if not (this is in the interaction and checking layer?)
