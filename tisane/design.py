from tisane.variable import AbstractVariable
from tisane.graph import Graph

from typing import List

class Design(object): 

    ivs : List[AbstractVariable]
    dv : AbstractVariable
    graph : Graph # IR

    def __init__(self, ivs: List[AbstractVariable], dv: AbstractVariable): 
        self.ivs = ivs 
        self.dv: = dv

        # TODO: For IVs: Create Graph with unknown edges (Graph is an IR!)

    # For expressing nested relationships
    def nest(unit: AbstractVariable, group: AbstractVariable): 
        # for nest: 
        # TODO: Add nest edges

    def assign(unit: AbstractVariable, treatment: AbstractVariable): 
        pass