"""
Inferring model effects structures from the graph IR
"""

from abc import abstractmethod
import pdb
from tisane.family import AbstractLink
from tisane import variable
from tisane import random_effects
from tisane.variable import (
    AbstractVariable,
    Associates,
    Causes,
    Has,
    Measure,
    Moderates,
    Nests,
    NumberValue,
    SetUp,
    Unit,
    Nominal,
)
from tisane.random_effects import RandomEffect, RandomSlope, RandomIntercept
from tisane.graph import Graph
from tisane.design import Design
from itertools import chain, combinations
from typing import Dict, List, Set, Any, Tuple
import typing  # for Union
import networkx as nx

##### HELPER #####
# TODO: May need to use helper function in additional to global explanation template to provide "personalized" explanations for each variable.
explanations = {
    "main effects": {
        # "query": {
        #     "causes": "The variable is included as an independent variable in the query. The variable also directly causes the dependent variable.",
        #     "associates with": "The variable is included as an independent variable in the query. The variable is also directly associated with the dependent variable.",
        # },
        "query": {
            "causes": "You included {cause} in your query. You specified that {cause} causes {effect}.",
            "associates": "You included {var1} in your query. You specified that {var1} is associated with {var2}.",
        },
        "common ancestors": "The variable {ancestor} is a shared cause of the following independent variables included in your query: {ivs}. {ancestor} might also exert causal influence on the dependent variable {dv}.",
        "causal ancestors": "The variable {ancestor} causes the following independent variables included in your query: {ivs}. {ancestor} might also exert causal influence on the dependent variable {dv}.",
        "intermediaries": "The variable {intermediary} is associated with the following independent variables included in your query: {ivs}. {intermediary_relationship_to_dv}. As a result, {intermediary} may be a confounding variable.",
        # "parents cause dv": "Variable parents cause the dv",
    },
    "interaction effects": "This interaction effect involves at least two variables that are included as main effects! The variables represented in this interaction effect: {variables}",
    "random effects": {
        # "repeated measures": "{measure} is measured multiple times ({num_times_measured}). We want to account for two clusters that might arise due to this. (1.) Since the same {unit} contributed multiple observations, those observations might be more alike. (2.) Observations at each repeated point (across {distinguisher}), might be similar to each other.",
        "repeated measures, unit": "{measure} is measured multiple times ({num_times_measured}). Since the same {unit} contributed multiple observations, those observations might be more alike.",
        "repeated measures, distinguisher": "{measure} is measured multiple times, once per {distinguisher}. Observations at each {distinguisher}, might be similar to each other.",
        "hierarchical data": "Because {nested} is nested within {nesting}, {nested} in the same {nesting} might be more alike, leading to non-independence in observations.",
        "non-nesting": "Observations belong to {groups} as well as others.",
        "interaction": "{unit} sees multiple instances of each of the variables {variables} in the interaction. Controling for the largest subset of interaction variables that are 'within-subjects' maximizes generalizability of statistical findings.",
    },
}


def get_conceptual_explanation(v: AbstractVariable, dv: AbstractVariable, gr: Graph):
    causes_expl = "You specified that {cause} causes {effect}."
    associates_expl = "You specified that {var1} is associated with {var2}."

    causes_edge = gr.get_edge(start=v, end=dv, edge_type="causes")
    associates_edge = gr.get_edge(start=v, end=dv, edge_type="associates")
    # Each variable @param v either causes or (logical or) is associated with @param dv
    # There must be a causes or associates edge between @param v and @param dv
    if causes_edge is None:
        assert associates_edge is not None
        expl = causes_expl.format(cause=v.name, effect=dv.name)
    else:
        assert causes_edge is not None
        assert associates_edge is None
        expl = associates_expl.format(var1=v.name, var2=dv.name)

    return expl


