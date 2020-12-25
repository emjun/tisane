from tisane.concept import Concept

import os 
import re 
from typing import List

single_arity = [    'variable(X)',
                    'numeric(X)',
                    'numeric_or_categorical(X)',
                    'transformed(X)'
                ]

def absolute_path(p: str) -> str:
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), p)

class KnowledgeBase(object):
    
    # @param name is string for set of variables that are supported/instantiate the constraints
    # @param ivs is a list of main effects we are considering 
    # @param dv is a list of DV Concept, need to check length is 1
    # TODO: Change @param effects into a set????
    # TODO: change name/automatically change
    def generate_constraints(self, name: str, ivs: List[Concept], dv: List[Concept]): 
        global single_arity

        assert(len(dv) == 1)

        specific_file_name = 'specific_constraints_' + name + '.lp'
        specific_abs_path = absolute_path(specific_file_name)
        generic_abs_path = absolute_path('generic_constraints.lp')

        with open(generic_abs_path, 'r') as generic_constraints, open(specific_abs_path, 'w') as specific_constraints: 

                main_effects_str = 'X0'
                main_effects_list = ['X0']
                if len(ivs) > 1:
                    for i in range(1, len(ivs)):
                        main_effects_str += (', X' + str(i))
                        main_effects_list.append('X' + str(i))

                for line in generic_constraints.readlines():
                    new_line = str()

                    # Ignore comments
                    if "%" in line: 
                        pass      

                    # See if the line is a logical rule
                    elif ":-" in line:
                        new_head = str()
                        new_rules = str()

                        # Check if there is a head
                        clauses = line.split(":- ")
                        if len(clauses) == 2:
                            head = clauses[0]
                            rules = clauses[1]
                        
                            # Update the head
                            if 'X' in head:
                                new_head = head.replace("X", main_effects_str)
                            else:
                                new_head = head

                        elif len(clauses) == 1:
                            rules = clauses[0]

                        else:
                            raise ValueError(f"Encountered a logical rule with more than a head and a list of rules (2 elements total).")
                        
                        # Update the rules
                        rule_list = rules.split(",")
                        for r in rule_list:
                            if r.strip() in single_arity:
                                for i in range(len(main_effects_list)):
                                    new_rules += r.replace("X", main_effects_list[i])
                                    if i+1 < len(main_effects_list):
                                        new_rules += ", "
                            else:
                                new_rules += r.replace("X", main_effects_str)
                            if not "\n" in r:
                                new_rules += ","
                        
                        new_line = new_head + ":- " + new_rules
                    
                    elif "X" in line:
                        assert(":-" not in line)
                        clauses = line.split("\n")
                        for c in clauses:
                            if c.strip() in single_arity:
                                    for i in range(len(main_effects_list)):
                                        new_line += c.replace("X", main_effects_list[i])
                                        if i+1 < len(main_effects_list):
                                            new_line += ", "
                            else:
                                import pdb; pdb.set_trace()
                                new_line += c.replace("X", main_effects_str)
                    else:
                        new_line = line
                    
                    specific_constraints.write(new_line)

                    # Add assertions for solving!!

                    # Add more statistical tests!


