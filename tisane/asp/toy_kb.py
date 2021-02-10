from clingo.control import Control
from clingo.solving import SolveHandle, SolveResult
import os

def absolute_path(p: str) -> str:
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), p)

generic_rules_path = absolute_path('toy_constraints.lp')
specific_rules = "model(iq, age, sat). link(sat, identity). "

def query(): 
    global generic_rules_path, specific_rules

    with open(generic_rules_path, 'r') as readfile: 
        rules = readfile.readlines()
    rules_str = ''.join(rules) + specific_rules

    ctl = Control()
    ctl.add("base", [], rules_str)
    ctl.ground([("base", [])])
    answer = ctl.solve(on_model=print, yield_=True)    
    # how to get the unsat core? 
    answer.core() # returns [], answer.get() is UNSAT

def query_chunks(): 
    global generic_rules_path, specific_rules

    with open(generic_rules_path, 'r') as readfile: 
        rules = readfile.readlines()

    i = 0 # count the number of new rules we are considering at the moment
    max_rule_count = 5
    curr_rules = list()
    for idx in range(len(rules)): 
        r = rules[idx]
        curr_rules.append(r)
        i += 1

        # Reached max number of new rules want to consider at this time
        if i == max_rule_count or idx+1 == len(rules): 
            curr_rules_str = ''.join(curr_rules)
            ctl = Control()
            ctl.add("base", [], curr_rules_str)
            # ctl.add("base", [], specific_rules)
            ctl.ground([("base", [])])
            # TODO: not sure how to pass assumptions...??
            answer = ctl.solve(assumptions=''.join(specific_rules), on_model=print, yield_=True)    
            import pdb; pdb.set_trace()
            result = answer.get()

            # If the query is SAT            
            if result.satisfiable: 
                i = 0 # reset counter
            elif result.unsatisfiable:
                # Get clauses that cause UNSAT
                unsat_core = answer.core() # currently returns []

                for clause in unsat_core: 
                    # Ask for user input 
                    while True: 
                        try: 
                            val = input(f'Can you clarify {clause}:')
                        except ValueError: 
                            print("Try again.")
                            continue
                        else: 
                            break
                # TODO: Now verify that with the user clarifications, the query is SAT



if __name__ == '__main__': 
    print(f"Trying to execute query all at once.\n")
    # query()
    print(f"Trying to execute query in chunks.\n")
    query_chunks()
    import pdb; pdb.set_trace()
