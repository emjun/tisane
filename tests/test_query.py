import tisane as ts

from z3 import *
import unittest

class QueryTest(unittest.TestCase): 

    def test(self): 
        print('hi')

    def test_statistical_model_to_variable_relationship_graph_main_effects_only(self): 
        # Could have a formula-based interface that parses to this object
        # E.g.: 
        # ts.StatisticalModel('SAT ~ Intelligence + Age', link='identity', variance='Gaussian')
        # or even something in the query function: ts.query('SAT ~ Intelligence + Age', outcome='variable relationship graph'...)
        
        sm = ts.StatisticalModel( dv='SAT_Score', 
                                    main_effects=['Intelligence', 'Age'], 
                                    interaction_effects=[], 
                                    mixed_effects=[], 
                                    link='identity', 
                                    variance='Gaussian') 
    
        # sm.to_logical_facts()
        sm.query(outcome='variable relationship graph')

        # Other important considerations: Currently assume categorical data is
        # represented in 1 variable, which is not what is happening
        # mathematically, could change this? 

    def test_statistical_model_to_variable_relationship_graph_main_effects_interaction(self): 
        
        sm = ts.StatisticalModel( dv='SAT_Score', 
                                    main_effects=['Intelligence', 'Age'], 
                                    interaction_effects=[('Intelligence', 'Age')], 
                                    mixed_effects=[], 
                                    link='identity', 
                                    variance='Gaussian') 
        
        sm.query(outcome='variable relationship graph')

    def test_idea(self): 
        # Assumes people know data schema when thinking about variables
        student_id = Numeric('pid')
        classroom = Numeric('class')
        age = Numeric('age')
        sat_score = Numeric('score')
        tutoring = Binary('tutoring') # Categorical('tutoring')

        # Create graph
        correlate(age, sat_score)
        cause(tutoring, sat_score)

        design = Design(ivs=[age, tutoring], dv=sat_score)
        design.nest(student_id, classroom)
        design.assign(tutoring, student_id)

        sm = StatisticalModel( dv=sat_score, 
                                    main_effects=[age, tutoring], 
                                    interaction_effects=[(age, tutoring)], 
                                    mixed_effects=[])
                                    # link='identity', 
                                    # variance='Gaussian') 
        
        sm_unknown = StatisticalModel( dv=sat_score, 
                                        main_effects=[unknown(age), unknown(tutoring)],
                                        interaction_effects=[unknown(age, tutoring, ...)]) # unknown construct helpful when analysts have most of an idea but don't know others (partial spec)

        sm = ts.infer_from(design, StatisticalModel())
        graph = ts.infer_from(design, Graph())

        res = ts.verify(design, sm)

    

    # def test_statistical_model_to_data_schema(self): 
    #     stat_mod = ts.StatisticalModel( dv='SAT', 
    #                                 main_effects=['Intelligence', 'Age'], 
    #                                 interaction_effects=[], 
    #                                 mixed_effects=[], 
    #                                 link='identity', 
    #                                 variance='Gaussian') 

    # Interaction effect SM -> Data Schema

    #     ts.query(input_obj=stat_mod, outcome='data schema')

