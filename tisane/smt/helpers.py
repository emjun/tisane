from z3 import *

variables = list () 

def get_facts_as_list(facts: dict): 
    global variables 

    all_facts = list()
    for k, v in facts.items(): 
        if k != 'variables': 
            all_facts += v
        else: 
            variables += v
    
    return all_facts

# @param pushed_constraints are constraints that were added as constraints all at once but then caused a conflict
# @param unsat_core is the set of cosntraints that caused a conflict
# @param keep_clause is the clause in unsat_core to keep and that resolves the conflict
def update_clauses(pushed_constraints: list, unsat_core: list, keep_clause: list): 
        # Verify that keep_clause is indeed a subset of unsat_core
        for c in keep_clause:
            assert(c in unsat_core)
        
        updated_constraints = list()
        for pc in pushed_constraints: 
            # Should we remove this constraint?
            if (pc in unsat_core) and (pc not in keep_clause): 
                # Add the negation to help solver down the line 
                updated_constraints.append(Not(pc))
                # pass
            else: 
                updated_constraints.append(pc)
        # import pdb; pdb.set_trace()
        return updated_constraints
        
    # @param current_constraints are constraints that are currently SAT before adding @param unsat_core
    # @param unsat_core, which are the conflicting clauses
    # @returns a set of new clauses with the unsat core resolved with user input
def elicit_user_input(current_constraints: list, unsat_core: list): 
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

def check_update_constraints(solver: Solver, assertions: list): 
        # updated_assertions = None
        state = solver.check(assertions)
        if (state == unsat): 
            unsat_core = solver.unsat_core() 
            import pdb; pdb.set_trace()
            assert(len(unsat_core) > 0)


            # solver.push() # save state before add @param assertions

            # Ask user for input
            keep_constraint = elicit_user_input(solver.assertions(), unsat_core)
            import pdb;pdb.set_trace()
            # Modifies @param assertions
            updated_assertions = update_clauses(assertions, unsat_core, keep_constraint)
            assertions = updated_assertions
        elif (state == sat): 
            pass
        else: 
            raise ValueError(f"State of solver after adding user input conceptual graph constraints is {state}")

        # Double check that the new_assertions do not cause UNSAT
        new_state = solver.check(assertions)
        import pdb; pdb.set_trace()
        if new_state == sat: 
            # return (solver, assertions)
            return solver
        elif new_state == unsat: 
            import pdb; pdb.set_trace()
            return check_update_constraints(solver=solver, assertions=assertions)
        else: 
            raise ValueError (f"Solver state is neither SAT nor UNSAT: {new_state}")

def parse_and_create_variable_relationship_graph(solver: Solver): 
    mdl = solver.model()
    print(mdl)
    
    # Should ask if this is valid before being output? (maybe more complex interactive editing is for later)