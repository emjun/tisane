from tisane.concept import Concept

from enum import Enum 
from typing import Union
from more_itertools import powerset
import copy 
import pandas as pd
import networkx as nx

class CONCEPTUAL_RELATIONSHIP(Enum): 
    CAUSE = 1
    CORRELATION = 2

    @classmethod 
    def cast(self, type_str: str): 
        if type_str.upper() == ('CAUSE'): # TODO: may want to allow for more string variability (.contains("CAUS"))
            return CONCEPTUAL_RELATIONSHIP.CAUSE
        elif type_str.upper() == 'CORRELATE':
            return CONCEPTUAL_RELATIONSHIP.CORRELATION
        else: 
            raise ValueError(f"Conceptual relationship type {type_str} not supported! Try CAUSE or CORRELATE")


class ConceptGraph(object): 
    _graph : nx.MultiDiGraph
    

    def __init__(self): 
        self._graph = nx.MultiDiGraph()

    def __repr__(self): 
        return str(self._graph.__dict__)
    def __str__(self): 
        list_elts = [n.__hash__() for n in self._graph]
        return f"{str(list_elts)} has {len(list_elts)} elts"

    def addNode(self, con: Concept):  # concepts are indexed by their names. Concepts must have unique names.
        if not self._graph: 
            self._graph = nx.MultiDiGraph()
        self._graph.add_node(con.name, concept=con)
    
    def addEdge(self, start_con: Concept, end_con: Concept, edge_type: str): 
        start_node = None
        end_node = None 

        # import pdb; pdb.set_trace()
        if not self.hasConcept(start_con): 
            self.addNode(start_con)
        start_node = self.getConcept(start_con)

        if not self.hasConcept(end_con): 
            self.addNode(end_con)
        end_node = self.getConcept(end_con)
            
        # Assert the start and end nodes are not None            
        assert(start_node)
        assert(end_node)
        # Add edges between concept names, use the concept names later to look up the actual concept objects
        # This assumes that each concept has a unique name
        self._graph.add_edge(start_node[0], end_node[0], edge_type=edge_type)

    def hasConcept(self, con: Concept): 
        return self._graph.has_node(con.name)

    # @returns handle to Node that represents the @param con Concept
    # @returns None if @param con Concept is not found in the graph 
    def getConcept(self, con: Concept): 
        for n in self._graph.nodes('concept'): 
            if n[0] == con.name:
                return n
        return None

    def getRelationships(self, dv: Concept, relationship_type: CONCEPTUAL_RELATIONSHIP): 
        # G = self._graph
        # TC = copy.deepcopy(G)
        # for v in G:
        #     import pdb; pdb.set_trace()
        #     edges = ((v, w) for u, w in nx.edge_dfs(G, v))
        #     TC.add_edges_from(edges)
        # import pdb; pdb.set_trace()
        tc = nx.transitive_closure(self._graph, reflexive=None) # do not create any self loops
        return tc

    # @param set_tc is a set of edges from the transitive closure of self.graph
    def infer_main_effects(self, dv: Concept, set_tc: set): 
        # Infer main effects from conceptual graph 

        # Filter the transitive closure to only include those that end in @param dv
        main_effects = list()
        for relat in set_tc:     
            # Check that each edge has only 2 nodes
            assert(len(relat) == 2)
            # Check that @param dv is the "receiving" edge
            if dv.name == relat[1]: 
                # add relationship/edge into list of possible main effects
                m_e = relat[0]
                main_effects.append(m_e)

        return main_effects

    # @param set_tc is a set of edges from the transitive closure of self.graph
    def infer_interaction_effects(self, dv: Concept, set_tc: set): 
        # Infer interaction effects based on conceptual graph 
        interaction_effects = list()
        for relat in set_tc: 
            # Check that each edge has only 2 nodes
            assert(len(relat) == 2)
            # Check that @param dv is not in the edge at all 
            # Would not make sense for @param dv to be in the "sending" edge for an interaction effect
            if not dv.name in relat: 
                interaction_effects.append(relat)
        
        # TODO Get effects based on study design

        return interaction_effects

    # @param effects is a list of effects lists 
    def get_all_effects_combinations(self, powerset_lists: dict): 
    
        all_effects_set = set()

        if len(powerset_lists) != 2: 
            raise NotImplementedError
        
        main_effects = powerset_lists['main']
        interaction_effects = powerset_lists['interaction']

        for m in main_effects:
            for i in interaction_effects:
                set_effects = frozenset({m, i})
                all_effects_set.add(set_effects)


        # TODO: check length, ALSO add as a test case
        return all_effects_set
        

    def generate_effects_sets(self, dv: Concept): 
        # Get the transitive closure of the graph (all edges)
        tc = self.getRelationships(dv=dv, relationship_type=CONCEPTUAL_RELATIONSHIP.CAUSE)
        set_tc = set(tc.edges()) # do not get multiples, only get set of edges in the transitive closure

        # Get the main and interaction effects
        main_effects = self.infer_main_effects(dv, set_tc)
        interaction_effects = self.infer_interaction_effects(dv, set_tc)

        # Create sets of main and interaction effects
        main_powerset = powerset(main_effects)
        interaction_powerset = powerset(interaction_effects)
        all_effects_set = self.get_all_effects_combinations({'main': list(main_powerset), 'interaction': list(interaction_powerset)})
        
        return all_effects_set
        