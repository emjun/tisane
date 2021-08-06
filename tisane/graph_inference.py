"""
Inferring model effects structures from the graph IR
"""

from tisane import variable
from tisane.variable import AbstractVariable
from tisane.graph import Graph
from tisane.design import Design
from itertools import chain, combinations
from typing import List, Set
import networkx as nx

##### HELPER #####
def powerset(iterable):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))

def cast_to_variables(names: Set[str], variables: List[AbstractVariable]) -> Set[AbstractVariable]:
    named_variables = set()

    for n in names:
        for v in variables: 
            if n == v.name: 
                named_variables.add(v)
        
    return named_variables

## Rule 1: Find common ancestors 
def find_common_ancestors(variables: List[AbstractVariable], gr: Graph) -> Set[str]: 
    common_ancestors = set()

    # Map counting ancestors of all @param variables
    _ancestor_to_count_ = dict()
    # Get causal subgraph
    causal_sub = gr.get_causal_subgraph()

    # Remove any edges between variables (IVs)
    var_names = [v.name for v in variables]

    edges = causal_sub.get_edges()
    for (n0, n1, edge_data) in edges:
        edge_type = edge_data["edge_type"]
        if edge_type == "causes":
            if n0 in var_names and n1 in var_names: 
                causal_sub._graph.remove_edge(n0, n1)

    # Take transitive closure of causal subgraph
    tc = nx.transitive_closure_dag(causal_sub._graph)

    # For each variable in @param variables: 
    # Get its predecessors from the transitive closure
    # Add them to a map (key is variable, count is value)   
    for v in variables: 
        # node = causal_sub.get_node(variable=v)
        predecessors = tc.predecessors(v.name)
        
        # Add each predecessor to the dictionary
        for p in predecessors:
            # Have we seen this ancestor before?
            if p in _ancestor_to_count_.keys(): 
                _ancestor_to_count_[p] += 1
            else:
                _ancestor_to_count_[p] = 1
    
    # At the end, add to set and return set of variables that have count > 1
    for key, value in _ancestor_to_count_.items():
        if value > 1: 
            common_ancestors.add(key)

    return common_ancestors

## Rule 2: Find causal ancestors
# Moved outside for testing purposes
def find_variable_causal_ancestors(variable: AbstractVariable, gr: Graph) -> Set[str]:
        causal_ancestors = set()

        causal_sub = gr.get_causal_subgraph()
        assert(isinstance(variable, AbstractVariable))
        if gr.has_variable(variable):
            pred = causal_sub._graph.predecessors(variable.name) # Returns an iterator obj
            # Add each predecessor to the set
            for p in pred: 
                causal_ancestors.add(p)  
                ancestors = find_variable_causal_ancestors(gr.get_variable(p), gr)
                causal_ancestors = causal_ancestors.union(ancestors)
        # Else: There is nothing to add to the set of causal ancestors
        return causal_ancestors

def find_all_causal_ancestors(variables: List[AbstractVariable], gr: Graph) -> Set[str]:
    all_causal_ancestors = set()
    for v in variables: 
        ancestors = find_variable_causal_ancestors(variable=v, gr=gr)
        all_causal_ancestors = all_causal_ancestors.union(ancestors)

    return all_causal_ancestors

## Rule 3: Find associated causes 
def find_variable_associates_that_causes_or_associates_another(source: AbstractVariable, sink: AbstractVariable, gr: Graph) -> Set[str]:
    intermediaries = set()

    assert(gr.has_variable(source))
    assert(gr.has_variable(sink))
    
    # Get all the variables that @param source variable is associated with
    associates_neighbors = gr.get_neighbors(source, edge_type="associates") # Returns list of AbstractVariables
    # Check if the neighbors also cause or are associated with @param sink variable
    for var in associates_neighbors:
        if gr.has_edge(start=var, end=sink, edge_type="causes"): 
            intermediaries.add(var.name)
        elif gr.has_edge(start=var, end=sink, edge_type="associates"): 
            intermediaries.add(var.name)

    return intermediaries

def find_all_associates_that_causes_or_associates_another(sources: List[AbstractVariable], sink: AbstractVariable, gr: Graph) -> Set[str]:
    all_intermediaries = set()
    for var in sources: 
        intermediaries = find_variable_associates_that_causes_or_associates_another(source=var, sink=sink, gr=gr)
        all_intermediaries = all_intermediaries.union(intermediaries)

    return all_intermediaries
    
## Rule 4: Find common cause
def find_variable_parent_that_causes_or_associates_another(source: AbstractVariable, sink: AbstractVariable, gr: Graph) -> Set[str]:
    parents_cause_sink = set()

    # Get parents of @param source
    parents = gr.get_predecessors(var=source)
    # Check to see if any parents cause @param sink
    for p in parents: 
        p_var = gr.get_variable(name=p)
        assert(isinstance(p_var, AbstractVariable))
        if gr.has_edge(start=p_var, end=source, edge_type="causes"):
            if gr.has_edge(start=p_var, end=sink, edge_type="causes"): 
                parents_cause_sink.add(p)
            elif gr.has_edge(start=p_var, end=sink, edge_type="associates"): 
                parents_cause_sink.add(p)
    
    return parents_cause_sink

def find_all_parents_that_causes_or_associates_another(sources: List[AbstractVariable], sink: AbstractVariable, gr: Graph) -> Set[str]:
    all_parents_cause_sink = set()
    for var in sources: 
        parents_cause_sink = find_variable_parent_that_causes_or_associates_another(source=var, sink=sink, gr=gr)
        all_parents_cause_sink = all_parents_cause_sink.union(parents_cause_sink)
    
    return all_parents_cause_sink

def infer_main_effects(gr: Graph, query: Design):
    main_candidates = set()

    ivs = query.ivs
    dv = query.dv
    all_variables_in_graph = gr.get_variables()

    common_ancestors_names = find_common_ancestors(variables=ivs, gr=gr)
    common_ancestors_variables = cast_to_variables(names=common_ancestors_names, variables=all_variables_in_graph)
    main_candidates = main_candidates.union(common_ancestors_variables)

    causal_ancestors = find_all_causal_ancestors(variables=ivs, gr=gr)
    causal_ancestors_variables = cast_to_variables(names=causal_ancestors, variables=all_variables_in_graph) 
    main_candidates = main_candidates.union(causal_ancestors_variables)

    # TODO: "intermediaries" might not be the best variable name
    intermediaries = find_all_associates_that_causes_or_associates_another(sources=ivs, sink=dv, gr=gr)
    intermediaries_variables = cast_to_variables(names=intermediaries, variables=all_variables_in_graph)
    main_candidates = main_candidates.union(intermediaries_variables)

    parents_cause_dv = find_all_parents_that_causes_another(sources=ivs, sink=dv, gr=gr)
    parents_cause_dv
    main_candidates = main_candidates.union(parents_cause_dv)

    
    return main_candidates

def infer_interaction_effects(gr: Graph):
    pass

def infer_random_effects(gr: Graph):
    pass