# Get personalized explanation of variables that were included in a query to infer a statistical model from a set of variable relationships
def get_query_explanation(v: AbstractVariable, dv: AbstractVariable, gr: Graph):
    global explanations

    main_explanations = explanations["main effects"]

    causes_edge = gr.get_edge(start=v, end=dv, edge_type="causes")
    associates_edge = gr.get_edge(start=v, end=dv, edge_type="associates")
    # Each variable @param v either causes or (logical or) is associated with @param dv
    # There must be a causes or associates edge between @param v and @param dv
    if causes_edge is None:
        assert associates_edge is not None
        expl = main_explanations["query"]["causes"].format(cause=v.name, effect=dv.name)
    else:
        assert causes_edge is not None
        assert associates_edge is None
        expl = main_explanations["query"]["associates"].format(
            var1=v.name, var2=dv.name
        )

    return expl


# Get personalized explanation of interaction effects that could be included in an inferred statistical model
def get_interaction_explanation(interaction_name: str, gr: Graph):
    global explanations

    interaction_explanations = explanations["interaction effects"]

    var_names = interaction_name.split("*")
    var_names_str = ",".join(var_names)
    expl = interaction_explanations.format(variables=var_names_str)

    return expl


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
def find_common_ancestors(
    variables: List[AbstractVariable], gr: Graph
) -> Tuple[Set[str], Dict[str, List[str]]]:
    common_ancestors = set()
    common_ancestor_to_children = dict()

    # Map counting ancestors of all @param variables
    _ancestor_to_count_ = dict()
    _ancestor_to_children_ = (
        dict()
    )  # keep track of children IVs for each common ancestor, mostly useful for explanations
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
        # if v.name == "Time":
        #     import pdb; pdb.set_trace()
        predecessors = tc.predecessors(v.name)

        # Add each predecessor to the dictionary
        for p in predecessors:
            # Have we seen this ancestor before?
            if p in _ancestor_to_count_.keys():
                _ancestor_to_count_[p] += 1
            else:
                _ancestor_to_count_[p] = 1
                _ancestor_to_children_[p] = list()
            # Add v to list of children that @p is an ancestor to
            assert p in _ancestor_to_children_.keys()
            _ancestor_to_children_[p].append(v.name)

    # At the end, add to set and return set of variables that have count > 1
    # At the end, also add to the dict of shared ancestor to variables that share that ancestor
    for key, value in _ancestor_to_count_.items():
        if value > 1:
            common_ancestors.add(key)
            common_ancestor_to_children[key] = _ancestor_to_children_[key]

    assert len(common_ancestors) == len(common_ancestor_to_children.keys())
    return (common_ancestors, common_ancestor_to_children)


## Rule 2: Find causal ancestors
# Moved outside for testing purposes
def find_variable_causal_ancestors(variable: AbstractVariable, gr: Graph) -> Set[str]:
    causal_ancestors = set()

    causal_sub = gr.get_causal_subgraph()
    if not isinstance(variable, AbstractVariable):
        import pdb

        pdb.set_trace()
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


