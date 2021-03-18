from tisane.variable import AbstractVariable, Nominal, Ordinal, Numeric, Treatment, Nest, RepeatedMeasure, Has, Associate, Cause

import networkx as nx
import pydot
from typing import List, Union, Tuple

"""
Class for expressing how variables (i.e., proxies) relate to one another at a
conceptual level: cause, correlate, contribute.
"""

class Graph(object): 
    _graph : nx.MultiDiGraph

    @classmethod
    def cast(**kwargs): 
        gr = Graph()

        return gr
    
    def __init__(self): 
        self._graph = nx.MultiDiGraph()

    def __repr__(self): 
        return str(self._graph.__dict__)
        
    def __str__(self): 
        nodes = [n for n in self._graph.nodes()]
        edges = [e for e in self._graph.edges()]
        return f"Nodes: {str(nodes)} has {len(nodes)} concepts. Edges: {str(edges)} has {len(edges)} relationships."
    
    # @returns True if the variable is in the grah
    def has_variable(self, variable: AbstractVariable) -> bool: 
        return self._graph.has_node(variable.name)
    
    # @returns True if the edge between @params start and end is in the graph
    def has_edge(self, start: AbstractVariable, end: AbstractVariable, edge_type: str) -> bool: 
        # return self._graph.has_edge(start.name, end.name)

        edge = self.get_edge(start=start, end=end, edge_type=edge_type)
        
        return edge is not None
        
    # @returns tuple representing edge or None if edge is not found in graph
    def get_edge(self, start: AbstractVariable, end: AbstractVariable, edge_type: str) -> Union[Tuple, None]: 
        edges = self.get_edges()

        for (n0, n1, edge_data) in edges: 

            if n0 == start.name and n1 == end.name:  
                 if edge_type == edge_data['edge_type']: 
                    return (n0, n1, edge_data)

        return None

    # @returns handle to Node that represents the @param variable 
    # @returns None if @param variable is not found in the graph 
    def _get_variable_node(self, variable: AbstractVariable): 
        for n in self._graph.nodes('variable'): 
            if n[0] == variable.name:
                return n
        return None
    
    # Variables have unique names and are indexed by their names.
    # Variables also have a 'tag' that indicate if they are 'identifiers' for a level
    def _add_variable(self, variable: AbstractVariable, is_identifier: bool=False):  
        if not self._graph: 
            self._graph = nx.MultiDiGraph()
        self._graph.add_node(variable.name, variable=variable, is_identifier=is_identifier)

    # Add edge to graph
    # If nodes aren't already in the graph, add them
    def _add_edge(self, start: AbstractVariable, end: AbstractVariable, edge_type: str, edge_obj: Union[Treatment, Nest, RepeatedMeasure]=None): 

        # If the variables aren't in the graph, add nodes first.
        start_node = None
        end_node = None 

        if not self.has_variable(start): 
            self._add_variable(start)
        start_node = self._get_variable_node(start)

        if not self.has_variable(end): 
            self._add_variable(end)
        end_node = self._get_variable_node(end)
        # Assert the start and end nodes are not None            
        assert(start_node)
        assert(end_node)

        # This assumes that each variable has a unique name
        # Add edges between variable names, use the variable names later to look
        # up the actual variable objects 
        # Add edge using NetworkGraph's API
        if edge_type == 'treat': 
            self._graph.add_edge(start_node[0], end_node[0], edge_type=edge_type, edge_obj=edge_obj)
        elif edge_type == 'nest': 
            self._graph.add_edge(start_node[0], end_node[0], edge_type=edge_type, edge_obj=edge_obj)
        elif edge_type == 'repeat': 
            self._graph.add_edge(start_node[0], end_node[0], edge_type=edge_type, edge_obj=edge_obj)
        else: 
            self._graph.add_edge(start_node[0], end_node[0], edge_type=edge_type)

    # @returns pydot object (representing DOT graph)representing conceptual graph info
    # Iterates through internal graph object and constructs vis
    def _get_graph_vis(self): 
        graph = pydot.Dot('graph_vis', graph_type='digraph')

        edges = list(self._graph.edges(data=True)) # get list of edges

        for (n0, n1, edge_data) in edges:         
            edge_type = edge_data['edge_type']
            if edge_type == 'cause': 
                graph.add_edge(pydot.Edge(n0, n1, style='bold', color='black'))
            elif edge_type == 'correlate': 
                graph.add_edge(pydot.Edge(n0, n1, style='dotted', color='black'))
                graph.add_edge(pydot.Edge(n1, n0, style='dotted', color='black'))
            elif edge_type == 'contribute': 
                graph.add_edge(pydot.Edge(n0, n1, style='dotted', color='red'))
            else: 
                pass
                # raise ValueError (f"Unsupported edge type: {edge_type}")

        return graph
    
    def visualize_graph(self): 
        graph = self._get_graph_vis()

        graph.write_png('graph_vis.png')

    # @return List of variables represented in this graph as nodes
    def get_variables(self) -> List[AbstractVariable]:
        variables = list()

        nodes = list(self._graph.nodes(data=True))
        for (n, data) in nodes:
            n_var = data['variable']
            variables.append(n_var)

        return variables

    # @return list of nodes in graph
    def get_nodes(self) -> List:
        return list(self._graph.nodes(data=True))
    
    # @return Node representing @param variable in graph
    def get_node(self, variable: AbstractVariable): 
        nodes = self.get_nodes()

        for n in nodes: 
            if n[1]['variable'] == variable: 
                return n
    
    # @return list of edges in graph
    def get_edges(self) -> List:
        return list(self._graph.edges(data=True))

    # @return neighbors of @param variable with @param edge_type such that there is an edge of @param edge_type between @param to neighbor
    # If @param edge_type == 'ALL' then return all neighbors
    def get_neighbors(self, variable: AbstractVariable, edge_type: str='ALL'): 
    
        neighbors = self._graph.neighbors(variable.name) # nodes are referenced by their variable name

        # List of variables with edge_type
        neigh_list = list() 

        if edge_type.upper() == 'ALL': 
            return neighbors
        else: 
            for n in neighbors: 
                n_var = self.get_variable(name=n)
                if self.has_edge(start=variable, end=n_var, edge_type=edge_type): 
                    neigh_list.append(n_var)
        
        return neigh_list

    # @param name is the name of the variable we are looking for
    # @return AbstractVariable in Graph with @param name, None otherwise
    def get_variable(self, name: str) -> AbstractVariable: 
        nodes = self.get_nodes()

        for (n, data) in nodes: 
            n_var = data['variable']
            if n_var.name == name: 
                return n_var
        return None
    
    def get_predecessors(self, var: AbstractVariable): 
        if self.has_variable(var): 
            nodes = self.get_nodes()
            for n, data in nodes: 
                n_var = data['variable']
                if n_var == var: 
                    return self._graph.predecessors(n) # pass node, not variable

    # @return a list of identifiers
    def get_identifiers(self) -> List[AbstractVariable]: 
        identifiers = list() 

        nodes = self.get_nodes()

        for (n, data) in nodes: 
            is_id = data['is_identifier']
            n_var = data['variable']
            if is_id: 
                identifiers.append(n_var)
        
        return identifiers

    # Update the edge by first removing then adding
    def update_edge(self, start: AbstractVariable, end: AbstractVariable, new_edge_type: str): 
        start_node = self._get_variable_node(variable=start)
        end_node = self._get_variable_node(variable=end)

        # First remove
        assert(self._graph.has_edge(start_node[0], end_node[0]))
        self._graph.remove_edge(start_node[0], end_node[0])

        # Then add back in
        self._add_edge(start=start, end=end, edge_type=new_edge_type)

    # Add a node that identifies levels in the Graph    
    def add_identifier(self, identifier: AbstractVariable): 
        self._add_variable(variable=identifier, is_identifier=True)
    
    def add_relationship(self, relationship: Union[Has, Nest, Associate, Cause]): 
        if isinstance(relationship, Has): 
            identifier = relationship.variable
            measure = relationship.measure
            self.has(identifier, measure)
        elif isinstance(relationship, Nest): 
            base = relationship.base
            group = relationship.group 
            self.nest(base, group, relationship)
        elif isinstance(relationship, Associate): 
            lhs = relationship.lhs
            rhs = relationship.rhs 
            self.associate(lhs, rhs)
        elif isinstance(relationship, Cause): 
            cause = relationship.cause
            effect = relationship.effect  
            self.cause(cause, effect)

    # Add an edge that indicates that identifier 'has' the variable measurement
    def has(self, identifier: AbstractVariable, variable: AbstractVariable): 
        if not self.has_variable(identifier): 
            self._add_variable(variable=identifier, is_identifier=True)
        else: 
            # Update the variable to have an identifier
            (node, node_data) = self.get_node(variable=identifier)    
            node_data['is_identifier'] = True
        # Is this edge new? 
        if not self.has_edge(start=identifier, end=variable, edge_type='has'): 
            self._add_edge(start=identifier, end=variable, edge_type='has')

    # Add an ''associate'' edge to the graph 
    # Adds two edges, one in each direction 
    def associate(self, lhs: AbstractVariable, rhs: AbstractVariable): 
        # Is this edge new? 
        if not self.has_edge(start=lhs, end=rhs, edge_type='associate'): 
            assert(not self.has_edge(start=rhs, end=lhs, edge_type='associate'))
            self._add_edge(start=lhs, end=rhs, edge_type='associate')
            self._add_edge(start=rhs, end=lhs, edge_type='associate')

    # Add a causal edge to the graph 
    def cause(self, cause: AbstractVariable, effect: AbstractVariable): 
        # Is this edge new? 
        if not self.has_edge(start=cause, end=effect, edge_type='cause'): 
            self._add_edge(start=cause, end=effect, edge_type='cause')
    
    # Add an ambiguous/contribute edge to the graph
    def contribute(self, lhs: AbstractVariable, rhs: AbstractVariable): 
        # Is this edge new? 
        if not self.has_edge(start=lhs, end=rhs, edge_type='contribute'): 
            self._add_edge(start=lhs, end=rhs, edge_type='contribute')

    # Add a 'treat' edge to the graph
    def treat(self, unit: AbstractVariable, treatment: AbstractVariable, treatment_obj: Treatment): 
        # Is this edge new? 
        if not self.has_edge(start=treatment, end=unit, edge_type='treat'): 
            self._add_edge(start=treatment, end=unit, edge_type='treat', edge_obj=treatment_obj)

    # Add a 'nest' edge to the graph 
    def nest(self, base: AbstractVariable, group: AbstractVariable, nest_obj: Nest=None):
        # Is this edge new? 
        if not self.has_edge(start=base, end=group, edge_type='nest'): 
            self._add_edge(start=base, end=group, edge_type='nest', edge_obj=nest_obj)
        
    # Add a 'repeat' edge to the graph
    def repeat(self, unit: AbstractVariable, response: AbstractVariable, repeat_obj: RepeatedMeasure): 
        # Is this edge new? 
        if not self.has_edge(start=unit, end=response, edge_type='repeat'): 
            self._add_edge(start=unit, end=response, edge_type='repeat', edge_obj=repeat_obj)

    # Generate Z3 consts that correspond to nodes in this graph 
    def generate_consts(self): 
        pass

    
from tisane.smt.query_manager import QM