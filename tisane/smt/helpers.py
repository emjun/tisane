from z3 import *

def get_facts_as_list(facts: dict): 
    all_facts = list()
    for k, v in facts.items(): 
        if k != 'variables': 
            all_facts += v
    
    return all_facts