from tisane.variable import AbstractVariable, Nominal, Ordinal, Numeric
from tisane.graph import Graph
from tisane.smt.rules import Cause, Correlate, MainEffect, NoMainEffect, Interaction, NoInteraction, NominalDataType, OrdinalDataType, NumericDataType, Transformation, NoTransformation, NumericTransformation, CategoricalTransformation, LogTransform, SquarerootTransform, LogLogTransform, ProbitTransform, LogitTransform

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
    def generate_const_from_fact(self, fact_dict: dict): 
        # Declare data type
        Object = DeclareSort('Object')

        # Prepare variables
        var_names_to_variables = dict()
        for v in self.get_variables(): 
            var_names_to_variables[v.name] = v

        main_seq = None
        interaction_seq = None
        # Get variable names
        start_name = fact_dict['start']
        end_name = fact_dict['end']
        # Get variables
        start_var = var_names_to_variables[start_name]
        end_var = var_names_to_variables[end_name]

        if fact_dict['function'] == 'MainEffect': 
            assert(end_var is self.dv)

            if 'main_effects' not in self.consts: 
                main_seq = Unit(start_var.const)
            else: 
                main_seq = self.consts['main_effects']
                main_seq = Concat(Unit(start_var.const), main_seq)
            self.consts['main_effects'] = main_seq
        
        elif fact_dict['function'] == 'NoMainEffect': 
            main_seq = Empty(SeqSort(Object))
            
            # If there are no main effects so far, create an empty SeqSort
            if 'main_effects' not in self.consts: 
                self.consts['main_effects'] = main_seq
            # Else: If there are main effects already, do nothing

        elif fact_dict['function'] == 'Interaction': 
            # Create set for interaction
            interaction = EmptySet(Object)
            SetAdd(interaction, start_var.const)
            SetAdd(interaction, end_var.const)
            if 'interactions' not in self.consts:
                interaction_seq = Unit(interaction)
            else: 
                interaction_seq = self.consts['interactions']
                interaction_seq = Concat(Unit(interaction), interaction_seq)
            self.consts['interactions'] = interaction_seq
        
        elif fact_dict['function'] == 'NoInteraction': 
            interaction = EmptySet(Object)

            # If there are no interactions so far, create a SeqSort of Sets
            if 'interactions' not in self.consts:
                interaction_seq = Unit(interaction)
                self.consts['interactions'] = interaction_seq

            # Else: If there are interactions already, do nothing

        else: 
            pass
    
    def generate_consts(self): 
        # Declare data type
        Object = DeclareSort('Object')

        # If we haven't already generated consts from facts 
        if 'main_effects' not in self.consts: 
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

            self.consts['main_effects'] = main_seq

        if 'interactions' not in self.consts: 
            interactions_seq = Unit(EmptySet(Object))
            self.consts['interactions'] = interactions_seq
        
    # Return the set of logical facts that this Design "embodies"
    def compile_to_facts(self) -> List: 
        facts = list() # TODO: START HERE: Are we trying to make facts a dictionary?
        nodes = list(self.graph._graph.nodes(data=True)) # get list of nodes
        for (n, data) in nodes: 
            n_var = data['variable']
            if isinstance(n_var, Nominal): 
                facts.append(NominalDataType(n_var.const))
            elif isinstance(n_var, Ordinal): 
                facts.append(OrdinalDataType(n_var.const))
            else: 
                assert (isinstance(n_var, Numeric)) 
                facts.append(NumericDataType(n_var.const))

        edges = list(self.graph._graph.edges(data=True)) # get list of edges

        for (n0, n1, edge_data) in edges: 
            edge_type = edge_data['edge_type']
            n0_var = self.graph._graph.nodes[n0]['variable']
            n1_var = self.graph._graph.nodes[n1]['variable']
            if edge_type == 'nest': 
                pass
            elif edge_type == 'treat': 
                pass
            else: 
                pass
            
        return facts

    def collect_ambiguous_effects_facts(self, main_effects: bool, interactions: bool) -> List: 
        facts = list()
        edges = list(self.graph._graph.edges(data=True)) # get list of edges

        # Do we care about Main Effects? 
        if main_effects: 
            # What Main Effects should we consider? 
            for (n0, n1, edge_data) in edges: 
                edge_type = edge_data['edge_type']
                n0_var = self.graph._graph.nodes[n0]['variable']
                n1_var = self.graph._graph.nodes[n1]['variable']
                if edge_type == 'nest': 
                    pass
                elif edge_type == 'treat': 
                    pass
                elif edge_type == 'unknown': 
                    facts.append(MainEffect(n0_var.const, n1_var.const))
                    facts.append(NoMainEffect(n0_var.const, n1_var.const))
        
        if interactions: 
            # What Interaction Effects should we consider?
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
    
    # @return additional set of logical facts that needs disambiguation depending on @param desired output_obj
    def collect_ambiguous_facts(self, output: str) -> List: 

        facts = list()
        edges = list(self.graph._graph.edges(data=True)) # get list of edges

        # Iterate over edges
        for (n0, n1, edge_data) in edges:         
            edge_type = edge_data['edge_type']
            n0_var = self.graph._graph.nodes[n0]['variable']
            n1_var = self.graph._graph.nodes[n1]['variable']
            if edge_type == 'unknown':
                if output.upper() == 'VARIABLE RELATIONSHIP GRAPH': 
                    # Induce UNSAT in order to get end-user clarification
                    facts.append(Cause(n0_var.const, n1_var.const))
                    facts.append(Correlate(n0_var.const, n1_var.const))
            elif edge_type == 'treat': 
                pass
            elif edge_type == 'nest': 
                # TODO: Mixed Effect
                raise NotImplementedError
            else: 
                pass
        
        # Iterate over nodes
        if output == 'STATISTICAL MODEL': 
            nodes = list(self.graph._graph.nodes(data=True))
            for (n, data) in nodes: 
                # Check if the variable is included as a main effect
                var = data['variable']
                if is_true(BoolVal(Contains(self.consts['main_effects'], Unit(var.const)))): 
                    # Induce UNSAT 
                    facts.append(Transformation(var.const))
                    facts.append(NoTransformation(var.const))
                    # # Induce UNSAT
                    # Depending on variable data type, add more constraints for possible transformations
                    if isinstance(var, Numeric): 
                        facts.append(NumericTransformation(var.const))
                        facts.append(LogTransform(var.const))
                        facts.append(SquarerootTransform(var.const))
                    elif isinstance(var, Nominal) or isinstance(var, Ordinal): 
                        facts.append(CategoricalTransformation(var.const))
                        facts.append(LogLogTransform(var.const))
                        facts.append(ProbitTransform(var.const))
                        # facts.append(LogitTransform(var.const)) # TODO: Might only make sense for binary data??                
                        
                    # TODO: If update main effect variable and it is involved in interaction, ask about or propagate automatically?
        
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