from tisane.concept import Concept

from enum import Enum 
from typing import Union
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
        