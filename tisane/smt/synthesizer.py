from tisane.graph import Graph
from tisane.variable import (
    Measure,
    Unit,
    AbstractVariable,
    Has,
    Associates,
    Causes,
    Moderates,
    Nests,
    Repeats,
)
from tisane.design import Design
from tisane.statistical_model import StatisticalModel
from tisane.smt.rules import *
from tisane.smt.rules import *
from tisane.smt.knowledge_base import KB
from tisane.random_effects import *

from z3 import *
import networkx as nx
from itertools import chain, combinations
from typing import List, Dict, Tuple
from copy import deepcopy
import json

# Declare data type
Object = DeclareSort("Object")


def powerset(iterable):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))


# Order the variables according to @param policy
# @param policy can be: 'alpha'
# @returns new list with @param variables ordered according to @param policy
def order_variables(variables: List[AbstractVariable], policy: str = "alpha"):
    variables_names = [v.name for v in variables]
    variables_names.sort()

    variables_ordered = list()
    for n in variables_names:
        for v in variables:
            if n == v.name:
                variables_ordered.append(v)
                break

    return variables_ordered


def parse_fact(fact: str) -> Dict[str, str]:
    fact_dict = dict()
    tmp = str(fact).split("(")
    func_name = tmp[0]
    fact_dict["function"] = func_name

    if func_name == "Interaction":
        arg_str = str(fact).split("False), ")

        assert len(arg_str) == 2
        arg_str = arg_str[1].split(",")

        # This for loop should take care of n-way Interactions
        variables = list()
        for s in arg_str:
            if "True" not in s:
                variables.append(s.strip())
        fact_dict["variables"] = variables
    else:
        variables = tmp[1].split(")")[0].split(",")

        if len(variables) == 1:
            fact_dict["variable_name"] = variables[0].strip()
        elif len(variables) == 2:
            fact_dict["start"] = variables[0].strip()
            fact_dict["end"] = variables[1].strip()

    return fact_dict


def cast_facts(facts: list, design: Design) -> List:
    z3_facts = list()
    for f in facts:
        fact_dict = parse_fact(f)
        if fact_dict["function"] == "FixedEffect":
            start_var = design.graph.get_variable(fact_dict["start"])
            end_var = design.graph.get_variable(fact_dict["end"])
            z3_facts.append(FixedEffect(start_var.const, end_var.const))

    return z3_facts


