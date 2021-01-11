from tisane.concept import Concept
from tisane.effect_set import EffectSet

import os 
import subprocess
import re 
from typing import List

single_arity = [    'variable(X)',
                    'numeric(X)',
                    'numeric_or_categorical(X)',
                    'transformed(X)'
                ]

_effects_sets_to_constraints_files = dict()

def absolute_path(p: str) -> str:
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), p)

class KnowledgeBase(object):
    
    # @param name is string for set of variables that are supported/instantiate the constraints
    # @param ivs is a list of main effects we are considering 
    # @param dv is a list of DV Concept, need to check length is 1
    # TODO: Change @param effects into a set????
    # TODO: change name/automatically change
    def generate_constraints(self, name: str, ivs: List[Concept], dv: List[Concept]): 
        global single_arity, _effects_sets_to_constraints_files

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
                    
                    # Copy empty
                    elif len(line.strip()) == 0:
                        new_line = line
                    
                    # Copy #const without modification
                    elif "#const" in line:
                        new_line = line
                    
                    # Update show arity
                    elif "#show" in line: 
                        # Are there any digits in the line indicating arity?
                        if re.search(r'[1-9]\D', line):
                            clauses = line.split("/")
                            import pdb; pdb.set_trace()
                            new_line = clauses[0] + "/" + str(len(ivs) + len(dv)) + ".\n"
                        else: 
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
                                r_cleaned = r.strip()
                                # Only process non-new line characters
                                if len(r_cleaned) >= 1:
                                    r_cleaned = r.strip()
                                    
                                    if "." not in r_cleaned:
                                        r_cleaned += ")"

                                    # Add single-arity rules for all IVs
                                    if r_cleaned in single_arity:
                                        for i in range(len(main_effects_list)):
                                            new_rules += r_cleaned.replace("X", main_effects_list[i])
                                            # if i+1 < len(main_effects_list):
                                            new_rules += ", "
                                    
                                    # If not single-arity, replace Xs with new IVs
                                    else:
                                        new_rules += r_cleaned.replace("X", main_effects_str)
                                        if "." not in r_cleaned: 
                                            new_rules += ", "
                                
                                # Keep track of if we processed the entire logical rule    
                                if "." in r_cleaned:
                                    new_rules += "\n"
                                    rule_completed = True

                            new_line = new_head + ":- " + new_rules
                        
                        # This is a continuation of a constraint
                        else: 
                            assert(":-" not in line)
                            new_head = str()
                            new_rules = str()

                            # Update the rules
                            rule_list = line.split("),")

                            for r in rule_list:
                                r_cleaned = r.strip()
                                # Only process non-new line characters
                                if len(r_cleaned) >= 1:
                                    if "." not in r_cleaned:
                                        r_cleaned += ")"
                                    
                                    # Add single-arity rules for all IVs
                                    if r_cleaned in single_arity:
                                        for i in range(len(main_effects_list)):
                                            new_rules += r_cleaned.replace("X", main_effects_list[i])
                                            # if i+1 < len(main_effects_list):
                                            new_rules += ", "
            
                                    # If not single-arity, replace Xs with new IVs
                                    else:
                                        new_rules += r_cleaned.replace("X", main_effects_str)
                                        if "." not in r_cleaned: 
                                            new_rules += ", "
                                # else:
                                #     new_rules += r_cleaned + ", "

                                # Keep track of if we processed the entire logical rule    
                                if "." in r_cleaned:
                                    new_rules += "\n"
                                    rule_completed = True

                            new_line = new_rules

                    specific_constraints.write(new_line)
                    rule_completed = False

        _effects_sets_to_constraints_files[f'(ivs={ivs}, dv={dv})'] = specific_abs_path
    
    # Add assertions for solving!!
    # These assertions are "global" in the sense that they will apply to all sets of constraints in _effects_sets_to_constraints_files
    def assert_property(self, prop:str): 
        raise NotImplementedError

    # TODO: Add all the assertions into a list
    # TODO: Return String instead of List of assertions?
    # TODO: Need a set of effects rather than return all assertions? -- maybe split into multiple functions?
    def get_assertions(self) -> list: 
        all_assertions = list()

        return all_assertions


    def get_concept_variable_constraint(self, concept: Concept, key: str, val: str): 
        c_name = concept.getVariableName()
        
        ## Variable constraints
        if key == 'dtype': 
            if val == 'numeric': 
                return f'numeric({c_name}).'
            elif val =='nominal': 
                return f'nominal({c_name}).'
            else: 
                raise NotImplementedError
        elif key == 'cardinality': 
            return f'binary({c_name}).'
        else: 
            return NotImplementedError
    
    def get_effect_set_constraint(self, effect_set: EffectSet, key: str, val: str): 
        ivs = list()
        for e in effect_set.get_main_effects().effect:
            e_name = e.lower().replace(' ', '_') 
            ivs.append(e_name)
        ivs_names = ','.join(ivs)

        ## Effect set constraints
        if key == 'tolerate_correlation': 
            if val: 
                return f'tolerate_correlation({ivs_names}).'
            else: 
                return f'not_tolerate_correlation({ivs_names}).'
        elif key == 'distribution': 
            if val == 'normal': 
                return f'normal({ivs_names}).'
            else: 
                raise NotImplementedError
        elif key == 'homoscedastic': 
            if val: 
                return f'homoscedastic({ivs_names}).'

    # collect and format assertions to include in query
    def collect_assertions(self, ivs: List[Concept], dv: Concept): 
        assertions_list = list() # List[str]

        # add constraints that ground the variables
        # add IVs
        for i in ivs: 
            assertions_list.append(f'variable({i.name}).')
        # add DV
        assertions_list.append(f'variable({dv.name}).')
        
        #  add constraints based on properties of variables, effect set (set of variables)
        for i in ivs: 
            # the IV has assertions
            if i.has_assertions(): 
                assertions_list.append(get_constraint(v=i, key=k, val=v))
                


    # @param file is a .lp file containing ASP constraints
    def query(self, file_name: str, ivs: List[Concept], dv: Concept): 
        assert(".lp" in file_name)

        # collect assertions before querying
        self.collect_assertions(ivs=ivs, dv=dv)

        # Read file in as a string
        constraints = None
        with open(file_name, 'r') as f:
            constraints = f.read()
        
        # Add assertions to read-in file
        all_assertions = self.get_assertions()
        formatted_all_assertions = '\n'.join(str(a) for a in all_assertions)
        
        # Concatenate constraints with assertions
        query = constraints + formatted_all_assertions
        query = stquery.encode("utf8") # Add encoding

        # Run clingo 
        clingo_command = ["clingo"]
        proc = subprocess.Popen(args=clingo_command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        stdout, stderr = proc.communicate(query)    
        
        return (stdout, stderr)
    
    def get_query_result(self):
        raise NotImplementedError
        # Parse output 
        
        # Return output

    # TODO: May want to refactor and make more generic KnowledgeBase querying interface?
    # TODO: KB wrapper for running query, adding assertions, getting results, etc?
