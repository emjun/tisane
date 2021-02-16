from tisane.variable import AbstractVariable
from tisane.graph import Graph

from typing import List
import pydot

"""
Class for expressing how data are collected (e.g., nesting, between-subjects, within-subjects)
"""

class Design(object): 

    ivs : List[AbstractVariable]
    dv : AbstractVariable
    unit : AbstractVariable # unit of observation and manipulation
    graph : Graph # IR

    def __init__(self, dv: AbstractVariable): 
        self.ivs = list()
        self.dv = dv
        # self.unit = unit
        # self.graph = self._create_graph(ivs=ivs, dv=dv)
        self.graph = Graph() # empty graph
        # Add dv to graph
        self.graph._add_variable(dv)

    def _create_graph(self, ivs: List[AbstractVariable], dv: AbstractVariable): 
        gr = Graph()
        for v in ivs: 
            gr.unknown(v, dv)
        
        return gr

    # TODO: Any way to get rid of ivs list? 
    # Add iv to self.ivs if iv is not already included
    def _add_iv(self, iv: AbstractVariable): 
        if iv not in self.ivs: 
            self.ivs.append(iv)
            self.graph.unknown(lhs=iv, rhs=self.dv)

    # Add edges between ivs and dv
    def _update_graph(self): 
        for v in self.ivs: 
            self.graph.unknown(lhs=v, rhs=self.dv)

    # @returns underlying graph IR
    def get_graph_ir(self): 
        return self.graph

    def get_design_vis(self): 
        graph = self.graph.get_graph_vis()

        edges = list(self.graph._graph.edges(data=True)) # get list of edges

        for (n0, n1, edge_data) in edges:         
            edge_type = edge_data['edge_type']
            if edge_type == 'treat':
                graph.add_edge(pydot.Edge(n0, n1, style='dotted', color='blue'))
            elif edge_type == 'nest':
                graph.add_edge(pydot.Edge(n0, n1, style='dotted', color='green'))
            else: 
                pass
                # raise ValueError (f"Unsupported edge type: {edge_type}")

        return graph

    def visualize_design(self): 
        p_graph = self.get_design_vis()
        
        p_graph.write_png('design_vis.png')

    # For expressing nested relationships
    def nest(self, unit: AbstractVariable, group: AbstractVariable): 
        self._add_iv(unit)
        self._add_iv(group)
        # Group -> Unit
        self.graph._add_edge(start=group, end=unit, edge_type="nest")

    # TODO: Name "treat" or "assign"?
    # Example: treat/assign student with/to tutoring
    # times for between and within?
    # Side effect: If either unit or treatment are not in the graph already, adds them to the graph first
    def treat(self, unit: AbstractVariable, treatment: AbstractVariable, times: int): 
        self._add_iv(unit)
        self._add_iv(treatment)

        self.graph._add_edge(start=treatment, end=unit, edge_type="treat")


    
    # TODO: Name "measure" or "observe"? Is this a special instance of treat? 
    # Example: measure age
    # Example: If measure a variable more than once, as long as not DV don't need special tagging with unit? 
    # How use times? between and within? 
    def randomize(self, unit: AbstractVariable, measure: AbstractVariable, times: int): 
        pass

    # TODO: Separate frequency from how manipulate? 
    # design.treat(student_id, tutoring).frequency(n=1) # default is n=1 (between)?
    # design.treat(student_id, tutoring, n=1)


    