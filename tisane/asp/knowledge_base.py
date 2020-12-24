import os 
import re 

def absolute_path(p: str) -> str:
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), p)

class KnowledgeBase(object):
    
    # @param name is string for set of variables that are supported/instantiate the constraints
    # TODO: change name/automatically change
    def generate_constraints(self, name: str): 
        specific_file_name = 'specific_constraints' + name + '.lp'
        with open('constraints.lp', 'r') as generic_constraints, open(specific_file_name, 'w') as specific_constraints: 

                for line in generic_constraints.readlines():
                    # Replace all the Xs with Var_names

                    # Add more statistical tests!
                    pass


