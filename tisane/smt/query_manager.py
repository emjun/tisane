from tisane.statistical_model import StatisticalModel
from tisane.design import Design 
from tisane.graph import Graph 

from tisane.smt.declare_constraints import *
import tisane.smt.rules as rules
from tisane.smt.knowledge_base import KB
from tisane.smt.qm_helpers import *

from z3 import *
from typing import List, Union, Dict



class QueryManager(object): 
    # QueryManager should be state-less? 

    def prep_query(self, input_obj: Union[Design, StatisticalModel], output_obj: Union[Graph, StatisticalModel]):
        effects_facts = list()

        # Used to ground rules to simplify quantification during constraint solving
        dv_const = input_obj.dv.const

        # If the @param output_obj is a StatisticalModel, do a prep phase to
        # narrow down an Effects Set to consider for the rest of the constraint
        # solving process
        if isinstance(input_obj, Design): 
            if isinstance(output_obj, StatisticalModel): 
                effects_facts = input_obj.collect_ambiguous_effects_facts(main_effects=True, interactions=True)
                
            # elif isinstance(output_obj, Graph): 
            #     effects_facts = input_obj.collect_ambiguous_effects_facts(main_effects=False, interactions=False)
                
            KB.ground_effects_rules(dv_const=dv_const)
            effects_rules = self.collect_rules(output_obj=output_obj, step='effects')
            (model, updated_effects_facts) = self.solve(facts=effects_facts, rules=effects_rules, setting=None)
            
            # Postprocess: Use these updated_effects_facts to update main
            # and interaction effect sequences Postprocess
            for f in updated_effects_facts: 
                fact_dict = parse_fact(f)
                # Generate consts for grounding KB
                input_obj.generate_const_from_fact(fact_dict=fact_dict)
            
            return updated_effects_facts
    
    def query(self, input_obj: Union[Design, StatisticalModel], output_obj: Union[Graph, StatisticalModel]):
        
        updated_effects_facts = self.prep_query(input_obj=input_obj, output_obj=output_obj)
        
        # Collect facts after prepping for query
        facts = updated_effects_facts + self.collect_facts(input_obj=input_obj, output_obj=output_obj)
        
        # Ground rules to simplify quantification during constraint solving
        input_obj.generate_consts()
        dv_const = input_obj.dv.const
        main_effects = input_obj.consts['main_effects']
        interactions = input_obj.consts['interactions']
        mixed_effects = None # mixed effects
        KB.ground_rules(dv_const=dv_const, main_effects=main_effects, interactions=interactions)
        
        # After grounding KB, collect rules to guide synthesis
        rules = self.collect_rules(output_obj=output_obj) # dict
        # Incrementally and interactively solve the facts and rules as constraints
        # TODO: Pass and initialize with model (used for effects facts to solver?)
        (model, updated_facts) = self.solve(facts=facts, rules=rules, setting=None)
        result = self.postprocess_query_results(model=model, updated_facts=updated_facts, input_obj=input_obj, output_obj=output_obj)

        return result

    def collect_facts(self, input_obj: Union[Design, StatisticalModel], output_obj: Union[Graph, StatisticalModel]): 
        # Compile @param input_obj to logical facts
        facts = input_obj.compile_to_facts() # D -> SM: Data types, Nested
        
        # TODO: Not sure this is necessary to do
        # # Prune out logical facts that would be trivially true
        # if isinstance(output_obj, StatisticalModel):
        #     rules_to_consider['data_type_rules'] = KB.data_type_rules
        #     rules_to_consider['data_transformation_rules'] = KB.data_transformation_rules
        #     rules_to_consider['variance_functions_rules'] = KB.variance_functions_rules
        # elif isinstance(output_obj, Graph):
        #     rules_to_consider['graph_rules'] = KB.graph_rules

        # elif isinstance(output_obj, Design): 
        #     # import pdb; pdb.set_trace()
        #     # TODO: Should allow separate queries for data schema and data collection?? probably not?
        #     rules_to_consider['data_type_rules'] = KB.data_type_rules
        #     rules_to_consider['data_transformation_rules'] = KB.data_transformation_rules
        #     rules_to_consider['variance_functions_rules'] = KB.variance_functions_rules

        # else: 
        #     raise ValueError(f"Query output is not supported: {type(output_obj)}.")
        output = None
        if isinstance(output_obj, Graph): 
            output = 'VARIABLE RELATIONSHIP GRAPH'
        elif isinstance(output_obj, StatisticalModel): 
            output = 'STATISTICAL MODEL'
        
        assert(output is not None)
        ambig_facts = input_obj.collect_ambiguous_facts(output=output) # D -> SM: Transformations, Link, Var
        facts += ambig_facts # Combine all facts

        return facts

    
    # @param outcome describes what the query result should be, can be a list of items, 
    # including: statistical model, variable relationship graph, data schema, data collection procedure
    # @return logical rules to consider during solving process
    def collect_rules(self, output_obj: Union[StatisticalModel, Graph, Design], **kwargs) -> Dict: 
        # Get and manage the constraints that need to be considered from the rest of Knowledge Base     
        rules_to_consider = dict()

        if 'step' in kwargs: 
            if kwargs['step'] == 'effects':     
                rules_to_consider['effects_rules'] = KB.effects_rules
        else: 
            # TODO: Clean up further so only create Z3 rules/functions for the rules that are added?
            if isinstance(output_obj, StatisticalModel):
                    rules_to_consider['data_type_rules'] = KB.data_type_rules
                    rules_to_consider['data_transformation_rules'] = KB.data_transformation_rules
                    rules_to_consider['variance_functions_rules'] = KB.variance_functions_rules
            elif isinstance(output_obj, Graph):
                rules_to_consider['graph_rules'] = KB.graph_rules

            elif isinstance(output_obj, Design): 
                # import pdb; pdb.set_trace()
                # TODO: Should allow separate queries for data schema and data collection?? probably not?
                rules_to_consider['data_type_rules'] = KB.data_type_rules
                rules_to_consider['data_transformation_rules'] = KB.data_transformation_rules
                rules_to_consider['variance_functions_rules'] = KB.variance_functions_rules

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
    def update_clauses(self, pushed_constraints: list, unsat_core: list, keep_clause: list): 
        # Verify that keep_clause is indeed a subset of unsat_core
        for c in keep_clause:
            assert(c in unsat_core)

        updated_constraints = list()
        for k in keep_clause: 
            # Add the keep clause
            updated_constraints.append(k)

            # If this keep clause is about Not Transforming data
            if 'NoTransform' in str(k):
                fact_dict = parse_fact(k)
                assert('variable_name' in fact_dict)
                var_name = fact_dict['variable_name']

                for pc in pushed_constraints: 
                    # If pc is not k (already added to updated_constraints)
                    if str(pc) != str(k): 
                        # Is the pushed consctraint about the same variable as the keep clause (NoTransform)?
                        if var_name in str(pc): 
                            # Keep the pushed constraint as long as it is not about
                            # transforming the variable
                            if 'Transform' not in str(pc):
                                updated_constraints.append(pc)
                        else: 
                            updated_constraints.append(pc)
            
            # If this keep clause is about anything else other than Not Transforming data
            else: 
                for pc in pushed_constraints: 
                    # If pc is not k (already added to updated_constraints)
                    if str(pc) != str(k):
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
            
            assert(len(unsat_core) > 0)


            # solver.push() # save state before add @param assertions

            # Ask user for input
            keep_constraint = self.elicit_user_input(solver.assertions(), unsat_core)
            
            # Modifies @param assertions
            updated_assertions = self.update_clauses(assertions, unsat_core, keep_constraint)
            assertions = updated_assertions
            # import pdb; pdb.set_trace()
        elif (state == sat): 
            pass
        else: 
            raise ValueError(f"State of solver after adding user input conceptual graph constraints is {state}")

        # Double check that the new_assertions do not cause UNSAT
        new_state = solver.check(assertions)
        
        if new_state == sat: 
            return (solver, assertions) # return the solver and the updated assertions
            # import pdb; pdb.set_trace()
            # return assertions
        elif new_state == unsat: 
            
            return self.check_update_constraints(solver=solver, assertions=assertions)
        else: 
            raise ValueError (f"Solver state is neither SAT nor UNSAT: {new_state}")

    # UPDATE: After trying to implement this: Realize easier to iterate through updated
    # facts and check that model is true rather than other way around. Have to
    # check which function instance is true anyway, which is what we have in the
    # updated facts. 
    def cast_from_model(self, input_obj: Union[Design], output_obj: Union[Graph], outcome: str, model: z3.ModelRef): 
        consts = dict()
        functions = list()

        # Iterate through the declarations in the model
        for d in model.decls(): 

            if isinstance(input_obj, Design): 
                input_vars = [v.name for v in input_obj.get_variables()]

                if d.name() in input_vars: 
                    consts[model.get_interp(d)] = d
                    # consts.append(d)
                # Is the it the name of a Function included in rules.py? 
                elif d.name() in dir(rules):  
                    functions.append(d)
                else: 
                    raise ValueError(f"Do not recognize this: {d.name()}")
        
        for f in functions: 
            if f.name() == 'Cause': 
                f_interp = model[f] # Get interpretation of f in this model
                num_entries = f_interp.num_entries()
                for i in range(num_entries):
                    (start, end, to_include) = f_interp.entry(i)
                    import pdb; pdb.set_trace()
            elif f.name() == 'Correlate': 
                pass
            elif f.name() == 'Interaction':
                pass
            else: 
                pass
    

    # TODO: START HERE: Probably some hybrid of above and below...
    # I need function name (to give me edge type), variable objects (to update edges to Graph: remove and replace)
    def postprocess_query_results(self, model: z3.ModelRef, updated_facts: List, input_obj: Union[Design], output_obj: Union[Graph]):
        
        # Delegate to helpers
        if isinstance(input_obj, Design) and isinstance(output_obj, Graph): 
            return design_to_statistical_model(model=model, updated_facts=updated_facts, input_obj=input_obj, output_obj=output_obj)
        
        elif isinstance(input_obj, Design) and isinstance(output_obj, StatisticalModel): 
            return design_to_statistical_model(model=model, updated_facts=updated_facts, input_obj=input_obj, output_obj=output_obj)
        
# Global QueryManager
QM = QueryManager()