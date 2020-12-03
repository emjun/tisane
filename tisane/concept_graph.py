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
        if not self.hasConcept(start_con): 
            self.addNode(start_con)
        if not self.hasConcept(end_con): 
            self.addNode(end_con)
            
        self._graph.add_edge(start_con, end_con, edge_type=edge_type)

    def hasConcept(self, con: Concept): 
        return self._graph.has_node(con.name)