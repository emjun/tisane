from tisane.concept import Concept
from tisane.variable import AbstractVariable
from tisane.effect_set import EffectSet
from tisane.asp.helpers import absolute_path, format_concept_variable_constraint, format_effect_set_constraint, update_phrase, update_duplicates, update_multiples

from typing import List
import subprocess
from clingo.control import Control

single_arity = [    'variable(X)',
                    'numeric(X)',
                    'numeric_or_categorical(X)',
                    'transformed(X)'
                ]
# cache the constraints generated for any set of variables
__effects_sets_to_constraints__ = dict()

class KnowledgeBase(object):
    all_generic_facts: str # filepath to .lp file containing all facts combined
    
    # TODO: HACK this out!
    """
    # Initialize KnowledgeBase with generic facts 
    # @params files containing different sets of facts
    def __init__(self, generate: str, define: str, test: str, show: str): 
        # TODO: move to helper file
        generate_path = absolute_path(generate)
        define_path = absolute_path(define)
        test_path = absolute_path(test)
        show_path = absolute_path(show)
        all_paths = [generate_path, define_path, test_path, show_path]

        output_path = absolute_path('all_generic_facts.lp')
        with open(output_path, 'r') as outfile: 
            for p in all_paths: 
                with open(p) as readfile: 
                    for line in readfile: 
                        outfile.write(line)
        
        self.all_generic_facts = output_path
    """


    # @param ivs is a list of main effects we are considering 
    # @param dv is a list of DV Concept, need to check length is 1
    # TODO: Change @param effects into a set????
    # TODO: change name/automatically change
    def generate_constraints(self, ivs: List[AbstractVariable], dv: List[AbstractVariable]): 
        global _effects_sets_to_constraints

        assert(len(dv) == 1)

        specific_constraints = list()
        generic_abs_path = absolute_path('all_generic_facts.lp')

        with open(generic_abs_path, 'r') as generic_constraints: 

                main_effects_str = 'X0'
                main_effects_list = ['X0']
                if len(ivs) > 1:
                    for i in range(1, len(ivs)):
                        main_effects_str += (', X' + str(i))
                        main_effects_list.append('X' + str(i))

                # Parse input file and dynamically adapt to current set of effects
                # rule_completed = False
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
                        if "#show 0." in line: 
                            new_line = line
                        else: 
                            # Are there any digits in the line indicating arity?
                            if re.search(r'[1-9]\D', line):
                                clauses = line.split("/")
                                new_line = clauses[0] + "/" + str(len(ivs) + len(dv)) + ".\n"
                            else: 
                                new_line = line

                    # Parse and modify logical constraint
                    # elif not rule_completed:
                        # This contains the beginning of a predicate
                    elif ":-" in line:

                        # Check if there is a head
                        clauses = line.split(":- ")
                        if len(clauses) == 2:
                            head = clauses[0]
                            rule = clauses[1]

                            new_head = update_phrase(head, main_effects_list)
                            new_rule = update_phrase(rule, main_effects_list)

                            if isinstance(new_head, list): 
                                assert('DX' in head)
                                if isinstance(new_rule, list): 
                                    assert('DX' in rule)
                                    assert(len(new_head) == len(new_rule))
                                    lines = [h+':-'+r for h,r in zip(new_head,new_rule)]
                                    new_line = ''.join(lines)
                                else:
                                    assert(isinstance(new_rule, str))
                                    lines = list()
                                    for h in new_head: 
                                        lines.append(h + ':-' + new_rule)
                                    new_line = ''.join(lines)
                            else: 
                                assert(isinstance(new_head, str))
                                if isinstance(new_rule, list):
                                    assert('DX' in rule)
                                    lines = list()
                                    for r in new_rule: 
                                        lines.append(new_head + ':-' + r)
                                    new_line = ''.join(lines)
                                else: 
                                    assert(isinstance(new_rule, str))
                                    new_line = new_head + ':-' + new_rule
                        
                        else: 
                            raise ValueError(f"Line cannot be processed: {line}")    

                    specific_constraints.append(new_line)

        
        __effects_sets_to_constraints__[f'(ivs:{ivs}, dv:{dv})'] = specific_constraints
    
    # Add assertions for solving!!
    # These assertions are "global" in the sense that they will apply to all sets of constraints in __effects_sets_to_constraints__
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

    # @param rules are a list of not yet ground logical rules
    def query(self, rules: list, assertions: list): 
        constraints = ''.join(rules)
        
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
    
    # Try to use clingo module for Python
    def query_clingo(self, rules: list, assertions: list): 
        rules_str = ''.join(rules)
        assertions_str = ''.join(assertions)
        
        ctl = Control()
        ctl.add("base", [], rules_str)
        ctl.add("assertions", [], assertions_str)
        ctl.ground([("base", [])])
        ctl.ground([("assertions", [])])
        print(ctl.solve(on_model=print))
        import pdb; pdb.set_trace()
        # ctl.ground()
        # with prg.builder() as b:
        
        #     prg.ground([("base", [])])
        #     prg.solve(on_model=lambda m: print("Answer: {}".format(m)))

    def query_clyngor(self, rules: list, assertions: list): 
        rules_str = ''.join(rules)
        answer = solve(inline=rules_str)
    

    # Query: Given a statistical model, get a data schema, asking for user input when necessary
    def query_data_schema(self, facts: List[str], ivs: List[AbstractVariable], dv: List[AbstractVariable], **kwargs):
        assert(len(dv) == 1)
        if 'carryover_facts' in kwargs: 
            facts.append(kwargs['carryover_facts'])
    
        rules = list()
        # Check if have dynamically generated constraints for this (ivs, dv)
        if f'(ivs:{ivs}, dv:{dv})' not in __effects_sets_to_constraints__: 
            self.generate_constraints(ivs=ivs, dv=dv)
        rules = __effects_sets_to_constraints__[f'(ivs:{ivs}, dv:{dv})']
        
        # (stdout, stderr) = 
        self.query_clingo(rules=rules, assertions=facts)

        if stderr: 
            # START HERE: process the error somehow - how to check if return UNSAT, what the true vals are in the solver?
            # Check SAT or UNSAT
            import pdb; pdb.set_trace()
            # add more facts, query again
            self.query_data_schema(file_name=file_name, carryover_facts=facts)
        else: 
            # assert SAT
            # parse the output, format data schema
            return output_data_schema(query_results=stdout)
    
    def output_data_schema(self, query_results: str): 
        pass

    def find_data_collection_procedure(self): 
        pass
    
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

    """
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
"""

    def get_query_result(self):
        raise NotImplementedError
        # Parse output 
        
        # Return output

    # TODO: May want to refactor and make more generic KnowledgeBase querying interface?
    # TODO: KB wrapper for running query, adding assertions, getting results, etc?


# Global KnowledgeBase
KB = KnowledgeBase() 