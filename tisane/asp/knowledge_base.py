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
        generic_abs_path = absolute_path('test_constraints.lp')

        with open(generic_abs_path, 'r') as generic_constraints, open(specific_abs_path, 'w') as specific_constraints: 

                main_effects_str = 'X0'
                main_effects_list = ['X0']
                if len(ivs) > 1:
                    for i in range(1, len(ivs)):
                        main_effects_str += (', X' + str(i))
                        main_effects_list.append('X' + str(i))

                # Parse input file and dynamically adapt to current set of effects
                rule_completed = False
                for line in generic_constraints.readlines():
                    # new line to write out to the new file
                    new_line = str()

                    # Copy comments without modification
                    if "%" in line: 
                        new_line = line

                    # Copy #const, #show without modification
                    elif "#" in line:
                        new_line = line
                    
                    # Copy empty
                    elif len(line.strip()) == 0:
                        new_line = line

                    # Parse and modify logical constraint
                    elif not rule_completed:
                        # This contains the beginning of a constraint
                        if ":-" in line:
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

                            else: 
                                assert(len(clauses) == 1)
                                rules = clauses[0]
                            
                            # Update the rules
                            rule_list = rules.split("),")
                            for r in rule_list:
                                # Only process non-new line characters
                                if len(r.strip()) >= 1:
                                    r_cleaned = r.strip()
                                    if "." not in line:
                                        r_cleaned += ")"
                                    
                                    # Add single-arity rules for all IVs
                                    if r_cleaned in single_arity:
                                        for i in range(len(main_effects_list)):
                                            new_rules += r_cleaned.replace("X", main_effects_list[i])
                                            
                                            # Keep track of if we processed the entire logical rule    
                                            if "." in r_cleaned:
                                                rule_completed = True
                                            # Add a comma if not the end of the rule (designated by a period)
                                            else:
                                                assert("." not in r_cleaned)
                                                new_rules += ", "

                                    # If not single-arity, replace Xs with new IVs
                                    else:
                                        new_rules += r_cleaned.replace("X", main_effects_str)
                            new_line = new_head + ":- " + new_rules
                        
                        # This is a continuation of a constraint
                        else: 
                            assert(":-" not in line)
                            new_head = str()
                            new_rules = str()

                            # Update the rules
                            rule_list = line.split("),")

                            for r in rule_list:
                                # Only process non-new line characters
                                if len(r.strip()) >= 1:
                                    r_cleaned = r.strip()
                                    if "." not in line:
                                        r_cleaned += ")"
                                    
                                    # Add single-arity rules for all IVs
                                    if r_cleaned in single_arity:
                                        for i in range(len(main_effects_list)):
                                            new_rules += r_cleaned.replace("X", main_effects_list[i])
                                            if i+1 < len(main_effects_list):
                                                new_rules += ", "
            
                                    # If not single-arity, replace Xs with new IVs
                                    else:
                                        new_rules += r_cleaned.replace("X", main_effects_str)
                            # Keep track of if we processed the entire logical rule    
                            if "." in line:
                                rule_completed = True
                            else:
                                new_rules += ", "

                            new_line = new_rules

                    specific_constraints.write(new_line)
                    rule_completed = False
                    # import pdb; pdb.set_trace()
                    # TODO: START HERE: Debug dynamic generation (then commit/push)
                    # TODO: Verify the sat/results are correct
                    # TODO: Connect the effects generation and knowledge base

                    # Add assertions for solving!!

                    # Add more statistical tests!