def find_all_causal_ancestors(
    variables: List[AbstractVariable], gr: Graph
) -> Tuple[Set[str], Dict[str, List[str]]]:
    all_causal_ancestors = set()
    variable_to_causal_ancestors = dict()

    for v in variables:
        ancestors = find_variable_causal_ancestors(variable=v, gr=gr)
        variable_to_causal_ancestors[v.name] = list(
            ancestors
        )  # Add to dict which is used for deriving explanations
        all_causal_ancestors = all_causal_ancestors.union(ancestors)

    return (all_causal_ancestors, variable_to_causal_ancestors)


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
) -> Tuple[Set[str], Dict[str, List[str]]]:
    all_intermediaries = set()
    variable_to_intermediaries = dict()

    for var in sources:
        intermediaries = find_variable_associates_that_causes_or_associates_another(
            source=var, sink=sink, gr=gr
        )
        variable_to_intermediaries[var.name] = list(intermediaries)
        all_intermediaries = all_intermediaries.union(intermediaries)

    assert len(sources) == len(variable_to_intermediaries.keys())
    return (all_intermediaries, variable_to_intermediaries)


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
# @returns a tuple: (set of candidates, dictionary with the main effects and the reasons they are considered candidates)
def infer_main_effects_with_explanations(
    gr: Graph, query: Design
) -> Set[AbstractVariable]:
    global explanations
    main_explanations = explanations["main effects"]
    main_candidates = set()
    main_candidates_explanations = dict()

    ivs = query.ivs
    # Add IVs already included in query
    for v in ivs:
        main_candidates.add(v)
    assert len(main_candidates) == len(ivs)
    # Add explanations
    for v in ivs:
        # Is the variable a new main effect candidate?
        if v.name not in main_candidates_explanations.keys():
            # declare the list of explanations/reasons for this variable
            main_candidates_explanations[v.name] = list()
        # add explanation
        expl = get_query_explanation(v, query.dv, gr)
        main_candidates_explanations[v.name].append(expl)
        # main_candidates_explanations[v.name].append(main_explanations["query"])
    dv = query.dv
    all_variables_in_graph = gr.get_variables()

    (
        common_ancestors_names,
        common_ancestors_names_to_variables,
    ) = find_common_ancestors(variables=ivs, gr=gr)
    common_ancestors_variables = cast_to_variables(
        names=common_ancestors_names, variables=all_variables_in_graph
    )
    # Add to set of effects
    main_candidates = main_candidates.union(common_ancestors_variables)
    # Add explanations
    for v in common_ancestors_names:
        # Is the variable a new main effect candidate?
        if v not in main_candidates_explanations.keys():
            # declare the list of explanations/reasons for this variable
            main_candidates_explanations[v] = list()
        # add explanation
        vars_names = common_ancestors_names_to_variables[v]
        expl = main_explanations["common ancestors"].format(
            ancestor=v, ivs=vars_names, dv=query.dv.name
        )
        main_candidates_explanations[v].append(expl)

    (causal_ancestors, variable_to_causal_ancestors) = find_all_causal_ancestors(
        variables=ivs, gr=gr
    )
    causal_ancestors_variables = cast_to_variables(
        names=causal_ancestors, variables=all_variables_in_graph
    )
    # Add to set of effects
    main_candidates = main_candidates.union(causal_ancestors_variables)
    # Add explanations
    for v in causal_ancestors:
        # Is the variable a new main effect candidate?
        if v not in main_candidates_explanations.keys():
            # declare the list of explanations/reasons for this variable
            main_candidates_explanations[v] = list()

        # add explanation
        # Get list of variables that this causal ancestor v causes
        v_causes_vars = list()
        for var_name, causal_ancestors in variable_to_causal_ancestors.items():
            if v in causal_ancestors:
                v_causes_vars.append(var_name)
        v_causes_vars_str = ",".join(v_causes_vars)
        expl = main_explanations["causal ancestors"].format(
            ancestor=v, ivs=v_causes_vars_str, dv=query.dv.name
        )
        main_candidates_explanations[v].append(expl)

    # TODO: "intermediaries" might not be the best variable name
    (
        intermediaries,
        variable_to_intermediaries,
    ) = find_all_associates_that_causes_or_associates_another(
        sources=ivs, sink=dv, gr=gr
    )
    intermediaries_variables = cast_to_variables(
        names=intermediaries, variables=all_variables_in_graph
    )
    # Add to set of effects
    main_candidates = main_candidates.union(intermediaries_variables)
    # Add explanations
    for v in intermediaries:
        # Is the variable a new main effect candidate?
        if v not in main_candidates_explanations.keys():
            # declare the list of explanations/reasons for this variable
            main_candidates_explanations[v] = list()

        # add explanation
        vars = list()
        for key, val in variable_to_intermediaries.items():
            if v in val:
                vars.append(key)
        vars_names_str = ",".join(vars)
        var = gr.get_variable(v)
        intermediary_relationship_to_dv = get_conceptual_explanation(
            v=var, dv=query.dv, gr=gr
        )
        expl = main_explanations["intermediaries"].format(
            intermediary=v,
            ivs=vars_names_str,
            intermediary_relationship_to_dv=intermediary_relationship_to_dv,
        )
        main_candidates_explanations[v].append(expl)

    # Redundant with Rule 2: Finding causal ancestors
    # parents_cause_dv = find_all_parents_that_causes_or_associates_another(
    #     sources=ivs, sink=dv, gr=gr
    # )
    # parents_cause_dv_variables = cast_to_variables(
    #     names=parents_cause_dv, variables=all_variables_in_graph
    # )
    # # Add to set of effects
    # main_candidates = main_candidates.union(parents_cause_dv_variables)
    # # Add explanations
    # for v in parents_cause_dv:
    #     # Is the variable a new main effect candidate?
    #     if v not in main_candidates_explanations.keys():
    #         # declare the list of explanations/reasons for this variable
    #         main_candidates_explanations[v] = list()
    #     # add explanation

    #     expl = main_explanations["parents cause dv"].format()
    #     main_candidates_explanations[v].append(expl)

    return (main_candidates, main_candidates_explanations)


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
def filter_interactions_involving_variables(
    variables: List[AbstractVariable], interaction_names=Set[str]
) -> Set[str]:
    interactions = set()

    for ixn in interaction_names:
        assert isinstance(ixn, str)  # ixn should be a string like "Measure_0*Measure_1"
        assert "*" in ixn
        num_vars = 0
        for v in variables:
            if v.name in ixn:
                num_vars += 1
        if num_vars >= 2:
            interactions.add(ixn)

    return interactions


