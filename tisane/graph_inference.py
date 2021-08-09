"""
Inferring model effects structures from the graph IR
"""

from abc import abstractmethod
from tisane import variable
from tisane.variable import AbstractVariable, Has, Moderates, NumberValue
from tisane.random_effects import RandomSlope, RandomIntercept
from tisane.graph import Graph
from tisane.design import Design
from itertools import chain, combinations
from typing import Dict, List, Set, Any, Tuple
import networkx as nx

##### HELPER #####
def powerset(iterable):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))


def cast_to_variables(
    names: Set[str], variables: List[AbstractVariable]
) -> Set[AbstractVariable]:
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
    assert isinstance(variable, AbstractVariable)
    if gr.has_variable(variable):
        pred = causal_sub._graph.predecessors(variable.name)  # Returns an iterator obj
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
def find_variable_associates_that_causes_or_associates_another(
    source: AbstractVariable, sink: AbstractVariable, gr: Graph
) -> Set[str]:
    intermediaries = set()

    assert gr.has_variable(source)
    assert gr.has_variable(sink)

    # Get all the variables that @param source variable is associated with
    associates_neighbors = gr.get_neighbors(
        source, edge_type="associates"
    )  # Returns list of AbstractVariables
    # Check if the neighbors also cause or are associated with @param sink variable
    for var in associates_neighbors:
        if gr.has_edge(start=var, end=sink, edge_type="causes"):
            intermediaries.add(var.name)
        elif gr.has_edge(start=var, end=sink, edge_type="associates"):
            intermediaries.add(var.name)

    return intermediaries


def find_all_associates_that_causes_or_associates_another(
    sources: List[AbstractVariable], sink: AbstractVariable, gr: Graph
) -> Set[str]:
    all_intermediaries = set()
    for var in sources:
        intermediaries = find_variable_associates_that_causes_or_associates_another(
            source=var, sink=sink, gr=gr
        )
        all_intermediaries = all_intermediaries.union(intermediaries)

    return all_intermediaries


## Rule 4: Find common cause
def find_variable_parent_that_causes_or_associates_another(
    source: AbstractVariable, sink: AbstractVariable, gr: Graph
) -> Set[str]:
    parents_cause_sink = set()

    # Get parents of @param source
    parents = gr.get_predecessors(var=source)
    # Check to see if any parents cause @param sink
    for p in parents:
        p_var = gr.get_variable(name=p)
        assert isinstance(p_var, AbstractVariable)
        if gr.has_edge(start=p_var, end=source, edge_type="causes"):
            if gr.has_edge(start=p_var, end=sink, edge_type="causes"):
                parents_cause_sink.add(p)
            elif gr.has_edge(start=p_var, end=sink, edge_type="associates"):
                parents_cause_sink.add(p)

    return parents_cause_sink


def find_all_parents_that_causes_or_associates_another(
    sources: List[AbstractVariable], sink: AbstractVariable, gr: Graph
) -> Set[str]:
    all_parents_cause_sink = set()
    for var in sources:
        parents_cause_sink = find_variable_parent_that_causes_or_associates_another(
            source=var, sink=sink, gr=gr
        )
        all_parents_cause_sink = all_parents_cause_sink.union(parents_cause_sink)

    return all_parents_cause_sink


# Infer candidate main effects for @param query given the relationships contained in @param gr
# The resulting set of candidate main effects include the ivs included in the query
def infer_main_effects(gr: Graph, query: Design) -> Set[AbstractVariable]:
    main_candidates = set()

    ivs = query.ivs
    # Add IVs already included in query
    for v in ivs:
        main_candidates.add(v)
    assert len(main_candidates) == len(ivs)
    dv = query.dv
    all_variables_in_graph = gr.get_variables()

    common_ancestors_names = find_common_ancestors(variables=ivs, gr=gr)
    common_ancestors_variables = cast_to_variables(
        names=common_ancestors_names, variables=all_variables_in_graph
    )
    main_candidates = main_candidates.union(common_ancestors_variables)
    # import pdb; pdb.set_trace()

    causal_ancestors = find_all_causal_ancestors(variables=ivs, gr=gr)
    causal_ancestors_variables = cast_to_variables(
        names=causal_ancestors, variables=all_variables_in_graph
    )
    main_candidates = main_candidates.union(causal_ancestors_variables)
    # import pdb; pdb.set_trace()

    # TODO: "intermediaries" might not be the best variable name
    intermediaries = find_all_associates_that_causes_or_associates_another(
        sources=ivs, sink=dv, gr=gr
    )
    intermediaries_variables = cast_to_variables(
        names=intermediaries, variables=all_variables_in_graph
    )
    main_candidates = main_candidates.union(intermediaries_variables)
    # import pdb; pdb.set_trace()

    parents_cause_dv = find_all_parents_that_causes_or_associates_another(
        sources=ivs, sink=dv, gr=gr
    )
    parents_cause_dv_variables = cast_to_variables(
        names=parents_cause_dv, variables=all_variables_in_graph
    )
    main_candidates = main_candidates.union(parents_cause_dv_variables)
    # import pdb; pdb.set_trace()

    return main_candidates

# @param on is outcome/dependent variable of interest
# @returns set of variable names representing interaction effects in @param gr
def find_moderates_edges_on_variable(gr: Graph, on: AbstractVariable) -> Set[str]: 
    moderates = set() 

    # Get causal subgraph
    conceptual_sub = gr.get_conceptual_subgraph()

    edges = conceptual_sub.get_edges()
    for e in edges: 
        (n0, n1, edge_data) = e
        if n1 == on.name: 
            if edge_data["edge_type"] == "associates": 
                edge_obj = edge_data["edge_obj"]
                if isinstance(edge_obj, Moderates): 
                    moderates.add(n0)
    
    return moderates

