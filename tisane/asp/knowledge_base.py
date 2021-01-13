from tisane.concept import Concept
from tisane.effect_set import EffectSet
from tisane.statistical_model import StatisticalModel

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

def format_concept_variable_constraint(concept: Concept, key: str, val: str): 
            c_name = concept.getVariableName()

            ## Variable constraints
            if key.upper() == 'DTYPE': 
                if val == 'numeric': 
                    return f'numeric({c_name}).'
                elif val =='nominal': 
                    # return f'nominal({c_name}).'
                    return f'categorical({c_name}).'
                else: 
                    # import pdb; pdb.set_trace()
                    raise NotImplementedError
            elif key.upper() == 'CARDINALITY': 
                return f'binary({c_name}).'
            else:
                # import pdb; pdb.set_trace()
                return NotImplementedError

def format_effect_set_constraint(effect_set: EffectSet, key: str, val: str): 
            ivs = list()
            for e in effect_set.get_main_effects().effect:
                e_name = e.lower().replace(' ', '_') 
                ivs.append(e_name)
            ivs_names = ','.join(ivs)

            dv_name = effect_set.get_dv().name.lower().replace(' ', '_') 
            all_names = ','.join(ivs) + f',{dv_name}'

            ## Effect set constraints
            if key.upper() == 'TOLERATE_CORRELATION': 
                if val: 
                    return f'tolerate_correlation({ivs_names}).'
                else: 
                    return f'not_tolerate_correlation({ivs_names}).'
            elif key.upper() == 'DISTRIBUTION': 
                if val == 'normal': 
                    return f'normal({ivs_names}).'
                else: 
                    raise NotImplementedError
            elif key.upper() == 'HOMOSCEDASTIC_RESIDUALS': 
                if val: 
                    return f'homoscedastic_residuals({all_names}).'
            elif key.upper() == 'NORMAL_RESIDUALS': 
                if val: 
                    return f'normal_residuals({all_names}).'

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


    def get_concept_constraints(self, concept: Concept): 
        assertions = list() 
        
        # add constraints that ground the variables
        c_name = concept.name.lower().replace(' ', '_') 
        assertions.append(f'variable({c_name}).')

        # add constraints that pertain to properties of the variables
        if concept.has_assertions(): 
            assert_dict = concept.get_assertions()
        
            for k, v in assert_dict.items(): 
                ass = format_concept_variable_constraint(concept=concept, key=k, val=v)
                assertions.append(ass)
        
        return assertions
    
    def get_effect_set_constraints(self, effect_set: EffectSet): 
        assertions = list()

        if effect_set.has_assertions(): 
            assert_dict = effect_set.get_assertions()
            
            for k, v in assert_dict.items(): 
                ass = format_effect_set_constraint(effect_set=effect_set, key=k, val=v)
                assertions.append(ass)
        
        return assertions

    # @param file is a .lp file containing ASP constraints
    def query(self, file_name: str, assertions: list): 
        assert(".lp" in file_name)

        # # collect assertions before querying
        # self.collect_assertions(ivs=ivs, dv=dv)

        # Read file in as a string
        constraints = None
        file_abs_path = absolute_path(file_name)
        with open(file_abs_path, 'r') as f:
            constraints = f.read()
        
        # Add assertions to read-in file
        formatted_all_assertions = '\n'.join(str(a) for a in assertions)
        
        # Concatenate constraints with assertions
        query = constraints + formatted_all_assertions
        query = query.encode("utf8") # Add encoding

        # Run clingo 
        clingo_command = ["clingo"]
        proc = subprocess.Popen(args=clingo_command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        stdout, stderr = proc.communicate(query)    
        
        return (stdout, stderr)
    
    # def is_query_successful(self, query_result: tuple): 
    #     assert(len(query_result) == 2) # KnowledgeBase query only returns 2-tuple
    #     valid_models =list()

    #     output = query_result[0]
    #     error = query_result[1]
    #     output_str = output.decode("utf8") # bytes to string
        
    #     # Extracting to find the answer now 
    #     ans = output_str.split('Answer')
    #     ans_metrics = ans.split('\n')

    #     if 'UNSATISFIABLE' in ans_metrics: 
    #         return False
    #     elif 'SATISFIABLE' in ans_metrics: 
    #         return True
    #     else: 
    #         raise ValueError(f"Query result is neither UNSAT or SAT!: {output}")

    # TODO: Move this to be an outside helper function
    # Should be called after query() function 
    # @param query_result has is a tuple resulting from calling KnowledgeBase's query() function
    def construct_models_from_query_result(self, query_result: tuple, effect_set: EffectSet): 

        output = query_result[0]
        error = query_result[1]
        assert(not error) # there is no error

        output_str = output.decode("utf8") # bytes to string
        # Extracting to find the answer now 
        ans = output_str.split('Answer')
        ans_metrics = ans[1].split('\n')
    
        # get index of SAT keyword 
        end_idx = ans_metrics.index('SATISFIABLE')
            
        # Figure out set of valid linear models
        valid_model_names = [ans_metrics[i] for i in range(end_idx)]
        assert(len(valid_model_names) >= 1)
        
        valid_models = list()
        for m in valid_model_names: 
            if "linear_regression" in m:
                mdl = StatisticalModel.create(model_type="linear_regression", effect_set=effect_set)
                valid_models.append(mdl)
    
        assert(len(valid_models) >= 1)
        return valid_models

    def get_query_result(self):
        raise NotImplementedError
        # Parse output 
        
        # Return output

    # TODO: May want to refactor and make more generic KnowledgeBase querying interface?
    # TODO: KB wrapper for running query, adding assertions, getting results, etc?