# More computationally efficient: Look through list of main effects in @param variables and find any interaction effects involving them
def find_interactions_for_main_effects(variables: List[AbstractVariable]):
    pass


# Infer candidate interaction effects for @param query given the relationships contained in @param gr
# @returns a tuple: (set of candidates, dictionary with the interaction effects and the reasons they are considered candidates)
def infer_interaction_effects_with_explanations(
    gr: Graph, query: Design, main_effects: List[AbstractVariable]
) -> Set[AbstractVariable]:
    global explanations
    interaction_explanation = explanations[
        "interaction effects"
    ]  # There is only one explanation for interaction effects

    interaction_candidates = set()
    interaction_candidates_explanations = dict()

    ivs = query.ivs
    dv = query.dv
    interactions = find_moderates_edges_on_variable(
        gr=gr, on=dv
    )  # Find all possible interactions
    interactions = filter_interactions_involving_variables(
        variables=main_effects, interaction_names=interactions
    )  # Filter to interactions involving two or more ivs
    interactions_variables = cast_to_variables(
        names=interactions, variables=gr.get_variables()
    )
    # Add to set of effects
    interaction_candidates = interaction_candidates.union(interactions_variables)
    # Add explanations
    for v in interactions:
        # Is the variable a new interaction effect candidate?
        if v not in interaction_candidates_explanations.keys():
            # declare the list of explanations/reasons for this variable
            interaction_candidates_explanations[v] = list()
        # add explanation
        assert isinstance(v, str)
        expl = get_interaction_explanation(v, gr)
        interaction_candidates_explanations[v].append(expl)
        # interaction_candidates_explanations[v].append(interaction_explanation)

    return (interaction_candidates, interaction_candidates_explanations)


def construct_random_effects_for_repeated_measures(
    gr: Graph, query: Design
) -> Set[RandomIntercept]:
    random_effects = set()
    # Get dv's unit
    dv = query.dv
    dv_unit = gr.get_identifier_for_variable(dv)

    if gr.has_edge(start=dv_unit, end=dv, edge_type="has"):
        (n0, n1, edge_data) = gr.get_edge(start=dv_unit, end=dv, edge_type="has")
        edge_obj = edge_data["edge_obj"]
        assert isinstance(edge_obj, Has)
        assert edge_obj.variable == dv_unit
        assert edge_obj.measure == dv
        # How many repeated measures are there?
        assert isinstance(edge_obj.repetitions, NumberValue)
        # There is more than one observation of the DV for each unit
        # import pdb; pdb.set_trace()
        if edge_obj.repetitions.is_greater_than_one():
            # Add a random intercept for the unit U
            ri = RandomIntercept(groups=dv_unit)
            random_effects.add(ri)

            ri = RandomIntercept(groups=edge_obj.according_to)
            random_effects.add(ri)

    return random_effects


