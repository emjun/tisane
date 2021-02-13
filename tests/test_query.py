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
        tutoring = Nominal('tutoring', 2) # Categorical('tutoring')

        # Create graph
        gr = Graph()
        gr = gr.correlate(age, sat_score)
        gr.cause(tutoring, sat_score)
        # Could be more functional 
        # correlate(age, sat_score, graph=gr)

        design = Design(ivs=[age, tutoring], dv=sat_score)
        design.nest(student_id, classroom)
        design.assign(tutoring, student_id)

        # Need to update graph with design info
        # design.nest(student_id, classroom, gr)
        # gr.apply(design) 
        # Could be more functional 
        # apply(design, gr)?

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


    def test_design_to_sm(self): 
        design = Design(ivs=[age, tutoring], dv=sat_score)
        design.nest(student_id, classroom) # -> nest(student_id, classroom, design)
        design.assign(tutoring, student_id)

        (gr, sm) = ts.infer_from(design, StatisticalModel())

    def test_design_to_graph(self): 
        design = Design(ivs=[age, tutoring], dv=sat_score, unit=student_id) # unit of obs, what rows correspond to, id?
        # Even if these IVs are not specified when creating Design object, they
        # are added when declared in this way.
        design.nest(student_id, classroom)
        design.assign(tutoring, student_id)
        # TODO: Should we somehow represent student_id has-a age?  (implied by unit=student_id?)
        # design.assign(age, student_id) # seems kinda weird to "assign"

        # TODO: During inference process, need to ask about interactions...
        gr = ts.infer_from(design, Graph())

    def test_sm_to_design(self): 
        sm = StatisticalModel( dv=sat_score, 
                                    main_effects=[age, tutoring], 
                                    interaction_effects=[(age, tutoring)], 
                                    mixed_effects=[])
                                    # link='identity', 
                                    # variance='Gaussian') 

        design = ts.infer_from(sm, Design())

    def test_sm_to_graph(self): 
        sm = StatisticalModel( dv=sat_score, 
                                    main_effects=[age, tutoring], 
                                    interaction_effects=[(age, tutoring)], 
                                    mixed_effects=[])
                                    # link='identity', 
                                    # variance='Gaussian') 

        gr = ts.infer_from(sm, Graph())

    def test_graph_to_design(self): 
        student_id = Variable('pid') # TODO: What happens if we dont have this? 
        classroom = Variable('class') # TODO: What happens if we dont have this? 
        age = Variable('age')
        tutoring = Variable('tutoring')
        sat_score = Variable('score')

        gr = Graph()
        gr = gr.correlate(age, sat_score)
        gr.cause(tutoring, sat_score)

        # TODO: Ask about nesting???
        design = ts.infer_from(gr, Design())

    # TODO: Seems like would have to ask about data schema, data collection 
    # TODO: Graph -> Experimental Design -> Statistical Model??
    def test_graph_to_sm(self): 
        student_id = Variable('pid') # TODO: What happens if we dont have this? 
        classroom = Variable('class') # TODO: What happens if we dont have this? 
        age = Variable('age')
        tutoring = Variable('tutoring')
        sat_score = Variable('score')

        gr = Graph()
        gr = gr.correlate(age, sat_score)
        gr.cause(tutoring, sat_score)

        sm = ts.infer_from(gr, StatisticalModel()) # Might require thinking about how to collect data....?
        
    # TODO: Do we want to support this use case? More of a use case for verification? Future work?
    def test_graph_and_data_schema_to_design(self):
        student_id = Numeric('pid')
        classroom = Numeric('class')
        age = Numeric('age')
        sat_score = Numeric('score')

        gr = Graph()
        gr = gr.correlate(age, sat_score)
        gr.cause(tutoring, sat_score)

        design = ts.infer_from(gr, Design())
    # def test_statistical_model_to_data_schema(self): 
    #     stat_mod = ts.StatisticalModel( dv='SAT', 
    #                                 main_effects=['Intelligence', 'Age'], 
    #                                 interaction_effects=[], 
    #                                 mixed_effects=[], 
    #                                 link='identity', 
    #                                 variance='Gaussian') 

    # Interaction effect SM -> Data Schema

    #     ts.query(input_obj=stat_mod, outcome='data schema')