class Synthesizer(object):
    solver: z3.Solver
    facts: List

    def __init__(self):
        self.solver = Solver()
        self.facts = list()

    # @param outcome describes what the query result should be, can be a list of items,
    # including: statistical model, variable relationship graph, data schema, data collection procedure
    # @return logical rules to consider during solving process
    def collect_rules(self, output: str, **kwargs) -> Dict:
        # Get and manage the constraints that need to be considered from the rest of Knowledge Base
        rules_to_consider = dict()

        if output.upper() == "EFFECTS":
            assert "dv_const" in kwargs
            KB.ground_effects_rules(dv_const=kwargs["dv_const"])
            rules_to_consider["effects_rules"] = KB.effects_rules
        elif output.upper() == "FAMILY":
            assert "dv_const" in kwargs
            KB.ground_family_rules(dv_const=kwargs["dv_const"])
            rules_to_consider["family_rules"] = KB.family_rules
        elif output.upper() == "TRANSFORMATION":
            assert "dv_const" in kwargs
            KB.ground_data_transformation_rules(dv_const=kwargs["dv_const"])
            rules_to_consider[
                "family_to_transformation_rules"
            ] = KB.family_to_transformation_rules
            rules_to_consider[
                "data_transformation_rules"
            ] = KB.data_transformation_rules
        elif output.upper() == "DEFAULT_FAMILY_LINK":
            assert "dv_const" in kwargs
            KB.ground_data_transformation_rules(dv_const=kwargs["dv_const"])
            rules_to_consider[
                "default_family_to_transformation"
            ] = KB.default_family_to_transformation
        else:
            # TODO: Clean up further so only create Z3 rules/functions for the rules that are added?
            if output.upper() == "STATISTICAL MODEL":
                rules_to_consider["data_type_rules"] = KB.data_type_rules
                rules_to_consider[
                    "data_transformation_rules"
                ] = KB.data_transformation_rules
                rules_to_consider[
                    "variance_functions_rules"
                ] = KB.variance_functions_rules
            elif output.upper() == "CONCEPTUAL MODEL":
                rules_to_consider["graph_rules"] = KB.graph_rules
            # elif output.upper() == 'STUDY DESIGN':
            #     #
            #     # TODO: Should allow separate queries for data schema and data collection?? probably not?
            #     rules_to_consider['data_type_rules'] = KB.data_type_rules
            #     rules_to_consider['data_transformation_rules'] = KB.data_transformation_rules
            #     rules_to_consider['variance_functions_rules'] = KB.variance_functions_rules

            else:
                raise ValueError(f"Query output is not supported: {type(output_obj)}.")

        return rules_to_consider

    # Returns True if SAT, False otherwise
    def check_constraints(self, facts: list, rule_set: str, design: Design) -> bool:
        # Get rules
        rules_dict = self.collect_rules(output=rule_set, dv_const=design.dv.const)

        for batch_name, rules in rules_dict.items():
            # print(f'Adding {batch_name} rules.')
            # Add rules
            self.solver.add(rules)

        z3_facts = cast_facts(facts=facts, design=design)
        state = self.solver.check(z3_facts)

        return state == sat

        # if (state == unsat):
        #     # unsat_core = solver.unsat_core()

        #     # if len(unsat_core) == 0:
        #     #
        #     assert(len(unsat_core) > 0)
        #     return (state, unsat_core)
        # elif (state == sat):
        #     return state

    def update_with_facts(self, facts: List, rule_set: str, design: Design):
        # Get rules
        rules_dict = self.collect_rules(output=rule_set, dv_const=design.dv.const)

        for batch_name, rules in rules_dict.items():
            # print(f'Adding {batch_name} rules.')
            # Add rules incrementally
            for r in rules:
                if r not in self.solver.assertions():
                    self.solver.add(r)

        z3_facts = cast_facts(facts=facts, design=design)
        state = self.solver.check(z3_facts)
        assert state == sat

        # Store facts
        self.facts.append(z3_facts)

        # # Solve constraints + rules
        # (res_model_fixed, res_facts_fixed) = QM.solve(facts=fixed_facts, rules=rules_dict)

        # # Update result StatisticalModel based on user selection
        # sm = QM.postprocess_to_statistical_model(model=res_model_fixed, facts=res_facts_fixed, graph=design.graph, statistical_model=sm)

    # @param pushed_constraints are constraints that were added as constraints all at once but then caused a conflict
    # @param unsat_core is the set of cosntraints that caused a conflict
    # @param keep_clause is the clause in unsat_core to keep and that resolves the conflict
    def update_clauses(self, pushed_constraints: list, unsat_core: list, keep_clause):
        #
        # Verify that keep_clause is indeed a subset of unsat_core
        if keep_clause not in unsat_core:
            raise ValueError(
                f"Keep clause ({keep_clause}) not in unsat_core({unsat_core})"
            )

        assert keep_clause in unsat_core

        updated_constraints = list()
        # Add the keep clause
        updated_constraints.append(keep_clause)

        # If this keep clause is about Not Transforming data
        # TODO: Probably revise this
        if "NoTransform" in str(keep_clause):
            fact_dict = parse_fact(keep_clause)
            assert "variable_name" in fact_dict
            var_name = fact_dict["variable_name"]

            for pc in pushed_constraints:
                # If pc is not keep_clause (already added to updated_constraints)
                if str(pc) != str(keep_clause):
                    # Is the pushed consctr, aint about the same variable as the keep clause (NoTransform)?
                    if var_name in str(pc):
                        # Keep the pushed constraint as long as it is not about
                        # transforming the variable
                        if "Transform" not in str(pc):
                            updated_constraints.append(pc)
                    else:
                        updated_constraints.append(pc)
        # elif 'NumericDataType' in str(keep_clause):
        #     fact_dict = parse_fact(keep_clause)
        #     assert('variable_name' in fact_dict)
        #     var_name = fact_dict['variable_name']

        #     for pc in pushed_constraints:
        #         # If pc is not keep_clause (already added to updated_constraints)
        #         if str(pc) != str(keep_clause):
        #             # Is the pushed consctraint about the same variable as the keep clause (NoTransform)?
        #             if var_name in str(pc):
        #                 # Keep the pushed constraint as long as it is not about
        #                 # categorical data types
        #                 if 'CategoricalDataType' not in str(pc) and 'NominalDataType' not in str(pc) and 'OrdinalDataType' not in str(pc):
        #                     updated_constraints.append(pc)
        #             else:
        #                 updated_constraints.append(pc)
        # If this keep clause is about anything else other than Not Transforming data
        else:
            for pc in pushed_constraints:
                # If pc is not keep_clause (already added to updated_constraints)
                if str(pc) != str(keep_clause):
                    # Should we remove this constraint because it caused UNSAT?
                    if pc in unsat_core:
                        pass
                    else:
                        updated_constraints.append(pc)

        # TODO: This may not generalize to n-way interactions
        # TODO: We want the end-user to provide hints towards interesting interactions
        return updated_constraints

    def check_update_constraints(self, solver: Solver, assertions: list) -> List:
        #
        state = solver.check(assertions)
        if state == unsat:
            unsat_core = solver.unsat_core()

            if len(unsat_core) == 0:
                raise ValueError(f"Unsat core: {unsat_core} is len==0")
            assert len(unsat_core) > 0

            # Ask user for input
            keep_constraint = InputInterface.resolve_unsat(
                facts=solver.assertions(), unsat_core=unsat_core
            )
            # keep_constraint = self.elicit_user_input(solver.assertions(), unsat_core)

            # Modifies @param assertions
            updated_assertions = self.update_clauses(
                assertions, unsat_core, keep_constraint
            )
            assertions = updated_assertions

            new_state = solver.check(assertions)

            if new_state == sat:
                return (solver, assertions)
            elif new_state == unsat:
                return self.check_update_constraints(
                    solver=solver, assertions=assertions
                )
            else:
                raise ValueError(
                    f"After eliciting end-user input, solver state is neither SAT nor UNSAT: {new_state}"
                )
        elif state == sat:
            return (solver, assertions)
        else:
            raise ValueError(
                f"Initial solver state into check_update_constraints is {state}"
            )

    # @param setting is 'interactive' 'default' (which is interactive), etc.?
    def solve(self, facts: List, rules: dict, setting=None):
        s = Solver()  # Z3 solver

        for batch_name, rule_set in rules.items():
            # print(f'Adding {batch_name} rules.')
            # Add rules
            s.add(rule_set)

        s.check(facts)
        mdl = s.model()

        return mdl

    # Reduce the graph associated with @param Design
    # Remove cycles in graph based on the DV
    def reduce_graph_old(self, graph: Graph, dv: AbstractVariable):
        gr_copy = deepcopy(graph._graph)
        dv_name = dv.name

        # Iterate over outgoing edges from design.dv
        for n in graph._graph.neighbors(dv_name):
            gr_copy.remove_edge(dv_name, n)

        return gr_copy

    def reduce_graph(self, graph: Graph, dv: AbstractVariable):
        # Remove outgoing edges from DV
        gr = graph.remove_outgoing_edges(dv)
        # Get only causal subgraph of this gr
        reduced_gr = gr.get_causal_subgraph()

        # Add back in associations to DV
        gr_edges = gr.get_edges()
        causal_edges = reduced_gr.get_edges()

        for e in gr_edges:
            if e not in causal_edges:
                (n0, n1, edge_data) = e
                edge_type = edge_data["edge_type"]
                if edge_type == "associate" and n1 == dv.name:
                    n0_var = gr.get_variable(n0)
                    n1_var = gr.get_variable(n1)

                    reduced_gr._add_edge(n0_var, n1_var, edge_type)

        return reduced_gr

    def _generate_fixed_candidates(self, design: Design) -> Dict:
        fixed_candidates = dict()
        # fixed_candidates = list()

        ### Add candidates that are directly part of design
        fixed_candidates["input"] = order_variables(design.ivs)

        ### Find candidates based on predecessors to the @param design.dv
        direct_pred_candidates = list()
        # Get the predecessors to the DV
        dv_pred = design.graph.get_predecessors(design.dv)
        for p in dv_pred:
            p_var = design.graph.get_variable(name=p)
            if design.graph.has_edge(start=p_var, end=design.dv, edge_type="cause"):
                direct_pred_candidates.append(p_var)
            elif design.graph.has_edge(
                start=p_var, end=design.dv, edge_type="associate"
            ):
                direct_pred_candidates.append(p_var)
        # Filter out any candidates that were already part of the input set and therefore already part of fixed_candidates
        direct_pred_filtered = list()
        for c in direct_pred_candidates:
            if c not in fixed_candidates["input"]:
                direct_pred_filtered.append(c)
        fixed_candidates["derived_direct"] = order_variables(direct_pred_filtered)

        ### Find candidates based on transitive conceptual relationships
        """
        Two use cases: 
        (1) X1 -> X2 -> Y => X1, X2 are fixed candidates
        (2) X1 -> Y, X2 -> Y, X3 -> X1, X3 -> X2 => X1, X2, X3 are fixed candidates
        """
        # Get transitive closure of graph with reduced graph (remove cycles)
        gr = design.graph._graph
        reduced_gr = self.reduce_graph_old(design.graph, design.dv)
        tc = nx.transitive_closure_dag(reduced_gr)
        transitive_pred_candidates = list()
        # Get the predecessors to the DV
        dv_node = design.graph.get_node(
            design.dv
        )  # Returns tuple: (name, data{variable, is_identifier})
        dv_pred = tc.predecessors(dv_node[0])
        for p in dv_pred:
            p_var = design.graph.get_variable(name=p)
            # If the variable was not part of the original graph
            p_node = design.graph.get_node(p_var)
            # If the variable is not an identifier
            if not p_node[1]["is_identifier"]:
                if p_var not in direct_pred_candidates:
                    transitive_pred_candidates.append(p_var)
        fixed_candidates["derived_transitive"] = order_variables(
            transitive_pred_candidates
        )

        return fixed_candidates

    def _generate_fixed_candidates_from_graph(
        self, graph: Graph, ivs: List[AbstractVariable], dv: AbstractVariable
    ) -> Dict:
        fixed_candidates = dict()

        ### Add candidates that are directly part of design
        graph_ivs = [graph.get_variable(i.name) for i in ivs]
        # import pdb; pdb.set_trace()
        # get rid of none
        graph_ivs = [v for v in graph_ivs if v is not None]
        fixed_candidates["input"] = order_variables(graph_ivs)

        ### Find candidates based on predecessors to the @param dv
        direct_pred_candidates = list()
        # Get the predecessors to the DV
        graph_dv = graph.get_variable(dv.name)
        dv_pred = graph.get_predecessors(graph_dv)
        if dv_pred is not None:
            for p in dv_pred:
                p_var = graph.get_variable(name=p)
                if graph.has_edge(start=p_var, end=graph_dv, edge_type="cause"):
                    direct_pred_candidates.append(p_var)
                elif graph.has_edge(start=p_var, end=graph_dv, edge_type="associate"):
                    direct_pred_candidates.append(p_var)
        # Filter out any candidates that were already part of the input set and therefore already part of fixed_candidates
        direct_pred_filtered = list()
        for c in direct_pred_candidates:
            if c not in fixed_candidates["input"]:
                direct_pred_filtered.append(c)
        fixed_candidates["derived_direct"] = order_variables(direct_pred_filtered)

        ### Find candidates based on transitive conceptual relationships
        """
        Two use cases: 
        (1) X1 -> X2 -> Y => X1, X2 are fixed candidates
        (2) X1 -> Y, X2 -> Y, X3 -> X1, X3 -> X2 => X1, X2, X3 are fixed candidates
        """

        # Prep graph to take transitive closure
        reduced_gr = self.reduce_graph(graph, graph_dv)
        tc = nx.transitive_closure_dag(reduced_gr._graph)
        # Filter reduced graph to only include relationships/edges to DV
        dv_node = graph.get_node(
            graph_dv
        )  # Returns tuple: (name, data{variable, is_identifier})
        dv_pred = tc.predecessors(dv_node[0])
        transitive_pred_candidates = list()
        for (n0, n1, edge_data) in tc.edges(data=True):
            if n1 == dv.name:
                p_var = graph.get_variable(name=n0)
                if (p_var not in fixed_candidates["input"]) and (
                    p_var not in fixed_candidates["derived_direct"]
                ):
                    transitive_pred_candidates.append(p_var)
        fixed_candidates["derived_transitive"] = order_variables(
            transitive_pred_candidates
        )

        # # Get the predecessors to the DV
        # for p in dv_pred:
        #     p_var = graph.get_variable(name=p)
        #     # If the variable was not part of the original graph
        #     p_node = graph.get_node(p_var)
        #     # If the variable is not an identifier
        #     if not p_node[1]['is_identifier']:
        #         if p_var not in direct_pred_candidates:
        #             transitive_pred_candidates.append(p_var)
        # fixed_candidates['derived_transitive'] = order_variables(transitive_pred_candidates)

        return fixed_candidates

    def generate_main_effects(self, design: Design) -> Dict:
        fixed_candidates = self._generate_fixed_candidates(design)

        return fixed_candidates

    def generate_main_effects_from_graph(
        self, graph: Graph, ivs: List[AbstractVariable], dv: AbstractVariable
    ) -> Dict:
        # Only the conceptual relationshpis are considered for deriving candidate fixed/main effects
        sub_gr = graph.get_conceptual_subgraph()
        assert isinstance(sub_gr, Graph)

        main_candidates = self._generate_fixed_candidates_from_graph(sub_gr, ivs, dv)

        return main_candidates

    def generate_fixed_effects_candidates(self, design: Design) -> Dict:
        fixed_candidates = self._generate_fixed_candidates(design)

        return fixed_candidates

    # def generate_interaction_effects(self, design: Design) -> Dict:
    #     fixed_candidates = self._generate_fixed_candidates(design)

    #     interaction_facts = dict()
    #     dv = design.dv

    #     # Generate possible interaction candidates from fixed_candidates
    #     interaction_candidates = [c for c in powerset(fixed_candidates) if len(c)>=2]

    #     # Get facts
    #     interaction_seq = None
    #     for ixn in interaction_candidates:
    #         # Build interaction sequence
    #         # interaction = EmptySet(Object)
    #         # for v in ixn:
    #         #     interaction = SetAdd(interaction, v.const)

    #         # Two-way interaction
    #         if len(ixn) == 2:
    #             if 'two-way' not in interaction_facts.keys():
    #                interaction_facts['two-way'] = list()

    #             interaction_dict = dict()
    #             interaction_name = list()
    #             interaction = EmptySet(Object)
    #             for v in ixn:
    #                 interaction_name.append(v.name)
    #                 interaction = SetAdd(interaction, v.const)
    #             interaction_dict['*'.join(interaction_name)] = Interaction(interaction)

    #             interaction_facts['two-way'] = interaction_dict

    #         # Three-way interaction
    #         # elif len(ixn) == 3:
    #         #     if 'three-way' not in interaction_facts.keys():
    #         #        interaction_facts['three-way'] = list()

    #         #     interaction_dict = dict()
    #         #     interaction_name = list()
    #         #     interaction = EmptySet(Object)
    #         #     for v in ixn:
    #         #         interaction_name.append(v.name)
    #         #         interaction = SetAdd(interaction, v.const)
    #         #     interaction_dict['*'.join(interaction_name)] = Interaction(interaction)

    #         #     interaction_facts['three-way'] = interaction_dict
    #         else:
    #             if 'n-way' not in interaction_facts.keys():
    #                interaction_facts['n-way'] = list()

    #             interaction_dict = dict()
    #             interaction_name = list()
    #             interaction = EmptySet(Object)
    #             for v in ixn:
    #                 interaction_name.append(v.name)
    #                 interaction = SetAdd(interaction, v.const)
    #             interaction_dict['*'.join(interaction_name)] = Interaction(interaction)

    #             interaction_facts['n-way'] = interaction_dict

    #         # interaction_facts.append(Interaction(interaction))
    #         # interaction_facts.append(NoInteraction(interaction))

    #         # interaction_seq = None

    #     # if 'three-way' not in interaction_facts.keys():
    #     #     interaction_facts['three-way'] = None
    #     if 'n-way' not in interaction_facts.keys():
    #         interaction_facts['n-way'] = None
    #     return interaction_facts

    #     # # Use rules from above

    #     # # Solve constraints + rules
    #     # (res_model_interaction, res_facts_interaction) = self.solve(facts=interaction_facts, rules=rules_dict)

    #     # # Update result StatisticalModel based on user selection
    #     # sm = self.postprocess_to_statistical_model(model=res_model_interaction, facts=res_facts_interaction, graph=design.graph, statistical_model=sm)

    def generate_interaction_effects(self, design: Design):
        interaction_facts = dict()
        dv = design.dv

        fixed_candidates = self._generate_fixed_candidates(design)  # Returns a dict
        # Collapse fixed_candidates dict into list
        fixed_candidates_list = list()
        for (key, value) in fixed_candidates.items():
            fixed_candidates_list += value

        # Generate possible interaction candidates from fixed_candidates
        interaction_candidates = [
            c for c in powerset(fixed_candidates_list) if len(c) >= 2
        ]
        interaction_facts["two-way"] = [
            c for c in interaction_candidates if len(c) == 2
        ]
        interaction_facts["n-way"] = [c for c in interaction_candidates if len(c) > 2]

        return interaction_facts

    def generate_interaction_effects_from_graph(
        self, graph: Graph, ivs: List[AbstractVariable], dv: AbstractVariable
    ):
        interaction_facts = dict()
        graph_dv = graph.get_variable(
            dv.name
        )  # Because graph may be a transformed copy of the original graph dv belongs to

        fixed_candidates = self._generate_fixed_candidates_from_graph(
            graph, ivs, graph_dv
        )  # Returns a dict
        # Collapse fixed_candidates dict into list
        fixed_candidates_list = list()
        for (key, value) in fixed_candidates.items():
            fixed_candidates_list += value

        # Generate possible interaction candidates from fixed_candidates
        interaction_candidates = [
            c for c in powerset(fixed_candidates_list) if len(c) >= 2
        ]
        interaction_facts["two-way"] = [
            c for c in interaction_candidates if len(c) == 2
        ]
        interaction_facts["n-way"] = [c for c in interaction_candidates if len(c) > 2]

        return interaction_facts

    # Build up maximal effects structure following Barr et al. 2012
    def generate_random_effects(self, design: Design) -> set:
        random_effects = set()

        # Identify the units
        identifiers = design.graph.get_identifiers()

        # There is only one level
        if len(identifiers) == 1:
            return None

        # There multiple levels or units

        # For each MAIN effect
        fixed_candidates = self._generate_fixed_candidates(design)
        # If it is "between-subjects" create a random intercept for the unit
        # If it is "within-subjects" create a random slope + intercept
        for i in identifiers:
            for (key, fixed) in fixed_candidates.items():
                for f in fixed:
                    if design.graph.has_edge(start=i, end=f, edge_type="has"):
                        (start_name, end_name, edge_data) = design.graph.get_edge(
                            start=i, end=f, edge_type="has"
                        )
                        rep = edge_data["repetitions"]
                        if isinstance(rep, int):
                            rep_count = rep
                        else:
                            rep_count = 2  # GreaterThanOne
                        # Is this a between subjects edge?
                        if rep_count == 1:
                            ri = RandomInterceptEffect(i.const)
                            random_effects.add((ri, RandomIntercept(i)))

                            # # Does the identifier already have a set of random effects associated with it?
                            # if i.name not in variables_to_effects.keys():
                            #     variables_to_effects[i.name] = set()
                            # # Add effect
                            # variables_to_effects[i.name] = variables_to_effects[i.name].append(ri)

                        # Is this a within subjects edge?
                        elif rep_count > 1:
                            ri = RandomInterceptEffect(i.const)
                            # rs = RandomSlopeEffect(f.const, i.const)
                            crsi = CorrelatedRandomSlopeInterceptEffects(
                                f.const, i.const
                            )
                            ursi = UncorrelatedRandomSlopeInterceptEffects(
                                f.const, i.const
                            )

                            random_effects.add((ri, RandomIntercept(i)))
                            random_effects.add(
                                (
                                    crsi,
                                    CorrelatedRandomSlopeAndIntercept(iv=f, groups=i),
                                )
                            )
                            random_effects.add(
                                (
                                    ursi,
                                    UncorrelatedRandomSlopeAndIntercept(iv=f, groups=i),
                                )
                            )
                            # random_effects.add((rs, RandomSlope(iv=f, groups=i)))

        # For each INTERACTION effect
        interaction_candidates = self.generate_interaction_effects(design)  # dict

        for key, interactions in interaction_candidates.items():

            for ixn in interactions:
                all_within = True
                for v in ixn:
                    if all_within:
                        # If all variables involved are "within-subjects" create random slope for the unit
                        if design.graph.has_edge(start=i, end=v, edge_type="has"):
                            (start_name, end_name, edge_data) = design.graph.get_edge(
                                start=i, end=v, edge_type="has"
                            )
                            if edge_data["repetitions"] == 1:
                                all_within = False
                if all_within:
                    ri = RandomInterceptEffect(i.const)
                    rs = RandomSlopeEffect(
                        ixn, i.const
                    )  # Add a random slope for the unit variable
                    random_effects.add((ri, RandomIntercept(i)))
                    random_effects.add((rs, RandomSlope(iv=ixn, groups=i)))

        # Return random effects
        return random_effects

    def get_valid_levels(self, graph: Graph, dv: AbstractVariable):
        graph_dv = graph.get_variable(dv)

        # Identify the units
        identifiers = graph.get_identifiers()

        # There is only one level
        if len(identifiers) == 1:
            return identifiers

        # # There multiple levels or units
        # # TODO: Find level of DV
        # levels_to_consider = list()
        # dv_level = None
        # for i in identifiers:
        #     if graph.has_edge(i, dv, 'has'):
        #         dv_level = i
        #         break

        # # dv_level_node = graph.get_node(dv_level)
        # for i in identifiers:
        #     if i != dv_level:
        #         # i_node = graph.get_node(i)
        #         paths = list(nx.all_simple_paths(graph._graph, source=i.name, target=dv_level.name))
        #         # There is a path, means level i is connected to level dv_level
        #         if len(paths) > 0:
        #             levels_to_consider.append(i)

        # levels_to_consider.append(dv_level)

        levels_to_consider = identifiers
        return levels_to_consider

    def generate_random_effects_for_main_effects(
        self, graph: Graph, ivs: List[AbstractVariable], dv: AbstractVariable
    ) -> set:
        random_effects = set()

        levels = self.get_valid_levels(graph, dv)

        # For each MAIN effect
        fixed_candidates = self._generate_fixed_candidates_from_graph(graph, ivs, dv)

        levels_included = list()
        for (key, fixed) in fixed_candidates.items():
            for f in fixed:
                # get parent
                parent = None
                for l in levels:
                    if graph.has_edge(start=l, end=f, edge_type="has"):
                        parent = l

                        break

                if parent is not None:
                    (start_name, end_name, edge_data) = graph.get_edge(
                        start=l, end=f, edge_type="has"
                    )
                    # Is this a between subjects edge?
                    if edge_data["repetitions"] == 1:
                        ri = RandomInterceptEffect(parent.const)
                        random_effects.add((ri, RandomIntercept(parent)))

                    # Is this a within subjects edge?
                    elif edge_data["repetitions"] > 1:
                        ri = RandomInterceptEffect(parent.const)
                        # rs = RandomSlopeEffect(f.const, i.const)
                        crsi = CorrelatedRandomSlopeInterceptEffects(
                            f.const, parent.const
                        )
                        ursi = UncorrelatedRandomSlopeInterceptEffects(
                            f.const, parent.const
                        )

                        random_effects.add((ri, RandomIntercept(parent)))
                        random_effects.add(
                            (
                                crsi,
                                CorrelatedRandomSlopeAndIntercept(iv=f, groups=parent),
                            )
                        )
                        random_effects.add(
                            (
                                ursi,
                                UncorrelatedRandomSlopeAndIntercept(
                                    iv=f, groups=parent
                                ),
                            )
                        )

                    levels_included.append(parent)

        # Should we include other random effects based on the levels that are already included?
        for l in levels:
            for li in levels_included:
                if graph.has_edge(start=li, end=l, edge_type="has"):
                    (start_name, end_name, edge_data) = graph.get_edge(
                        start=li, end=l, edge_type="has"
                    )

                    if edge_data["repetitions"] == 1:
                        ri = RandomInterceptEffect(l.const)
                        random_effects.add((ri, RandomIntercept(l)))

        # import pdb; pdb.set_trace()

        # If it is "between-subjects" create a random intercept for the unit
        # If it is "within-subjects" create a random slope + intercept
        # for i in levels:
        #     for (key, fixed) in fixed_candidates.items():
        #         for f in fixed:
        #             if graph.has_edge(start=i, end=f, edge_type='has'):
        #                 (start_name, end_name, edge_data) = graph.get_edge(start=i, end=f, edge_type='has')
        #                 # Is this a between subjects edge?
        #                 if edge_data['repetitions'] == 1:
        #                     ri = RandomInterceptEffect(i.const)
        #                     random_effects.add((ri, RandomIntercept(i)))

        #                 # Is this a within subjects edge?
        #                 elif edge_data['repetitions'] > 1:
        #                     ri = RandomInterceptEffect(i.const)
        #                     # rs = RandomSlopeEffect(f.const, i.const)
        #                     crsi = CorrelatedRandomSlopeInterceptEffects(f.const, i.const)
        #                     ursi = UncorrelatedRandomSlopeInterceptEffects(f.const, i.const)

        #                     random_effects.add((ri, RandomIntercept(i)))
        #                     random_effects.add((crsi, CorrelatedRandomSlopeAndIntercept(iv=f, groups=i)))
        #                     random_effects.add((ursi, UncorrelatedRandomSlopeAndIntercept(iv=f, groups=i)))
        #                     # random_effects.add((rs, RandomSlope(iv=f, groups=i)))
        #             elif graph.has_edge(start=f, end=i, edge_type='has'):
        #                 # This only happens when both f and i are identifiers
        #                 assert(i in levels)
        #                 assert(f in levels)
        #                 (start_name, end_name, edge_data) = graph.get_edge(start=f, end=i, edge_type='has')
        #                 rep = edge_data['repetitions']
        #                 if isinstance(rep, int):
        #                     rep_count = rep
        #                 else:
        #                     rep_count = 2 # GreaterThanOne

        #                 # Is this a between subjects edge?
        #                 if rep_count == 1:
        #                     ri = RandomInterceptEffect(i.const)
        #                     random_effects.add((ri, RandomIntercept(i)))

        #                 # Is this a within subjects edge?
        #                 elif rep_count > 1:
        #                     ri = RandomInterceptEffect(i.const)
        #                     # rs = RandomSlopeEffect(f.const, i.const)
        #                     crsi = CorrelatedRandomSlopeInterceptEffects(f.const, i.const)
        #                     ursi = UncorrelatedRandomSlopeInterceptEffects(f.const, i.const)

        #                     random_effects.add((ri, RandomIntercept(i)))
        #                     random_effects.add((crsi, CorrelatedRandomSlopeAndIntercept(iv=f, groups=i)))
        #                     random_effects.add((ursi, UncorrelatedRandomSlopeAndIntercept(iv=f, groups=i)))

        # import pdb; pdb.set_trace()
        return random_effects

    # Follows updated Barr guidelines from https://www.frontiersin.org/articles/10.3389/fpsyg.2013.00328/full
    def generate_random_effects_for_interaction_effects(
        self, graph: Graph, ivs: List[AbstractVariable], dv: AbstractVariable
    ):
        random_effects = set()

        interaction_candidates = self.generate_interaction_effects_from_graph(
            graph, ivs, dv
        )  # dict

        levels = self.get_valid_levels(graph, dv)
        # Go through two-way, n-way individually
        for key, interactions in interaction_candidates.items():

            # For each k-way interaction (e.g., All two-way interactions)
            for ixn in interactions:

                within_subjects_subset = list()
                per_ixn_random_effects = list()
                # For each variable involved in the current k-way interaction
                for v in ixn:
                    # If the variable is  "within-subjects" create random slope for the unit
                    # v_id = graph.get_identifier_for_variable(v)

                    for l in levels:
                        edge = graph.get_edge(start=l, end=v, edge_type="has")
                        # import pdb; pdb.set_trace()
                        if edge is not None:
                            # assert(l == v_id)
                            (start_name, end_name, edge_data) = edge
                            if edge_data["repetitions"] > 1:
                                ri = RandomInterceptEffect(l.const)
                                rs = RandomSlopeEffect(
                                    v.const, l.const
                                )  # Add a random slope for the unit variable

                                per_ixn_random_effects.append((ri, RandomIntercept(l)))
                                per_ixn_random_effects.append((rs, RandomSlope(v, l)))

                                within_subjects_subset.append(v)

                                break
                for (
                    e
                ) in per_ixn_random_effects:  # Add individual variable random effects
                    random_effects.add(e)
                # Add combination random effects
                if len(within_subjects_subset) > 1:
                    combin = tuple(within_subjects_subset)
                    if len(levels) == 1:
                        group = levels[0]
                    else:
                        # group = levels[len(levels) - 1] # same level as DV
                        for l in levels:
                            if graph.has_edge(start=l, end=dv, edge_type="has"):
                                group = l
                                break
                    ri = RandomInterceptEffect(group.const)
                    rs = RandomSlopeEffect(
                        group.const, group.const
                    )  # Add a random slope for the combined interaction variable

                    per_ixn_random_effects.append((ri, RandomIntercept(group)))
                    per_ixn_random_effects.append((rs, RandomSlope(combin, group)))
                    random_effects.add((ri, RandomIntercept(group)))
                    random_effects.add((rs, RandomSlope(combin, group)))

        keep = list()
        # Remove redundancies
        for (fact, re) in random_effects:
            if len(keep) == 0:
                keep.append((fact, re))
            else:
                in_keep = False
                for (k_fact, k_re) in keep:
                    if str(fact) == str(k_fact):
                        if type(re) == type(k_re):
                            in_keep = True

                if not in_keep:
                    keep.append((fact, re))

        return set(keep)
        # return keep

    # Build up maximal effects structure following Barr et al. 2012
    def generate_random_effects_from_graph(
        self, graph: Graph, ivs: List[AbstractVariable], dv: AbstractVariable
    ) -> set:
        random_effects = set()
        graph_dv = graph.get_variable(dv)

        levels = self.get_valid_levels(graph, dv)

        if len(levels) == 1:
            return None

        ### MAIN EFFECTS
        # Add random effects derived for main effects
        re_main = self.generate_random_effects_for_main_effects(graph, ivs, dv)
        for e in re_main:
            random_effects.add(e)

        ### INTERACTION EFFECTS
        # Add random effects derived for interaction effects
        re_ixn = self.generate_random_effects_for_interaction_effects(graph, ivs, dv)
        for e in re_ixn:
            random_effects.add(e)

        # Filter out redundancies
        keep = set()
        for (fact, re) in random_effects:
            if len(keep) == 0:
                keep.add((fact, re))
            else:
                in_keep = False
                for (k_fact, k_re) in keep:
                    if str(k_fact) == str(fact):
                        in_keep = True
                if not in_keep:
                    keep.add((fact, re))

        # Return random effects
        return random_effects

    def generate_family_link(
        self, design: Design
    ) -> Dict[z3.BoolRef, List[z3.BoolRef]]:
        family_link = dict()

        for family_fact in self.generate_family_distributions(design):
            family_link[family_fact] = self.generate_link_functions(
                design=design, family_fact=family_fact
            )

        return family_link

    def generate_family_distributions(self, design: Design) -> List[z3.BoolRef]:
        family_facts = list()

        # Get facts from data types
        dv = design.dv
        if isinstance(dv, Numeric) or isinstance(dv, Ordinal):
            family_facts.append(GaussianFamily(dv.const))
            family_facts.append(InverseGaussianFamily(dv.const))
            family_facts.append(GammaFamily(dv.const))
            family_facts.append(TweedieFamily(dv.const))
            family_facts.append(PoissonFamily(dv.const))
        # if isinstance(dv, Count):
        #     family_facts.append(PoissonFamily(dv.const))
        # if isinstance(dv, Time):
        #     family_facts.append(GaussianFamily(dv.const))
        #     family_facts.append(InverseGaussianFamily(dv.const))
        #     # Expontential distribution would go here
        #     family_facts.append(GammaFamily(dv.const))
        #     family_facts.append(TweedieFamily(dv.const))
        if isinstance(dv, Nominal) or isinstance(dv, Ordinal):
            if dv.cardinality is not None:
                if dv.cardinality == 2:
                    family_facts.append(BinomialFamily(dv.const))
                    family_facts.append(NegativeBinomialFamily(dv.const))
                elif dv.cardinality > 2:
                    family_facts.append(MultinomialFamily(dv.const))
            else:
                pass

        return family_facts

    def generate_link_functions(self, design: Design, family_fact: z3.BoolRef):

        # Find possible link functions
        dv = design.dv
        # Get rules for families and valid data transformations/link functions
        rules_dict = self.collect_rules(output="TRANSFORMATION", dv_const=dv.const)
        family_to_transformation_rules = rules_dict["family_to_transformation_rules"]
        # Solve fact + rules to get possible link functions
        res_model_transformations = self.solve(
            facts=family_fact,
            rules={"family_to_transformation_rules": family_to_transformation_rules},
        )
        # Get link facts
        transformation_candidate_facts = self.model_to_transformation_facts(
            model=res_model_transformations, design=design
        )

        return transformation_candidate_facts

    def generate_default_family_link(self, design: Design):
        default_family_to_link = dict()

        dv = design.dv
        # Get rules for families and valid data transformations/link functions
        rules_dict = self.collect_rules(output="DEFAULT_FAMILY_LINK", dv_const=dv.const)
        default_family_to_transformation_rules = rules_dict[
            "default_family_to_transformation"
        ]

        for family_fact in self.generate_family_distributions(design):
            # Solve fact + rules to get possible link functions
            res_model_transformations = self.solve(
                facts=family_fact,
                rules={
                    "default_family_to_transformation": default_family_to_transformation_rules
                },
            )
            # Get link facts
            default_transformation_fact = self.model_to_transformation_facts(
                model=res_model_transformations, design=design
            )

            default_family_to_link[family_fact] = default_transformation_fact

        return default_family_to_link

    # Compile Statistical Model from JSON facts
    # @returns StatisticalModel with properties initialized with values in @param model_json
    def create_statistical_model(self, model_json: str, design: Design):
        def get_variable(design: Design, var_name: str):
            # List of variables in @param design
            variables = design.graph.get_variables()

            for v in variables:
                if v.name == var_name:
                    return v

        tmp = json.loads(model_json)  # read in json
        model_spec = json.loads(tmp)  # Json to Dict

        # TODO: Rename SM fixed_ivs to main_ivs
        main_effects = list()
        interaction_effects = list()
        random_effects = list()
        family = None
        link = None

        for (
            key,
            facts,
        ) in model_spec.items():

            if key == "main_effects":
                for f in facts:
                    assert isinstance(f, str)
                    assert "FixedEffect" in f
                    var_names = f.split("FixedEffect(")[1].split(",")
                    iv_name = var_names[0].strip()
                    dv_name = var_names[1].split(")")[0].strip()
                    if design.dv.name != dv_name:
                        raise ValueError(f"Fact does not have DV as recipient!{f}")
                    assert design.dv.name == dv_name

                    v = get_variable(design, iv_name)
                    main_effects.append(v)

            elif key == "interaction_effects":
                for f in facts:
                    assert "Store(K(Object, False)," in f

                    var_names = f.split("Store(K(Object, False),")[1].split("True)")
                    ixn = list()
                    # Get var names
                    cleaned_var_names = list()
                    for v in var_names:
                        clean = v.strip()
                        clean = clean.split(",")

                        for c in clean:
                            if len(c) > 0:
                                cleaned_var_names.append(c.strip())

                    # Get variables
                    for n in cleaned_var_names:
                        v = get_variable(design, n)
                        ixn.append(v)
                    interaction_effects.append(tuple(ixn))

            elif key == "random_effects":
                for f in facts:
                    assert "Random" in f
                    if "RandomSlopeEffect" in f:
                        var_names = f.split("RandomSlopeEffect(")[1].split(",")
                        iv_name = var_names[0].strip()
                        group_name = var_names[1].split(")")[0].strip()

                        iv = get_variable(design, iv_name)
                        group = get_variable(design, group_name)
                        random_effects.append(RandomSlope(iv=iv, groups=group))

                    elif "RandomInterceptEffect" in f:
                        var_name = f.split("RandomInterceptEffect(")[1]
                        var_name = var_name.split(")")[0].strip()

                        v = get_variable(design, var_name)
                        random_effects.append(RandomIntercept(v))

                    elif "CorrelatedRandomSlopeInterceptEffects" in f:
                        var_names = f.split("CorrelatedRandomSlopeInterceptEffects(")[
                            1
                        ].split(",")
                        iv_name = var_names[0].strip()
                        group_name = var_names[1].split(")")[0].strip()

                        iv = get_variable(design, iv_name)
                        group = get_variable(design, group_name)
                        random_effects.append(
                            CorrelatedRandomSlopeAndIntercept(iv=iv, groups=group)
                        )

                    elif "UncorrelatedRandomSlopeInterceptEffects(" in f:
                        var_names = f.split("UncorrelatedRandomSlopeInterceptEffects(")[
                            1
                        ].split(",")
                        iv_name = var_names[0].strip()
                        group_name = var_names[1].split(")")[0].strip()

                        iv = get_variable(design, iv_name)
                        group = get_variable(design, group_name)
                        random_effects.append(
                            UncorrelatedRandomSlopeAndIntercept(iv=iv, groups=group)
                        )

            elif key == "family":
                assert isinstance(facts, str)
                family = facts.split("Family")[0]
                dv_name = facts.split("(")[1].split(")")[0].strip()
                assert design.dv.name == dv_name
            elif key == "link":
                assert isinstance(facts, str)
                link = facts.split("Transform")[0]
                dv_name = facts.split("(")[1].split(")")[0].strip()
                assert design.dv.name == dv_name
            else:
                raise NotImplementedError

        sm = StatisticalModel(
            dv=design.dv,
            fixed_ivs=main_effects,
            interactions=interaction_effects,
            random_ivs=random_effects,
            family=family,
            link_func=link,
        )
        return sm

    def model_to_transformation_facts(self, model: z3.ModelRef, design: Design):
        transform_name_to_constraint = {
            "IdentityTransform": IdentityTransform(design.dv.const),
            "LogTransform": LogTransform(design.dv.const),
            "CLogLogTransform": CLogLogTransform(design.dv.const),
            "SquarerootTransform": SquarerootTransform(design.dv.const),
            "InverseTransform": InverseTransform(design.dv.const),
            "InverseSquaredTransform": InverseSquaredTransform(design.dv.const),
            "PowerTransform": PowerTransform(design.dv.const),
            "CauchyTransform": CauchyTransform(design.dv.const),
            "LogLogTransform": LogLogTransform(design.dv.const),
            "ProbitTransform": ProbitTransform(design.dv.const),
            "LogitTransform": LogitTransform(design.dv.const),
            "NegativeBinomialTransform": NegativeBinomialTransform(design.dv.const),
        }
        facts = list()

        for c in model:
            # Is c a function that we care about?
            if c.arity() > 0:
                c_val = is_true(model[c].else_value())
                if c_val:
                    c_name = str(c)
                    if "Transform" in c_name:
                        facts.append(transform_name_to_constraint[c_name])

        return facts

    def generate_and_select_family(
        self, design: Design, statistical_model: StatisticalModel
    ):
        family_facts = self.generate_family_distributions(design=design)
        dv = design.dv

        # End-user: Ask about which family
        selected_family_fact = [
            self.input_interface.ask_family(options=family_facts, dv=design.dv)
        ]

        # Get rules
        rules_dict = self.collect_rules(output="FAMILY", dv_const=dv.const)

        # Solve constraints + rules
        (res_model_family, res_facts_family) = self.solve(
            facts=selected_family_fact, rules=rules_dict
        )

        # Update result StatisticalModel based on user selection
        statistical_model = self.postprocess_to_statistical_model(
            model=res_model_family,
            facts=res_facts_family,
            graph=design.graph,
            statistical_model=statistical_model,
        )

        # Return updated StatisticalModel
        return statistical_model

    # Synthesizer generates viable data transformations to the variables
    # End-user interactively selects which transformations they want
    # These transformations are the link functions
    def generate_and_select_link(
        self, design: Design, statistical_model: StatisticalModel
    ):
        # TODO: Start with no vis
        # TODO: Add in vis

        family_fact = list()
        # Re-create family fact based on statistical model fact
        family = statistical_model.family
        if family == "Gaussian":
            family_fact.append(GaussianFamily(design.dv.const))
        elif family == "InverseGaussian":
            family_fact.append(InverseGaussianFamily(design.dv.const))
        elif family == "Poisson":
            family_fact.append(PoissonFamily(design.dv.const))
        elif family == "Gamma":
            family_fact.append(GammaFamily(design.dv.const))
        elif family == "Tweedie":
            family_fact.append(TweedieFamily(design.dv.const))
        elif family == "Binomial":
            family_fact.append(BinomialFamily(design.dv.const))
        elif family == "NegativeBinomial":
            family_fact.append(NegativeBinomialFamily(design.dv.const))
        elif family == "Multinomial":
            family_fact.append(MultinomialFamily(design.dv.const))

        # Ask for user-input
        transform_data = self.input_interface.ask_inclusion(
            subject="data transformations"
        )

        if transform_data:
            dv = design.dv

            ##### Derive possible valid transforms from knowledge base
            # Get rules
            rules_dict = self.collect_rules(output="TRANSFORMATION", dv_const=dv.const)
            # Get rules for possible link functions
            family_to_transformation_rules = rules_dict[
                "family_to_transformation_rules"
            ]

            # Solve fact + rules to get possible link functions
            (res_model_transformations, res_facts_family) = self.solve(
                facts=family_fact,
                rules={
                    "family_to_transformation_rules": family_to_transformation_rules
                },
            )

            ##### Pick link/data transformation
            # Get link/data transformation rules
            data_transformation_rules = rules_dict["data_transformation_rules"]

            # Get link facts
            transformation_candidate_facts = self.model_to_transformation_facts(
                model=res_model_transformations, design=design
            )

            # Solve facts + rules
            (res_model_link, res_facts_link) = self.solve(
                facts=transformation_candidate_facts,
                rules={"data_transformation_rules": data_transformation_rules},
            )

            # Update result StatisticalModel based on user selection
            statistical_model = self.postprocess_to_statistical_model(
                model=res_model_link,
                facts=res_facts_link,
                graph=design.graph,
                statistical_model=statistical_model,
            )

            # Return statistical model
            return statistical_model

    # Synthesizer generates statistical model properties that depend on data
    # End-user interactively selects properties they want about their statistical model
    def generate_and_select_data_model_properties(
        self, design: Design, statistical_model: StatisticalModel
    ):
        # TODO: Ask end-user if they want to consider transformations before families?
        # Ideally: Would be ideal to let them go back and forth between transformation and family...

        pass

    # Input: Design
    # Output: StatisticalModel
    def synthesize_statistical_model(self, design: Design):
        """
        Step-based, feedback-based (both) synthesis algorithm
        Incrementally builds up an output StatisticalModel object
        """
        ##### Effects set generation
        sm = self.generate_and_select_effects_sets_from_design(design=design)
        assert isinstance(sm, StatisticalModel)

        ##### Data property checking + Model characteristic selection
        ##### Updates the StatisticalModel constructed above
        # Family
        sm = self.generate_and_select_family(design=design, statistical_model=sm)

        # Link function
        sm = self.generate_and_select_link(design=design, statistical_model=sm)

        # TODO: Do we have a revision notion?
        # Diagnostics: Multicollinearity

    # Not yet necessary
    # Synthesizer generates possible variance functions based on the family
    # End-user selects variance function
    def generate_and_select_variance_function(
        self, design: Design, statistical_model: StatisticalModel
    ):
        # If the statistical model has no specified family, pick a family first
        if statistical_model.family is None:
            self.generate_and_select_family(
                design=design, statistical_model=statistical_model
            )

        # We have already specified a family
        # Get the default variance function
        default_variance_func = None  # TODO

        # Ask user if they want to change the default
        self.input_interface.ask_change_default(
            subject="variance function", default=default_variance_func
        )

        variance_facts = list()

        # Get facts from variance function

    # @param graph is a graph of variables and relationships
    # @returns a copy of the graph with additional edges
    # TODO: May consider removing rather than just adding edges, too
    def transform_to_has_edges(self, graph: Graph):
        gr = copy.deepcopy(graph)

        edges = graph.get_edges()

        for (n0, n1, edge_data) in edges:
            edge_type = edge_data["edge_type"]
            edge_obj = edge_data["edge_obj"]

            # Transform all Treatments into Has
            if edge_type == "treat":
                assert isinstance(edge_obj, Treatment)
                treatment = edge_obj.treatment
                identifier = edge_obj.unit
                num_assignments = edge_obj.num_assignments

                # Add has relationship to gr
                gr.has(
                    identifier=identifier,
                    variable=treatment,
                    has_obj=edge_obj,
                    repetitions=num_assignments,
                )

            # Transform all Nest into Has
            elif edge_type == "nest":
                assert isinstance(edge_obj, Nest)
                base = edge_obj.base
                group = edge_obj.group

                # Add has relationship to gr
                gr.has(identifier=base, variable=group, has_obj=edge_obj, repetitions=1)

            # Transfom all Repeat into Has + Associate
            elif edge_type == "repeat":
                assert isinstance(edge_obj, RepeatedMeasure)
                unit = edge_obj.unit
                response = edge_obj.response
                according_to = edge_obj.according_to

                # Add has relationshipt to gr
                gr.has(
                    identifier=unit,
                    variable=according_to,
                    has_obj=edge_obj,
                    repetitions=according_to.get_cardinality(),
                )
                gr.has(
                    identifier=unit,
                    variable=response,
                    has_obj=edge_obj,
                    repetitions=according_to.get_cardinality(),
                )

                # Add implied associate relationship to gr
                gr.associate(according_to, response)

        return gr