# @returns an ordered list of unitts included in @param gr, the lowest unit/level is in the lowest index
def find_ordered_list_of_units(gr: Graph) -> List[str]:
    measurement_sub = (
        gr.get_nesting_subgraph()
    )  # returns subgraph containing nests edges only
    # Topologically sort the edges/nodes
    # Note: this may need to be revised to more fully support units/levels where one unit can nest within multiple other units (e.g., in some non-nested cases)
    ordered_units = list(nx.topological_sort(measurement_sub._graph))
    # If there is only one unit, there would be no nesting relationships to the set of ordered_units in case all measures come from the same unit
    if len(ordered_units) == 0:
        identifiers = gr.get_identifiers()
        assert len(identifiers) == 1
        ordered_units = [i.name for i in identifiers]

    return ordered_units


# Make random effects for main effects in @param variables
# The number of
def construct_random_effects_for_nests(
    gr: Graph, dv: AbstractVariable, variables: List[AbstractVariable]
) -> Set[RandomIntercept]:
    random_effects = set()
    variable_units = set()

    # Find all the units for all the variables involved
    dv_unit = gr.get_identifier_for_variable(dv)
    # Get list of all units
    all_ordered_units = find_ordered_list_of_units(
        gr=gr
    )  # returns a list of unit names for which there are nests relationships
    assert dv_unit.name in all_ordered_units
    idx = all_ordered_units.index(dv_unit.name)
    # For random effects due to nesting, focus on those that nest the unit that has the DV
    units_to_consider = all_ordered_units[idx + 1 :]

    # Add random effects for nested variables now
    for v in variables:
        v_unit = gr.get_identifier_for_variable(v)
        # Is the variable's unit the same as the dv's
        if v_unit is dv_unit:
            assert v_unit.name not in units_to_consider
            variable_units.add(v_unit.name)

        else:
            if v_unit is not None:
                if v_unit.name not in units_to_consider:
                    assert v_unit == v
                    assert isinstance(v, SetUp)
                else:
                    assert v_unit.name in units_to_consider

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


# "If a factor is within-unit and there are multiple observations per
# treatment level per unit, then you need a by-unit random slope for that
# TODO: Could this rule also apply if all the variables are units? or all measures?
# factor...." - Barr et al. 2013
def construct_random_effects_for_composed_measures(
    gr: Graph, variables: List[AbstractVariable]
) -> Set[RandomIntercept]:
    random_effects = set()

    # Go through the selected main effects, looking only for Measures
    for v in variables:
        if isinstance(v, Measure):
            for r in v.relationships:
                if isinstance(r, Has):
                    # Does this measure have/consist of units?
                    if v == r.variable and isinstance(r.measure, Unit):
                        v_unit = gr.get_identifier_for_variable(v)
                        (n0, n1, edge_data) = gr.get_edge(
                            start=v_unit, end=v, edge_type="has"
                        )
                        v_unit_has_obj = edge_data["edge_obj"]
                        assert isinstance(v_unit_has_obj.repetitions, NumberValue)
                        # Is variable v within-subjects?
                        if v_unit_has_obj.repetitions.is_greater_than_one():
                            # Does variable v have multiple instances of the unit r.measure?
                            if r.repetitions.is_greater_than_one():
                                # If so, for each instance of v_unit account for clusters in r.measure observations within each instance of v.
                                rs = RandomSlope(iv=v, groups=v_unit)
                                random_effects.add(rs)
                            # There is only one observation of r.measure per
                            # each v. This is like saying r.measure and v are
                            # 1:1, meaning they are redundant measures of each
                            # other. By transitive property, v_unit has multiple
                            # r.measure instances.
                            else:
                                assert v_unit_has_obj.repetitions.is_equal_to_one()
                                ri = RandomIntercept(groups=v_unit)
                                random_effects.add(ri)

    return random_effects


