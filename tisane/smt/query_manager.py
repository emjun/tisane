from tisane.statistical_model import StatisticalModel
from tisane.smt.declare_constraints import *
from tisane.smt.helpers import *

from typing import Dict, Any, Union

class QueryManager(object): 
    # QueryManager should be state-less
    
    # TODO: Multiple queries should be handled outside? maybe outcome as a list? 
    def query(self, input_obj=Union[StatisticalModel], outcome=str): 
        # TODO: Check that input and outcome match? 

        rules = self.accumulate(outcome=outcome) 

        facts = input_obj.to_logical_facts() # dict
        result = self.solve(facts=facts, rules=rules, setting=None)        
        return result
    
    # @param outcome describes what the query result should be, can be a list of items, 
    # including: statistical model, variable relationship graph, data schema, data collection procedure
    # @return logical rules to consider during solving process
    def accumulate(self, outcome=str) -> Dict: 
        # Get and manage the constraints that need to be considered from the rest of Knowledge Base     
        rules_to_consider = dict()

        # TODO: Clean up further so only create Z3 rules/functions for the rules that are added?
        if outcome.upper() == 'STATISTICAL MODEL': 
            raise NotImplementedError
        elif outcome.upper() == 'VARIABLE RELATIONSHIP GRAPH': 
            rules_to_consider['model_explanation_rules'] = model_explanation_rules
            rules_to_consider['conceptual_graph_rules'] = conceptual_graph_rules
            rules_to_consider['link_functions_rules'] = link_functions_rules
            rules_to_consider['variance_functions_rules'] = variance_functions_rules
        elif outcome.upper() == 'DATA SCHEMA': 
            rules_to_consider['model_explanation_rules'] = model_explanation_rules
            rules_to_consider['data_schema_rules'] = data_schema_rules
        elif  outcome.upper()  == 'DATA COLLECTION PROCEDURE': 
            raise NotImplementedError
        else: 
            raise ValueError(f"Query is not supported: {outcome}. Try the following: 'STATISTICAL MODEL', 'VARIABLE RELATIONSHIP GRAPH', 'DATA SCHEMA', 'DATA COLLECTION PROCEDURE'")
        
        return rules_to_consider

    # @param setting is 'interactive' 'default' (which is interactive), etc.?
    def solve(self, facts: dict, rules: dict, setting=None): 
        s = Solver() # Z3 solver

        for batch_name, rules in rules.items(): 
            print(f'Adding {batch_name} rules.')
            # Add rules
            s.add(And(rules))

            # Add facts (implied/asserted by user)
            all_facts = get_facts_as_list(facts)
            self.verify_update_constraints(solver=s, assertions=all_facts)
            s.push()
        
        mdl =  s.model()
        # import pdb; pdb.set_trace()
        print(s.model()) # assumes s.check() is SAT
        return mdl # TODO: Change this!

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

    def verify_update_constraints(self, solver: Solver, assertions: list): 
        state = solver.check(assertions)
        if (state == unsat): 
            unsat_core = solver.unsat_core() 
            import pdb; pdb.set_trace()
            assert(len(unsat_core) > 0)

            solver.push() # save state before add @param assertions

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
        solver.add(assertions)
        assert(solver.check() == sat)


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