# Filters the list of interaction_names to only include those that involve two or more of the variables named in @param variables
# @returns the names of moderates/interaction variables that contain two or more of the @param variables
def filter_interactions_involving_variables(variables: List[AbstractVariable], interaction_names=Set[str]) -> Set[str]: 
    interactions = set() 

    for ixn in interaction_names: 
        assert(isinstance(ixn, str)) # ixn should be a string like "Measure 0*Measure 1"
        assert("*" in ixn)
        num_vars = 0
        for v in variables: 
            if v.name in ixn: 
                num_vars += 1
        if num_vars >=2: 
            interactions.add(ixn)

    return interactions

# More computationally efficient: Look through list of main effects in @param variables and find any interaction effects involving them 
def find_interactions_for_main_effects(variables: List[AbstractVariable]): 
    pass

# Infer candidate interaction effects for @param query given the relationships contained in @param gr
def infer_interaction_effects(gr: Graph, query: Design, main_effects: List[AbstractVariable]) -> Set[AbstractVariable]:
    interaction_candidates = set() 

    ivs = query.ivs
    dv = query.dv
    interactions = find_moderates_edges_on_variable(gr=gr, on=dv) # Find all possible interactions
    interactions = filter_interactions_involving_variables(variables=main_effects, interaction_names=interactions) # Filter to interactions involving two or more ivs
    interactions_variables = cast_to_variables(names=interactions, variables=gr.get_variables())
    interaction_candidates = interaction_candidates.union(interactions_variables)
    return interaction_candidates

def construct_random_effects_for_repeated_measures(gr: Graph, query: Design): 
    random_effects = set() 
    # Get dv's unit
    dv = query.dv
    dv_unit = gr.get_identifier_for_variable(dv)

    if gr.has_edge(start=dv_unit, end=dv, edge_type="has"): 
        (n0, n1, edge_data) = gr.get_edge(start=dv_unit, end=dv, edge_type="has")
        edge_obj = edge_data["edge_obj"]
        assert(isinstance(edge_obj, Has))
        assert(edge_obj.variable == dv_unit)
        assert(edge_obj.measure == dv)
        # How many repeated measures are there? 
        assert(isinstance(edge_obj.repetitions, NumberValue))
        # There is more than one observation of the DV for each unit
        if edge_obj.repetitions.is_greater_than_one(): 
            # Add a random intercept for the unit U 
            ri = RandomIntercept(groups=dv_unit)
            random_effects.add(ri)
        
    return random_effects

# @returns an ordered list of unitts included in @param gr, the lowest unit/level is in the lowest index
def find_ordered_list_of_units(gr: Graph) -> List[str]: 
    measurement_sub = gr.get_nesting_subgraph() # returns subgraph containing nests edges only  
    # Topologically sort the edges/nodes 
    # Note: this may need to be revised to more fully support units/levels where one unit can nest within multiple other units (e.g., in some non-nested cases)
    ordered_units = list(nx.topological_sort(measurement_sub._graph)) 
    # If there is only one unit, there would be no nesting relationships to the set of ordered_units in case all measures come from the same unit 
    if len(ordered_units) == 0: 
        identifiers = gr.get_identifiers()
        assert(len(identifiers), 1)
        ordered_units = [i.name for i in identifiers]

    return ordered_units

# Make random effects for main effects in @param variables
# The number of 
def construct_random_effects_for_nests(gr: Graph, dv: AbstractVariable, variables: List[AbstractVariable]) -> Set[str]: 
    random_effects = set() 
    random_effects_names = set() # used to keep track of the random inercepts for variable names already added
    variable_units = set()
    
    # Find all the units for all the variables involved    
    dv_unit = gr.get_identifier_for_variable(dv)
    # Get list of all units
    all_ordered_units = find_ordered_list_of_units(gr=gr) # returns a list of unit names for which there are nests relationships
    assert(dv_unit.name in all_ordered_units)
    idx = all_ordered_units.index(dv_unit.name) 
    # For random effects due to nesting, focus on those that nest the unit that has the DV
    units_to_consider = all_ordered_units[idx+1:]

    # Add random effects for nested variables now
    for v in variables: 
        v_unit = gr.get_identifier_for_variable(v)
        # Is the variable's unit the same as the dv's
        if v_unit is dv_unit: 
            assert(v_unit.name not in units_to_consider)
            variable_units.add(v_unit.name)

        else: 
            assert(v_unit.name in units_to_consider)

    # Add any nesting units whose measures are not included in the list of variables 
    for u in units_to_consider: 
        if u not in variable_units: 
            unit = gr.get_variable(name=u)
            ri = RandomIntercept(groups=unit)
            random_effects.add(ri)

    # Check if there are other units in which v_unit is nested 
    # TODO: If len(units_to_consider) > 1 (there are multiple chains of nesting), there may be a more concise way to express this rather than adding each as a separat random intercept
    # TODO: Does this approach work for non-nested as well?
    return random_effects

# Infer candidate interaction effects for @param query given the relationships contained in @param gr
def infer_random_effects(gr: Graph, main_effects: List[AbstractVariable]): 
    pass

def gnerate_all_model_candidates(gr: Graph, query: Design): 
    # Combine all the main effects, interaction effects, and random effects
    # In order to make it easy to populate the GUI/disambiguation questions and react to analysts' selections, what should the right data structure be?
    pass