# Filter a set such that only one of each random effect per variable is returned
def filter_random_candidates(random_candidates: Set[RandomEffect]) -> Set[RandomEffect]:
    random_effects_names = set()
    random_effects = set()

    for rc in random_candidates:
        if isinstance(rc, RandomIntercept):
            name_key = (rc.groups.name, rc.__class__)
        else:
            assert isinstance(rc, RandomSlope)
            name_key = (rc.groups.name, rc.iv.name, rc.__class__)
        # Have we seen this before?
        if name_key in random_effects_names:
            pass
        else:  # This random effect is new!
            random_effects.add(rc)
            random_effects_names.add(name_key)

    return random_effects


def get_variables_in_interaction_effect(
    gr: Graph, interaction_effect: AbstractVariable
) -> List[AbstractVariable]:
    variables = list()

    interaction_effect_name = interaction_effect.name
    names = interaction_effect_name.split("*")
    # Get the variables that comprise @param interaction_effect
    for n in names:
        var = gr.get_variable(name=n)
        if var is None:
            import pdb

            pdb.set_trace()

        assert var is not None
        # Add to list of variables
        variables.append(var)

    return variables


def create_variable_from_set_of_variables(
    variables: Set[AbstractVariable],
) -> AbstractVariable:
    # Create new interaction variable
    names = [v.name for v in variables]
    names.sort()  # Alphabetize the names to avoid multiple interaction effects with inversed order of variable names
    name = "*".join(names)

    cardinality = 1
    for v in variables:
        if v.get_cardinality() is not None:
            cardinality *= v.get_cardinality()

    var = Nominal(
        name, cardinality=cardinality
    )  # Interaction variables are cast as nominal variables

    return var


def find_largest_subset_of_variables_that_vary_within_unit(
    gr: Graph, interaction_effect: AbstractVariable
) -> AbstractVariable:
    variables = get_variables_in_interaction_effect(
        gr=gr, interaction_effect=interaction_effect
    )
    subset = set()
    for v in variables:
        assert gr.has_variable(variable=v)
        v_unit = gr.get_identifier_for_variable(variable=v)
        # Is the variable a unit variable?
        if v == v_unit:
            # Get nesting parent
            for r in v.relationships:
                if isinstance(r, Nests):
                    if r.base == v:
                        subset.add(r.group)
        else:
            assert gr.has_variable(variable=v)
            v_unit = gr.get_identifier_for_variable(variable=v)
            if v_unit is None:
                import pdb

                pdb.set_trace()
            (n0, n1, edge_data) = gr.get_edge(start=v_unit, end=v, edge_type="has")
            edge_obj = edge_data["edge_obj"]
            # Is v is within-subjects?
            if edge_obj.repetitions.is_greater_than_one():
                subset.add(v)

    return subset


def get_identifier_for_subset_interaction(
    gr: Graph, interaction_effect: AbstractVariable
) -> AbstractVariable:
    units = set()

    variables = get_variables_in_interaction_effect(
        gr=gr, interaction_effect=interaction_effect
    )
    for v in variables:
        v_unit = gr.get_identifier_for_variable(variable=v)
        assert v_unit is not None
        units.add(v_unit)

    if len(units) == 1:
        return units.pop()
    else:
        ordered_list_units = find_ordered_list_of_units(gr=gr)
        highest_unit = units.pop()
        for u in units:
            if ordered_list_units.index(highest_unit.name) < ordered_list_units.index(
                u.name
            ):
                highest_unit = u
        return highest_unit


