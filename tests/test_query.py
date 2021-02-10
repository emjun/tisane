import tisane as ts

from z3 import *
import unittest

class QueryTest(unittest.TestCase): 

    def test_statistical_model_to_variable_relationship_graph(self): 
        stat_mod = ts.StatisticalModel( dv='SAT', 
                                    main_effects=['Intelligence', 'Age'], 
                                    interaction_effects=[], 
                                    mixed_effects=[], 
                                    link='identity', 
                                    variance='normal') 
        
        ts.query(input_obj=stat_mod, outcome='variable relationship graph')

    # def test_statistical_model_to_data_schema(self): 
    #     stat_mod = ts.StatisticalModel( dv='SAT', 
    #                                 main_effects=['Intelligence', 'Age'], 
    #                                 interaction_effects=[], 
    #                                 mixed_effects=[], 
    #                                 link='identity', 
    #                                 variance='normal') 

    #     ts.query(input_obj=stat_mod, outcome='data schema')

