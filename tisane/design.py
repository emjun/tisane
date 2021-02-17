from tisane.variable import AbstractVariable
from tisane.graph import Graph
from tisane.smt.rules import Cause, Correlate, Interaction, NoInteraction

from typing import List, Union
import pydot
from z3 import *

"""
Class for expressing how data are collected (e.g., nesting, between-subjects, within-subjects)
"""

class Design(object): 

    ivs : List[AbstractVariable]
    dv : AbstractVariable
    unit : AbstractVariable # unit of observation and manipulation
    graph : Graph # IR

    consts : dict # Dict of Z3 consts involved in Design

    def __init__(self, dv: AbstractVariable): 
        self.ivs = list()
        self.dv = dv
        # self.unit = unit
        # self.graph = self._create_graph(ivs=ivs, dv=dv)
        self.graph = Graph() # empty graph
        # Add dv to graph
        self.graph._add_variable(dv)

        self.consts = dict()

    # @return IV and DV variables
    def get_variables(self): 
        variables = list()
        variables = self.ivs + [self.dv]

        return variables

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

    # @return dict of Z3 consts for variables in model
    def generate_consts(self): 
        consts_to_variables = dict() # used for post-processing query results

        main_seq = None
        # Does not use self.ivs
        nodes = list(self.graph._graph.nodes(data=True)) # get list of edges

        for (n, data) in nodes: 
            n_var = data['variable']
            if n_var is not self.dv: 
                if main_seq is None: 
                    main_seq = Unit(n_var.const)
                else: 
                    main_seq = Concat(Unit(n_var.const), main_seq)
            
            # Add to consts_to_variables dict for post-processing query
            consts_to_variables[n_var.const] = n_var

        self.consts['main_effects'] = main_seq

        # TODO: There are no interactions yet until end-user provides info or we do some analysis...?
        interactions_seq = None
        self.consts['interactions'] = interactions_seq

        return consts_to_variables 
        
    # Return the set of logical facts that this Design "embodies"
    def compile_to_facts(self) -> List: 
        facts = list()
        
        edges = list(self.graph._graph.edges(data=True)) # get list of edges

        for (n0, n1, edge_data) in edges: 
            edge_type = edge_data['edge_type']
            n0_var = self.graph._graph.nodes[n0]['variable']
            n1_var = self.graph._graph.nodes[n1]['variable']
            if edge_type == 'nest': 
                pass
            elif edge_type == 'treat': 
                pass
            
        return facts

    # Return additional set of logical facts that needs disambiguation
    def collect_ambiguous_facts(self) -> List: 
        facts = list()
        edges = list(self.graph._graph.edges(data=True)) # get list of edges

        for (n0, n1, edge_data) in edges:         
            edge_type = edge_data['edge_type']
            n0_var = self.graph._graph.nodes[n0]['variable']
            n1_var = self.graph._graph.nodes[n1]['variable']
            if edge_type == 'unknown':
                # induce UNSAT in order to get end-user clarification
                facts.append(Cause(n0_var.const, n1_var.const))
                facts.append(Correlate(n0_var.const, n1_var.const))
            else: 
                pass
        
        # Are there any interactions we should include?
        # Check if the edge does not include the DV
        incoming_edges = list(self.graph._graph.in_edges(self.dv.name, data=True))
        # import pdb; pdb.set_trace()
        interactions_considered = list()
        for (ie, dv, data) in incoming_edges: 
            ie_var = self.graph._graph.nodes[ie]['variable']
            for (other, dv, data) in incoming_edges: 
                other_var = self.graph._graph.nodes[other]['variable']
                if (ie is not other) and ({ie, other} not in interactions_considered):             
                    # TODO: Add all combinatorial interactions, should we ask end-user for some interesting ones? 
                    facts.append(Interaction(ie_var.const, other_var.const))
                    facts.append(NoInteraction(ie_var.const, other_var.const))

                    interactions_considered.append({ie, other})

        return facts

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


    