def interaction_is_all_within(
    interaction: AbstractVariable, within_subset: Set[AbstractVariable]
) -> bool:
    within_subset_names = [w.name for w in within_subset]
    within_subset_names.sort()  # interactions with variables in different orders are still the same effect
    ixn_var_names = interaction.name.split("*")
    ixn_var_names.sort()  # interactions with variables in different orders are still the same effect

    return within_subset_names == ixn_var_names


def construct_random_effects_for_interactions(
    gr: Graph, query: Design, interactions: Set[AbstractVariable]
) -> Set[RandomEffect]:
    random_effects = set()
    if interactions is None:
        return random_effects
    for ixn in interactions:
        within_subset = find_largest_subset_of_variables_that_vary_within_unit(
            gr=gr, interaction_effect=ixn
        )
        # Are all the variables in ixn within-subjects?
        if interaction_is_all_within(interaction=ixn, within_subset=within_subset):
            ixn_unit = gr.get_identifier_for_variable(variable=ixn)
            rs = RandomSlope(ixn, ixn_unit)
            random_effects.add(rs)
        # Are there any within-subjects variables in ixn?
        elif len(within_subset) > 0:
            # TODO: Below, May want to see if we can get an existing variable from @param gr?
            within_subset_variable = create_variable_from_set_of_variables(
                variables=within_subset
            )
            within_subset_variable_unit = get_identifier_for_subset_interaction(
                gr=gr, interaction_effect=within_subset_variable
            )
            assert isinstance(within_subset_variable_unit, Unit)
            rs = RandomSlope(within_subset_variable, within_subset_variable_unit)
            random_effects.add(rs)
        elif len(within_subset) == 0:
            ixn_names = ixn.name.split("*")
            ixn_variables = [gr.get_variable(name) for name in ixn_names]

            dv = query.dv
            dv_unit = gr.get_identifier_for_variable(dv)

            assert gr.has_edge(start=dv_unit, end=dv, edge_type="has")
            (n0, n1, edge_data) = gr.get_edge(start=dv_unit, end=dv, edge_type="has")
            edge_obj = edge_data["edge_obj"]

            if edge_obj.according_to is not None:
                for v in ixn_variables:
                    if edge_obj.according_to == v:
                        rs = RandomSlope(iv=v, groups=dv_unit)
                        random_effects.add(rs)

    return random_effects


