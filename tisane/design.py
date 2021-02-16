from tisane.variable import AbstractVariable
from tisane.graph import Graph

from typing import List

"""
Class for expressing how data are collected (e.g., nesting, between-subjects, within-subjects)
"""

class Design(object): 

    ivs : List[AbstractVariable]
    dv : AbstractVariable
    unit : AbstractVariable # unit of observation and manipulation
    graph : Graph # IR

    def __init__(self, dv: AbstractVariable): 
        # self.ivs = ivs 
        self.dv: = dv
        # self.unit = unit
        # self.graph = self._create_graph(ivs=ivs, dv=dv)
        self.graph = Graph() # empty graph

    def _create_graph(self, ivs: List[AbstractVariable], dv: AbstractVariable): 
        gr = Graph()
        for v in ivs: 
            gr.unknown(v, dv)
        
        return gr

    def get_graph_ir(self): 
        return self.graph

    # For expressing nested relationships
    def nest(self, unit: AbstractVariable, group: AbstractVariable): 
        # TODO: ** ADD TO IVs (maybe not necessary since everything is in Graph)**
        # Group -> Unit
        self.graph._add_edge(start=group, end=unit, edge_type="nest")

    # TODO: Name "treat" or "assign"?
    # Example: treat/assign student with/to tutoring
    # times for between and within?
    def treat(self, unit: AbstractVariable, treatment: AbstractVariable, times: int): 
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


    