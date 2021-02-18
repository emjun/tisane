from tisane.variable import AbstractVariable
from tisane.graph import Graph
from tisane.smt.rules import Cause, Correlate, Interaction, NoInteraction

from typing import List, Union
import pydot
from z3 import *

"""
Class for expressing (i) that there is a manipulation and (ii) how there is a manipulation (e.g., between-subjects, within-subjects)
Used within Class Design
"""
class Treatment(object): 
    unit: AbstractVariable
    manipulation: AbstractVariable
    number_of_assignments: int # 1 means Between-subjects, >1 means Within-subjects

    def __init__(self, unit: AbstractVariable, manipulation: AbstractVariable, number_of_assignments: int=1): 
        self.unit = unit
        self.manipulation = manipulation
        self.number_of_assignments = number_of_assignments
        
        # TODO: Check that allocation is divisble? 
        # TODO: Assumption that manipulation is categorical, not continuous? 
    
    # Default to between subjects
    def assign(self, number_of_assignments: int, unit: AbstractVariable=None): 
        assert(unit is self.unit)
        self.number_of_assignments = number_of_assignments

        # TODO: Check if number_of_assignments < cardinality of manipulation?

"""
Together with Class Treatment, Class for expressing (i) data collection structure, (ii) that there is a manipulation and (iii) how there is a manipulation (e.g., between-subjects, within-subjects)
Relies on Class Treatment
"""
class Design(object): 

    ivs : List[AbstractVariable]
    dv : AbstractVariable
    unit : AbstractVariable # unit of observation and manipulation
    treatments : List[Treatment] # list of treatments applied in this design
    graph : Graph # IR

    consts : dict # Dict of Z3 consts involved in Design

    def __init__(self, dv: AbstractVariable): 
        self.ivs = list()
        self.dv = dv
        self.treatments = list() 
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
        # consts_to_variables = dict() # used for post-processing query results

        main_seq = None
        # Does not use self.ivs
        nodes = list(self.graph._graph.nodes(data=True)) # get list of edges
        edges = list(self.graph._graph.edges(data=True)) # get list of edges

        # for (n, data) in nodes: 
        #     n_var = data['variable']
        #     if n_var is not self.dv: 
        #         if main_seq is None: 
        #             main_seq = Unit(n_var.const)
        #         else: 
        #             main_seq = Concat(Unit(n_var.const), main_seq)
        for (n0, n1, edge_data) in edges: 
            edge_type = edge_data['edge_type']

            if edge_type == 'unknown_main': 
                n0_var = self.graph._graph.nodes[n0]['variable']
                n1_var = self.graph._graph.nodes[n1]['variable']
                assert(n1_var is self.dv)

                if main_seq is None: 
                    main_seq = Unit(n0_var.const)
                else: 
                    main_seq = Concat(Unit(n0_var.const), main_seq)

            # Add to consts_to_variables dict for post-processing query
            # consts_to_variables[n_var.const] = n_var
        
        self.consts['main_effects'] = main_seq

        # TODO: There are no interactions yet until end-user provides info or we do some analysis...?
        interactions_seq = None
        self.consts['interactions'] = interactions_seq

        # return consts_to_variables 

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

    
    # @return additional set of logical facts that needs disambiguation depending on @param desired output_obj
    def collect_ambiguous_facts(self, **kwargs) -> List: 
        def select_main_effect(iv_var: AbstractVariable, dv_var: AbstractVariable): 
            while True: 
                ans = str(input(f'Are you interested in explaining {dv_var.name} using {iv_var.name}? Y or N:'))
                if ans.upper() == 'Y': 
                    print(f"Ok, will use {iv_var.name} as an IV in the statistical model.")
                    return True
                elif ans.upper() == 'N': 
                    print(f"Ok, will not use {iv_var.name} as an IV in the statistical model.")
                    return False
                else: 
                    raise ValueError(f"Unsupported input: {ans}")

        output = kwargs['output']

        facts = list()
        edges = list(self.graph._graph.edges(data=True)) # get list of edges

        for (n0, n1, edge_data) in edges:         
            edge_type = edge_data['edge_type']
            n0_var = self.graph._graph.nodes[n0]['variable']
            n1_var = self.graph._graph.nodes[n1]['variable']
            if edge_type == 'unknown':
                if output.upper() == 'VARIABLE RELATIONSHIP GRAPH': 
                    # Induce UNSAT in order to get end-user clarification
                    facts.append(Cause(n0_var.const, n1_var.const))
                    facts.append(Correlate(n0_var.const, n1_var.const))
                elif output.upper() == 'STATISTICAL MODEL':
                    # Should we include n0_var as a main effect?
                    if (n1_var is self.dv): 
                        # Ask user
                        user_decision = select_main_effect(n0_var, n1_var)
                        if user_decision: 
                            # Update edge
                            self.graph.update_edge(n0_var, n1_var, new_edge_type='unknown_main')
            elif edge_type == 'treat': 
                pass
            elif edge_type == 'nest': 
                # TODO: Mixed Effect
                raise NotImplementedError
            else: 
                pass
        
        # Are there any interactions we should include?
        # Check if the edge does not include the DV
        incoming_edges = list(self.graph._graph.in_edges(self.dv.name, data=True))
        
        interactions_considered = list()
        for (ie, dv, data) in incoming_edges: 
            ie_var = self.graph._graph.nodes[ie]['variable']
            for (other, dv, data) in incoming_edges: 
                # Asks about interactions even if end-user does not want to
                # include the corresponding main effects
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
    def treat(self, unit: AbstractVariable, treatment: AbstractVariable, how: str=None): 
        self._add_iv(unit)
        self._add_iv(treatment)

        number_of_assignments = 1
        if how is not None: 
            if how == "within": 
                # Assume fully factorial design
                # Otherwise, must use treat then assign idiom
                number_of_assignments = treatment.get_cardinality()
        self.treatments.append(Treatment(unit=unit, manipulation=treatment, number_of_assignments=number_of_assignments))
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