# Infer candidate interaction effects for @param query given the relationships contained in @param gr
# @returns a tuple: (set of candidates, dictionary with the main effects and the reasons they are considered candidates)
def infer_random_effects_with_explanations(
    gr: Graph,
    query: Design,
    main_effects: List[AbstractVariable],
    interaction_effects: Set[AbstractVariable] = None,
):
    global explanations
    random_explanations = explanations["random effects"]

    random_candidates = set()
    random_candidates_explanations = dict()

    repeats_effects = construct_random_effects_for_repeated_measures(gr=gr, query=query)
    # repeats_names = filter_random_effects_involving_variables(main_effects, random_names=repeats_names)
    # Add to set of effects
    random_candidates = random_candidates.union(repeats_effects)

    # Add explanations
    for rc in repeats_effects:
        # Is the variable a new random effect candidate?
        if isinstance(rc, RandomIntercept):
            name_key = f"{rc.groups.name},{type(rc).__name__}"
        else:
            assert isinstance(rc, RandomSlope)
            name_key = f"{rc.groups.name}, {rc.iv.name}, {type(rc).__name__}"
        if name_key not in random_candidates_explanations.keys():
            # declare the list of explanations/reasons for this variable
            random_candidates_explanations[name_key] = list()
        # add explanation

        if isinstance(rc.groups, Unit) and gr.has_edge(
            start=rc.groups, end=query.dv, edge_type="has"
        ):
            groups = rc.groups.name
            # if not gr.has_edge(start=rc.groups, end=query.dv, edge_type="has"):
            #     import pdb; pdb.set_trace()
            (n0, n1, edge_data) = gr.get_edge(
                start=rc.groups, end=query.dv, edge_type="has"
            )
            has_relat = edge_data["edge_obj"]
            num_times_measured = has_relat.repetitions.get_value()
            distinguisher = has_relat.according_to.name
            # expl = random_explanations["repeated measures"].format(measure=query.dv.name, num_times_measured=num_times_measured, unit=groups, distinguisher=distinguisher)
            expl = random_explanations["repeated measures, unit"].format(
                measure=query.dv.name,
                num_times_measured=num_times_measured,
                unit=groups,
            )
            random_candidates_explanations[name_key].append(expl)
        else:
            # expl = f"There are multiple observations of {query.dv.name} for every {rc.groups.name}."
            expl = random_explanations["repeated measures, distinguisher"].format(
                measure=query.dv.name, distinguisher=rc.groups.name
            )
            random_candidates_explanations[name_key].append(expl)

    nests_effects = construct_random_effects_for_nests(
        gr=gr, dv=query.dv, variables=main_effects
    )
    # nests_variables = cast_to_variables(names=nests_names, variables=main_effects)
    random_candidates = random_candidates.union(nests_effects)
    # Add explanations
    for rc in nests_effects:
        # Is the variable a new random effect candidate?
        if isinstance(rc, RandomIntercept):
            name_key = f"{rc.groups.name},{type(rc).__name__}"
        else:
            assert isinstance(rc, RandomSlope)
            name_key = f"{rc.groups.name}, {rc.iv.name}, {type(rc).__name__}"
        if name_key not in random_candidates_explanations.keys():
            # declare the list of explanations/reasons for this variable
            random_candidates_explanations[name_key] = list()
        # add explanation
        units = find_ordered_list_of_units(gr)
        nested = rc.groups.name
        idx = units.index(nested)
        if idx + 1 < len(units):
            nesting = units[idx + 1]
        else:
            nesting = nested
            nested = units[idx - 1]
        expl = random_explanations["hierarchical data"].format(
            nested=nested, nesting=nesting
        )

        random_candidates_explanations[name_key].append(expl)

    composed_effects = construct_random_effects_for_composed_measures(
        gr=gr, variables=main_effects
    )
    random_candidates = random_candidates.union(composed_effects)
    # Add explanations
    for rc in composed_effects:
        # Is the variable a new random effect candidate?
        if isinstance(rc, RandomIntercept):
            name_key = f"{rc.groups.name},{type(rc).__name__}"
        else:
            assert isinstance(rc, RandomSlope)
            name_key = f"{rc.groups.name}, {rc.iv.name}, {type(rc).__name__}"
        if name_key not in random_candidates_explanations.keys():
            # declare the list of explanations/reasons for this variable
            random_candidates_explanations[name_key] = list()
        # add explanation
        expl = random_explanations["non-nesting"].format(groups=rc.groups.name)
        random_candidates_explanations[name_key].append(expl)

    interaction_random_effects = construct_random_effects_for_interactions(
        gr=gr, query=query, interactions=interaction_effects
    )
    random_candidates = random_candidates.union(interaction_random_effects)
    # Add explanations
    for rc in interaction_random_effects:
        assert isinstance(rc, RandomSlope)
        # Is the variable a new random effect candidate?
        # if isinstance(rc, RandomIntercept):
        #     name_key = f"{rc.groups.name},{type(rc).__name__}"
        # else:
        #     assert isinstance(rc, RandomSlope)

        name_key = f"{rc.groups.name}, {rc.iv.name}, {type(rc).__name__}"
        if name_key not in random_candidates_explanations.keys():
            # declare the list of explanations/reasons for this variable
            random_candidates_explanations[name_key] = list()

        # add explanation
        # Get unit for interaction effect
        unit = gr.get_identifier_for_variable(variable=rc.iv)
        assert unit is not None

        var_names = rc.iv.name.split("*")
        var_names_str = ",".join(var_names)
        expl = random_explanations["interaction"].format(
            unit=unit, variables=var_names_str
        )
        random_candidates_explanations[name_key].append(expl)

    random_candidates = filter_random_candidates(random_candidates)

    return (random_candidates, random_candidates_explanations)
