import tisane as ts

from z3 import *
import unittest

class StatisticalModelTest(unittest.TestCase): 

    def test_to_logical_facts(self): 
        stat_mod = ts.StatisticalModel( dv='SAT', 
                                main_effects=['Intelligence', 'Age'], 
                                interaction_effects=[], 
                                mixed_effects=[], 
                                link='identity', 
                                variance='normal') 

        # Get this working
        facts = stat_mod.to_logical_facts()
        
        # TODO: may compare Z3 objects by reference rather than value, so should check
        for key, val in facts: 
            pass
    

class DataForTests:   
    intelligence = Const('Intelligence', Object)      
    age = Const('Age', Object)      
    sat_score = Const('SAT', Object)      
    ivs = Concat(Unit(intelligence), Unit(age))

    facts: {
        'variables': [intelligence, age, sat],
        'ivs': ivs 
    }

