from tisane.variable import AbstractVariable
from tisane.statistical_model import StatisticalModel
from tisane.design import Design 
from tisane.graph import Graph 

from tisane.smt.declare_constraints import *
from tisane.smt.rules import *
from tisane.smt.knowledge_base import KB
from tisane.smt.qm_helpers import *
from tisane.smt.input_interface import InputInterface

from z3 import *
from typing import List, Union, Dict, Tuple


"""
Class for managing queries to KnowledgeBase and processing results of solving constraints
"""
class QueryManager(object): 

    def _collect_ambiguous_effects_facts(self, dv: AbstractVariable, graph: Graph, main_effects: bool, interactions: bool): 
        facts = list() 
        edges = graph.get_edges()

        # Declare data type
        Object = DeclareSort('Object')

        # Do we care about Main Effects? 
        if main_effects: 
            # What Main Effects should we consider? 
            for (n0, n1, edge_data) in edges: 
                edge_type = edge_data['edge_type']
                n0_var = graph.get_variable(n0)
                n1_var = graph.get_variable(n1)
                if edge_type == 'unknown': 
                    facts.append(MainEffect(n0_var.const, n1_var.const))
                    facts.append(NoMainEffect(n0_var.const, n1_var.const))

        if interactions: 
            # What Interaction Effects should we consider?
            # Check if the edge does not include the DV
            incoming_edges = list(graph._graph.in_edges(dv.name, data=True))
            
            interactions_considered = list()
            for (ie, dv, data) in incoming_edges: 
                ie_var = graph.get_variable(ie)
                for (other, dv, data) in incoming_edges: 
                    # Asks about interactions even if end-user does not want to
                    # include the corresponding main effects
                    other_var = graph.get_variable(other)
                    if (ie is not other) and ({ie, other} not in interactions_considered):             
                        # TODO: Add all combinatorial interactions, should we ask end-user for some interesting ones? 
                        i_set = EmptySet(Object)
                        i_set = SetAdd(i_set, ie_var.const)
                        i_set = SetAdd(i_set, other_var.const)

                        facts.append(Interaction(i_set))
                        facts.append(NoInteraction(i_set))

                        interactions_considered.append({ie, other})

        return facts

    def _postprocess_effects_facts(self, dv: AbstractVariable, graph: Graph, effects_facts: list): 
        # Postprocess result of KB query and generate Z3 consts
        main_seq = None
        interaction_seq = None
        model_variables = set() # Variables that are included in a Statistical Model

        for f in effects_facts: 
            fact_dict = parse_fact(f)
            start_name = fact_dict['start']
            end_name = fact_dict['end']
            start_var = graph.get_variable(start_name)
            end_var = graph.get_variable(end_name)

            if fact_dict['function'] == 'MainEffect': 
                assert(end_var is dv)
                if main_seq is None: 
                    main_seq = Unit(start_var.const)
                else: 
                    main_seq = Concat(Unit(start_var.const), main_seq)
                model_variables.add(start_var)
            elif fact_dict['function'] == 'Interaction': 
                # Create set for interaction
                interaction = EmptySet(Object)
                SetAdd(interaction, start_var.const)
                SetAdd(interaction, end_var.const)
                if interaction_seq is None: 
                    interaction_seq = Unit(interaction)
                else: 
                    interaction_seq = Concat(Unit(interaction), interaction_seq)
                model_variables.append(start_var)
                model_variables.append(end_var)
        
        # Before returning 
        if main_seq is None: 
            main_seq = Empty(SeqSort(Object))
        if interaction_seq is None: 
            interaction_seq = Unit(EmptySet(Object))

        # return {'main_effects': main_seq, 'interactions': interaction_seq}
        return (main_seq, interaction_seq, model_variables)
    
    def _prep_synthesize_statistical_model(self, dv: AbstractVariable, graph: Graph): 
        # Collect ambiguous effects facts for end-user interaction
        dv_const = dv.const
        effects_facts = self._collect_ambiguous_effects_facts(dv=dv, graph=graph, main_effects=True, interactions=True)
        # Collect rules for effects facts
        KB.ground_effects_rules(dv_const=dv_const)
        effects_rules = self.collect_rules(output='STATISTICAL MODEL', step='effects')
        # Query Knowledge Base and solve for valid effects_facts
        (model, updated_effects_facts) = self.solve(facts=effects_facts, rules=effects_rules, setting=None)

        return updated_effects_facts

    def synthesize_statistical_model(self, dv: AbstractVariable, graph: Graph): 
        # Prep query
        effects_facts = self._prep_synthesize_statistical_model(dv=dv, graph=graph)
        (main_effects, interactions, model_variables) = self._postprocess_effects_facts(dv=dv, graph=graph, effects_facts=effects_facts)
        
        # Query + Interaction 
        (model, updated_facts) = self.query(dv=dv, graph=graph, main_effects=main_effects, interactions=interactions, model_variables=model_variables)

        # Process output
        sm = postprocess_to_statistical_model(dv=dv, graph=graph, model=model, updated_facts=updated_facts)
        
        return sm


    def query(self, dv: AbstractVariable, graph: Graph, main_effects: SeqSort, interactions: SeqSort, **kwargs) -> Any: 
            
            KB.ground_rules(dv_const=dv.const, main_effects=main_effects, interactions=interactions)
            
            # Collect facts
            if 'model_variables' in kwargs: 
                facts = self.collect_facts(dv=dv, graph=graph, output='STATISTICAL MODEL', model_variables=kwargs['model_variables'])
            else: 
                facts = self.collect_facts(dv=dv, graph=graph, output='STATISTICAL MODEL')

            # After grounding KB, collect rules to guide synthesis
            rules = self.collect_rules(output='STATISTICAL MODEL') # dict
            # Incrementally and interactively solve the facts and rules as constraints
            return self.solve(facts=facts, rules=rules, setting=None)


    # TODO: When move to Graph IR: It seems to me that all the prep methods could be in the QueryManager itself!
    # TODO: Could also move collect_ambiguous facts to QueryManager (helpers)???
    def prep_query(self, input_obj: Union[Design, StatisticalModel, Graph], output_obj: Union[Graph, StatisticalModel, Design]):
        effects_facts = list()

        # If the @param output_obj is a StatisticalModel, do a prep phase to
        # narrow down an Effects Set to consider for the rest of the constraint
        # solving process
        if isinstance(input_obj, Design): 
            # Used to ground rules to simplify quantification during constraint solving
            dv_const = input_obj.dv.const

            if isinstance(output_obj, StatisticalModel): 
                effects_facts = input_obj.collect_ambiguous_effects_facts(main_effects=True, interactions=True)
                
            KB.ground_effects_rules(dv_const=dv_const)
            effects_rules = self.collect_rules(output_obj=output_obj, step='effects')
            (model, updated_effects_facts) = self.solve(facts=effects_facts, rules=effects_rules, setting=None)
            
            # Postprocess: Use these updated_effects_facts to update main
            # and interaction effect sequences
            for f in updated_effects_facts: 
                fact_dict = parse_fact(f)
                # Generate consts for grounding KB
                input_obj.generate_const_from_fact(fact_dict=fact_dict)
            
            return updated_effects_facts
        
        if isinstance(input_obj, StatisticalModel): 
            # Used to ground rules to simplify quantification during constraint solving
            dv_const = input_obj.dv.const
            
            if isinstance(output_obj, Design): 
                # Ask for treatment before structure because seems more
                # intuitive this way. 
                # Also, by asking for treatment, get some structure information.
                input_obj.elicit_treatment_facts(gr=input_obj.graph, dv=input_obj.dv, variables=get_variables(), input_obj=input_obj)
                # input_obj.elicit_structure_facts()

                # ds_facts = input_obj.collect_ambiguous_data_structure_facts()
                # treatment_facts = input_obj.collect_ambiguous_treatment_facts()

                # import pdb; pdb.set_trace()
        
        if isinstance(input_obj, Graph): 
            if isinstance(output_obj, Design): 
                # Ask end-user about which DV to use
                dv = elicit_dv(gr=input_obj)
                output_obj.set_dv(dv=dv)
                variables = input_obj.get_variables()
                # Elicit treatment facts
                elicit_treatment_facts(gr=input_obj, dv=dv, variables=variables)
                # Elicit data/structure facts
                elicit_structure_facts(gr=input_obj, dv=dv, variables=variables)

        return effects_facts
    

    def query_old(self, input_obj: Union[Design, StatisticalModel, Graph], output_obj: Union[Graph, StatisticalModel, Design]):
        
        updated_effects_facts = self.prep_query(input_obj=input_obj, output_obj=output_obj)
        
        # Collect facts after prepping for query
        facts = updated_effects_facts + self.collect_facts(input_obj=input_obj, output_obj=output_obj)
        
        # Ground rules to simplify quantification during constraint solving
        input_obj.generate_consts()
        dv_const = input_obj.dv.const
        main_effects = input_obj.consts['main_effects']
        interactions = input_obj.consts['interactions']
        mixed_effects = None # mixed effects
        # import pdb; pdb.set_trace()
        KB.ground_rules(dv_const=dv_const, main_effects=main_effects, interactions=interactions)
        
        # After grounding KB, collect rules to guide synthesis
        rules = self.collect_rules(output_obj=output_obj) # dict
        # Incrementally and interactively solve the facts and rules as constraints
        # TODO: Pass and initialize with model (used for effects facts to solver?)
        (model, updated_facts) = self.solve(facts=facts, rules=rules, setting=None)
        result = self.postprocess_query_results(model=model, updated_facts=updated_facts, input_obj=input_obj, output_obj=output_obj)

        return result

    def _compile_graph_to_facts(self, graph: Graph): 
        facts = list()  # should be dict?

        nodes = graph.get_nodes()
        # Data type facts
        for (n, data) in nodes: 
            n_var = data['variable']
            if isinstance(n_var, Nominal): 
                facts.append(NominalDataType(n_var.const))
            elif isinstance(n_var, Ordinal): 
                facts.append(OrdinalDataType(n_var.const))
            else: 
                assert (isinstance(n_var, Numeric)) 
                facts.append(NumericDataType(n_var.const))
        
        return facts
    
    def _collect_ambiguous_facts_for_statistical_model(self, graph: Graph, **kwargs): 
        facts = list() 

        model_variables = kwargs['model_variables'] # Variables that are involved in the Statistical Model 

        nodes = graph.get_nodes()

        import pdb; pdb.set_trace()
        for var in model_variables: 
            # Data Transformations
            # Induce UNSAT 
            facts.append(Transformation(var.const))
            facts.append(NoTransformation(var.const))
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

        return facts

    def collect_facts(self, dv: AbstractVariable, graph: Graph, output: str, **kwargs): 
    
        facts = self._compile_graph_to_facts(graph=graph)
        if output == 'STATISTICAL MODEL': 
            if 'model_variables' in kwargs:
                model_variables = kwargs['model_variables'] 
                ambig_facts = self._collect_ambiguous_facts_for_statistical_model(graph=graph, model_variables=model_variables) 
            else: 
                ambig_facts = self._collect_ambiguous_facts_for_statistical_model(graph=graph)
            facts += ambig_facts # Combine all facts

        return facts
    
    # @param outcome describes what the query result should be, can be a list of items, 
    # including: statistical model, variable relationship graph, data schema, data collection procedure
    # @return logical rules to consider during solving process
    def collect_rules(self, output: str, **kwargs) -> Dict: 
        # Get and manage the constraints that need to be considered from the rest of Knowledge Base     
        rules_to_consider = dict()

        if output.upper() == 'EFFECTS':
            assert('dv_const' in kwargs)
            KB.ground_effects_rules(dv_const=kwargs['dv_const'])
            rules_to_consider['effects_rules'] = KB.effects_rules
        else: 
            # TODO: Clean up further so only create Z3 rules/functions for the rules that are added?
            if output.upper() == 'STATISTICAL MODEL': 
                    rules_to_consider['data_type_rules'] = KB.data_type_rules
                    rules_to_consider['data_transformation_rules'] = KB.data_transformation_rules
                    rules_to_consider['variance_functions_rules'] = KB.variance_functions_rules
            elif output.upper() == 'CONCEPTUAL MODEL': 
                rules_to_consider['graph_rules'] = KB.graph_rules
            # elif output.upper() == 'STUDY DESIGN': 
            #     # import pdb; pdb.set_trace()
            #     # TODO: Should allow separate queries for data schema and data collection?? probably not?
            #     rules_to_consider['data_type_rules'] = KB.data_type_rules
            #     rules_to_consider['data_transformation_rules'] = KB.data_transformation_rules
            #     rules_to_consider['variance_functions_rules'] = KB.variance_functions_rules

            else: 
                raise ValueError(f"Query output is not supported: {type(output_obj)}.")
            
        return rules_to_consider

    # @param setting is 'interactive' 'default' (which is interactive), etc.?
    def solve(self, facts: List, rules: dict, setting=None): 
        s = Solver() # Z3 solver

        for batch_name, rules in rules.items(): 
            print(f'Adding {batch_name} rules.')
            # Add rules
            s.add(rules)

            (model, updated_facts) = self.check_update_constraints(solver=s, assertions=facts)
            # import pdb; pdb.set_trace()
            facts = updated_facts        
        
        mdl =  s.model()
        return (mdl, updated_facts)

    # @param pushed_constraints are constraints that were added as constraints all at once but then caused a conflict
    # @param unsat_core is the set of cosntraints that caused a conflict
    # @param keep_clause is the clause in unsat_core to keep and that resolves the conflict
    def update_clauses(self, pushed_constraints: list, unsat_core: list, keep_clause): 
        # Verify that keep_clause is indeed a subset of unsat_core
        assert(keep_clause in unsat_core)

        updated_constraints = list()
        # Add the keep clause
        updated_constraints.append(keep_clause)

        # If this keep clause is about Not Transforming data
        # TODO: Probably revise this
        if 'NoTransform' in str(keep_clause):
            fact_dict = parse_fact(keep_clause)
            assert('variable_name' in fact_dict)
            var_name = fact_dict['variable_name']

            for pc in pushed_constraints: 
                # If pc is not keep_clause (already added to updated_constraints)
                if str(pc) != str(keep_clause): 
                    # Is the pushed consctr, aint about the same variable as the keep clause (NoTransform)?
                    if var_name in str(pc): 
                        # Keep the pushed constraint as long as it is not about
                        # transforming the variable
                        if 'Transform' not in str(pc):
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
        
    # @param current_constraints are constraints that are currently SAT before adding @param unsat_core
    # @param unsat_core, which are the conflicting clauses
    # @returns a set of new clauses with the unsat core resolved with user input
    def elicit_user_input(self, current_constraints: list, unsat_core: list): 
        keep = list()
        while True: 
            # TODO: Allow for something totally new or different?
            idx = int(input(f'These cannot be true at the same time. Which is true? If neither, enter -1. {unsat_core}:'))
            if idx == -1: 
                pass
                # TODO: Remove both?
            elif idx in range(len(unsat_core)): 
                # only keep the constraint that is selected. 
                constraint = unsat_core[idx] 
                keep.append(constraint)
                print(f"Ok, going to add {constraint} and remove the others.")
                break
            else:
                raise ValueError

        return keep

    def check_update_constraints(self, solver: Solver, assertions: list) -> List: 
        state = solver.check(assertions)
        if (state == unsat): 
            unsat_core = solver.unsat_core() 
            
            # import pdb; pdb.set_trace()
            assert(len(unsat_core) > 0)

            # Ask user for input
            keep_constraint = InputInterface.resolve_unsat(facts=solver.assertions(), unsat_core=unsat_core)
            # keep_constraint = self.elicit_user_input(solver.assertions(), unsat_core)
            
            # Modifies @param assertions
            updated_assertions = self.update_clauses(assertions, unsat_core, keep_constraint)
            assertions = updated_assertions

            new_state = solver.check(assertions)

            if new_state == sat: 
                return (solver, assertions)
            elif new_state == unsat: 
                return self.check_update_constraints(solver=solver, assertions=assertions)
            else: 
                raise ValueError (f"After eliciting end-user input, solver state is neither SAT nor UNSAT: {new_state}")    
        elif (state == sat): 
            return (solver, assertions)
        else:
            raise ValueError(f"Initial solver state into check_update_constraints is {state}")
            
    # Postprocess results of finding a valid z3 @param model and @param updated_facts
    # @return results cast in output_obj
    def postprocess_query_results(self, model: z3.ModelRef, updated_facts: List, input_obj: Union[Design], output_obj: Union[Graph]):
        
        # Delegate to helpers
        if isinstance(input_obj, Design) and isinstance(output_obj, Graph): 
            return design_to_graph(model=model, updated_facts=updated_facts, input_obj=input_obj, output_obj=output_obj)
        
        elif isinstance(input_obj, Design) and isinstance(output_obj, StatisticalModel): 
            return design_to_statistical_model(model=model, updated_facts=updated_facts, input_obj=input_obj, output_obj=output_obj)

        elif isinstance(input_obj, StatisticalModel) and isinstance(output_obj, Graph): 
            return statistical_model_to_graph(model=model, updated_facts=updated_facts, input_obj=input_obj, output_obj=output_obj)
        else: 
            raise NotImplementedError

    def postprocess_to_statistical_model(self, model: z3.ModelRef, facts: List, graph: Graph, statistical_model: StatisticalModel) -> StatisticalModel: 
        fixed_ivs = list()
        interaction_ivs = list()
        random_slopes = list() 
        random_intercepts = list()
        
        for f in facts: 
            fact_dict = parse_fact(f)
            function = fact_dict['function']
            
            # Is this fact about Fixed effects?
            if function == 'FixedEffect': 
                # Get variable names
                iv_name = fact_dict['start']
                dv_name = fact_dict['end']
                # Get variables 
                iv_var = graph.get_variable(iv_name)
                dv_var = graph.get_variable(dv_name)

                fixed_ivs.append(iv_var)

            elif function == 'Interaction': 
                # Get variable names
                var_names = fact_dict['variables']
                # Get variables 
                variables = list()

                for v in var_names: 
                    var = graph.get_variable(v)
                    variables.append(var)

                interaction_ivs.append(tuple(variables))
                
            # elif ('Transform' in function) and (function != 'Transformation'): 
            #     assert('variable_name' in fact_dict)
            #     var_name = fact_dict['variable_name']

            #     # Apply transformation to variable, everywhere it exists in output_obj (StatisticalModel)
            #     var = graph.get_variable(var_name)
            #     var.transform(transformation=function)
                
        
        if len(fixed_ivs) > 0:
            statistical_model.set_fixed_ivs(fixed_ivs)
        if len(interaction_ivs) > 0: 
            statistical_model.set_interactions(interaction_ivs)    
        # output_obj.set_mixed_effects(mixed_effects)

        return statistical_model

        
# Global QueryManager
QM = QueryManager()