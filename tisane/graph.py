from tisane.variable import AbstractVariable

import networkx as nx

"""
Class for expressing how variables (i.e., proxies) relate to one another at a
conceptual level: cause, correlate, unknown.
"""

class Graph(object): 
    _graph : nx.MultiDiGraph
    
    def __init__(self): 
        self._graph = nx.MultiDiGraph()

    def __repr__(self): 
        return str(self._graph.__dict__)
        
    def __str__(self): 
        nodes = [n for n in self._graph.nodes()]
        edges = [e for e in self._graph.edges()]
        return f"Nodes: {str(nodes)} has {len(nodes)} concepts. Edges: {str(edges)} has {len(edges)} relationships."

    # Variables have unique names and are indexed by their names.
    def _add_variable(self, variable: AbstractVariable):  
        if not self._graph: 
            self._graph = nx.MultiDiGraph()
        self._graph.add_node(variable.name, variable=variable)

    # @returns node of underlying _graph if in graph, otherwise None
    def _has_variable(self, variable: AbstractVariable): 
        return self._graph.has_node(variable.name)
    
    # @returns handle to Node that represents the @param variable 
    # @returns None if @param variable is not found in the graph 
    def _get_variable_node(self, variable: Variable): 
        for n in self._graph.nodes('variable'): 
            if n[0] == variable.name:
                return n
        return None

    def _add_edge(self, start: AbstractVariable, end: AbstractVariable, edge_type: str): 

        # If the variables aren't in the graph, add nodes first.
        start_node = None
        end_node = None 

        if not self._has_variable(start): 
            self._add_variable(start)
        start_node = self._get_variable_node(start)

        if not self._has_variable(end): 
            self._add_variable(end)
        end_node = self._get_variable_node(end)
        # Assert the start and end nodes are not None            
        assert(start_node)
        assert(end_node)

        # This assumes that each variable has a unique name
        # Add edges between variable names, use the variable names later to look
        # up the actual variable objects 
        # Add edge using NetworkGraph's API
        self._graph._add_edge(start_node[0], end_node[0], edge_type=edge_type)

    def correlate(lhs: AbstractVariable, rhs: AbstractVariable): 
        self._add_edge(start=lhs, end=rhs, edge_type='correlate')

    def cause(lhs: AbstractVariable, rhs: AbstractVariable): 
        self._add_edge(start=lhs, end=rhs, edge_type='cause')
    
    # TODO: Could rename to unspecify or something like that
    def unknown(lhs: AbstractVariable, rhs: AbstractVariable): 
        self._add_edge(start=lhs, end=rhs, edge_type='unknown')
