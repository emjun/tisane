# from tisane.statistical_model import StatisticalModel
from tisane.smt.declare_constraints import *
# from tisane.smt.helpers import variables, get_facts_as_list
from tisane.smt.rules import *
from tisane.smt.knowledge_base import KB

from z3 import *
from typing import List, Union, Dict

class QueryManager(object): 
    # QueryManager should be state-less? 
    
    # # TODO: Multiple queries should be handled outside? maybe outcome as a list? 
    # def query(self, input_obj: Union[StatisticalModel], outcome: str): 

    #     # Set up 
    #     # Get and use Z3 consts created for the input_obj
    #     dv_const = input_obj.consts['dv']
    #     main_effects = input_obj.consts['main_effects']
    #     interactions = input_obj.consts['interactions']
    #     self.ground_rules(dv_const=dv_const, main_effects=main_effects, interactions=interactions)

    #     # Collect rules and facts
    #     rules = self.collect_rules(outcome=outcome) # dict
    #     facts = self.collect_facts(input_obj=input_obj, outcome=outcome, z3_consts=z3_consts)
    #     result = self.solve(facts=facts, rules=rules, setting=None)        
        
    #     # TODO: cast the result to a specific object? 

    #     return result
    
    def query(self, outcome: str, facts: List): 
        rules = self.collect_rules(outcome=outcome) # dict
        result = self.solve(facts=facts, rules=rules, setting=None)        

        return result
    
    # @param outcome describes what the query result should be, can be a list of items, 
    # including: statistical model, variable relationship graph, data schema, data collection procedure
    # @return logical rules to consider during solving process
    def collect_rules(self, outcome=str) -> Dict: 
        # Get and manage the constraints that need to be considered from the rest of Knowledge Base     
        rules_to_consider = dict()

        # TODO: Clean up further so only create Z3 rules/functions for the rules that are added?
        if outcome.upper() == 'STATISTICAL MODEL': 
            raise NotImplementedError

        elif outcome.upper() == 'VARIABLE RELATIONSHIP GRAPH': 
            rules_to_consider['graph_rules'] = KB.graph_rules

        elif outcome.upper() == 'DATA SCHEMA': 
            rules_to_consider['data_type_rules'] = KB.data_type_rules
            rules_to_consider['data_transformation_rules'] = KB.data_transformation_rules
            rules_to_consider['variance_functions_rules'] = KB.variance_functions_rules

        elif outcome.upper()  == 'DATA COLLECTION PROCEDURE': 
            raise NotImplementedError
        
        else: 
            raise ValueError(f"Query is not supported: {outcome}. Try the following: 'STATISTICAL MODEL', 'VARIABLE RELATIONSHIP GRAPH', 'DATA SCHEMA', 'DATA COLLECTION PROCEDURE'")
        
        return rules_to_consider

    # @param setting is 'interactive' 'default' (which is interactive), etc.?
    def solve(self, facts: List, rules: dict, setting=None): 
        s = Solver() # Z3 solver

        for batch_name, rules in rules.items(): 
            print(f'Adding {batch_name} rules.')
            # Add rules
            s.add(rules)
            # import pdb; pdb.set_trace()

            # Add facts (implied/asserted by user)
            # all_facts = get_facts_as_list(facts)
            
            self.check_update_constraints(solver=s, assertions=facts)
        
        
        import pdb; pdb.set_trace()
        mdl =  s.model()
        
        print(s.model()) # assumes s.check() is SAT
        return mdl 

    # @param pushed_constraints are constraints that were added as constraints all at once but then caused a conflict
    # @param unsat_core is the set of cosntraints that caused a conflict
    # @param keep_clause is the clause in unsat_core to keep and that resolves the conflict
    def update_clauses(self, pushed_constraints: list, unsat_core: list, keep_clause: list): 
        # Verify that keep_clause is indeed a subset of unsat_core
        for c in keep_clause:
            assert(c in unsat_core)
        
        updated_constraints = list()
        for pc in pushed_constraints: 
            # Should we remove this constraint?
            if (pc in unsat_core) and (pc not in keep_clause): 
                pass
            else: 
                updated_constraints.append(pc)

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
            elif idx in range(len(unsat_core)): 
                # only keep the constraint that is selected. 
                keep.append(unsat_core[idx])
                print(f"Ok, going to add {unsat_core[idx]} and remove the others.")
                break
            else:
                raise ValueError

        # return current_constraints + keep
        return keep

    def check_update_constraints(self, solver: Solver, assertions: list): 
        # updated_assertions = None
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
        elif (state == sat): 
            pass
        else: 
            raise ValueError(f"State of solver after adding user input conceptual graph constraints is {state}")

        # Double check that the new_assertions do not cause UNSAT
        new_state = solver.check(assertions)
        # import pdb; pdb.set_trace()
        if new_state == sat: 
            # return (solver, assertions)
            return solver
        elif new_state == unsat: 
            # import pdb; pdb.set_trace()
            return self.check_update_constraints(solver=solver, assertions=assertions)
        else: 
            raise ValueError (f"Solver state is neither SAT nor UNSAT: {new_state}")

class Query(object): 
    rules : list # rules to consider
    facts : list # facts to consider while solving rules + facts
    
    def __init__(self, rules=list, facts=list): 
        self.rules = rules 
        self.facts = facts
    
    def solve(self): 
        pass

# Goal: just get the example working with last week working with current API/system
# 1. Query Manager (only the implementation that is absolutely necessary)
# 2. Variable Relationship Graph (should be clear if cause or correlate) [M]
# 3. Data Schema (should output clearly a data schema) [M]
# 4. Data collect procedure [T]

# Global QueryManager
QM = QueryManager()