from tisane import *

from z3 import *
import unittest

class QueryTest(unittest.TestCase): 

    # Included only when need to debug pytest
    def test(self): 
        print('hi')

    def test_design_to_graph_between(self): 
        student_id = Numeric('student_id')
        sat_score = Numeric('sat_score')
        tutoring = Nominal('tutoring', cardinality=2) # Categorical('tutoring')
        
        design = Design(dv = sat_score)
        design.treat(student_id, tutoring, 'between')
        
        # Vis pre-disambiguation
        # design.graph.visualize_graph()
        
        gr = infer_from(design, 'variable relationship graph')

        gr.visualize_graph()
    # TODO: What happens if end-user does not specify the types of variables? (When Graph -> Design/SM)? 

    # # TODO: Think through how an end-user might express interaction in a study design 
    # # def test_design_to_graph_interaction(self): 
    # #     student_id = Numeric('student_id')
    # #     sat_score = Numeric('sat_score')
    # #     tutoring = Nominal('tutoring', cardinality=2) # Categorical('tutoring')
        
    # #     design = Design(dv = sat_score)
    # #     design.treat(student_id, tutoring, 'between')
        
    # #     # Vis pre-disambiguation
    # #     # design.graph.visualize_graph()
        
    # #     gr = infer_from(design, 'variable relationship graph')

    # #     gr.visualize_graph()

    # def test_design_sm_between(self): 
    #     student_id = Numeric('student_id')
    #     sat_score = Numeric('sat_score')
    #     tutoring = Nominal('tutoring', cardinality=2) # Categorical('tutoring')
        
    #     design = Design(dv = sat_score)
    #     design.treat(student_id, tutoring, 'between')

    #     sm = infer_from(design, 'statistical model')

    #     print(sm)
    #     print(sm.mathematize())

    # def test_sm_to_graph_main(self): 
    #     student_id = Numeric('student_id')
    #     sat_score = Numeric('sat_score')
    #     tutoring = Nominal('tutoring', cardinality=2) # Categorical('tutoring')
        
    #     sm = StatisticalModel(dv=sat_score, main_effects=[tutoring])

    #     gr = infer_from(sm, 'variable relationship graph')
        
    #     gr.visualize_graph()

    # def test_sm_to_graph_interaction(self): 
    #     student_id = Numeric('student_id')
    #     intelligence = Numeric('iq')
    #     sat_score = Numeric('sat_score')
    #     tutoring = Nominal('tutoring', cardinality=2) # Categorical('tutoring')
        
        # sm = StatisticalModel(dv=sat_score, main_effects=[tutoring, intelligence], interaction_effects=[(intelligence, tutoring)])

    #     gr = infer_from(sm, 'variable relationship graph')
        
    #     gr.visualize_graph()

    # TODO: COME BACK TO!
    # def test_sm_to_design_between(self):
    #     sat_score = Variable('sat_score')
    #     tutoring = Variable('tutoring')
        
    #     sm = StatisticalModel(dv=sat_score, main_effects=[tutoring], link_func='Log', variance_func='Gaussian')

    #     design = infer_from(sm, 'study design')
    #     import pdb; pdb.set_trace()

    #     # GOAL 
    #     # design = Design(dv = sat_score)
    #     # design.treat(student_id, tutoring, 'between')
        
    #     print(design)

    def test_graph_to_design_simple(self): 
        sat_score = Variable('sat_score')
        tutoring = Variable('tutoring')
        
        gr = Graph()
        gr.cause(tutoring, sat_score)
        
        # GOAL
        # design = Design(dv = sat_score)
        # design.treat(student_id, tutoring, 'between')

        design = infer_from(gr, 'study design')

        # TODO: For "Between" --> Student_id should be in Graph? 
        # TODO: How much to suggest changes to the original input? Not take as complete truth? (Maybe this is what makes this domain a bit harder for interactive synth?)
    
    def test_graph_to_statistical_model(self): 
        pass

    # def test_sm_to_design_between_multiple(self): 
    #     # TODO: Allow for "Variable" rather than "Numeric/Nominal/Ordinal" -- might have to change the code in a few different places
    #     student_id = Numeric('student_id')
    #     intelligence = Numeric('iq')
    #     sat_score = Numeric('sat_score')
    #     tutoring = Nominal('tutoring', cardinality=2) # Categorical('tutoring')
        
    #     sm = StatisticalModel(dv=sat_score, main_effects=[tutoring, intelligence])

    #     design = infer_from(sm, 'study design')
    #     import pdb; pdb.set_trace()
        
    #     print(design)

    # def test_design_to_graph_nested_between(self): 
    #     student_id = Numeric('student_id')
    #     classroom = Numeric('class', cardinality=4)
    #     age = Numeric('age')
    #     sat_score = Numeric('sat_score')
    #     tutoring = Nominal('tutoring', cardinality=2) # Categorical('tutoring')

    #     # Application of treatment - *that* we treat units
    #     design = Design(dv = sat_score)
    #     design.nest(studenƒ2t_id, classroom)
    #     treatment = design.treat(classroom, tutoring) # "algorithm"

    #     # "schedule" - *how* we treat units
    #     treatment.assign(classroom, 1) # Between implied since know Tutoring has cardinality 2
    #     treatment.assign(classroom, 2) # Within applied since know Tutoring has cardinality 2
    #     # TODO: Assumption: Don't need to know exact order or conditions but that conditions were distributed as between vs. within?
    #     # TODO: If num (second @param in assign) does not go into group (e.g., classroom) evenly, surface issue to end-user?
        

    # def test_design_to_graph_nested_within(self): 
    #     pass

    # TODO: to SM for nested between and within

    # def test_design_to_sm_main(self): 
    #     design = Design(dv = sat_score)
    #     design.treat(student_id, tutoring, times=1)

    #     (gr, sm) = ts.infer_from(design, StatisticalModel())

    # def test_design_to_sm_main_interaction(self): 
    #     pass
    
    # def test_design_to_sm_main_interaction_nested(self): 
    #     pass

    # def test_design_to_sm_main_nested(self): 
    #     design = Design()
    #     # "unit" is implied in nesting structure
    #     design.nest(student_id, classroom) # -> nest(student_id, classroom, design)
    #     # "unit" is implied in assignment
    #     design.treat(student_id, tutoring)

    #     (gr, sm) = ts.infer_from(design, StatisticalModel())

    #     # Example
    #     # Exam score measured once after tutoring
    #     design = Design(dv=exam_score)
    #     design.treat(student_id, tutoring) # between-subjects (implicit)

    #     # Exam score measured twice: before and after tutoring
    #     design = Design(dv=diff_exam_score)
    #     design.treat(student_id, tutoring)

    #     design = Design(dv=exam_score)
    #     design.treat(student_id, tutoring)
    #     design.treat(student_id, exam_time) # "Treat" feels weird here

    #     # Exam score measured twice: middle and after tutoring
    #     design = Design(dv=exam_score)
    #     design.treat(student_id, tutoring) # assume between-subjects
    #     # design.measure(student_id, exam_time) # exam_time is middle, after
    #     design.treat(student_id, exam_time) # exam_time is middle, after
    #     design.treat(exam_time, exam_score) # exam_time is middle, after
    #     # OR
    #     design.measure(exam_score, exam_time) # measure exam_score according to exam_time, exam-score must be DV (?)
    #     # Below is sugar for two calls to treat?
    #     # "repeat" or "measure"?
    #     design.repeat(student_id, exam_score, exam_time) # exam_time is middle, after
        
    #     design = Design(dv=score)
    #     design.treat(student_id, condition, times=1) # between-subjects
    #     design.treat(task, condition, times=2) # within-subjects

    #     design = Design(dv=score)
    #     design.treat(student_id, condition) # between-subjects
    #     design.randomize(student_id, condition, times=1) # between-subjects
    #     design.treat(task, condition) # within-subjects
    #     design.randomize(task, condition, times=2) # within-subjects
        
    #     design.treat(student_id, condition)
    #     design.nest(task, condition)

    #     """ DESIGN DECISION
    #     NO: Assuming relationships in Graph based on IV inclusion in Design ctor mixes concerns, don't like this!
    #     # Without IVS explicitly stated, assume that all vars in design associated with dv
    #     design = Design(dv=exam_score) #ivs=[style, exam_type], dv=exam_score)
    #     design.nest(student_id, classroom)
    #     design.treat(classroom, style)
    #     design.treat(exam_type, student_id)
        
    #     # With IVS explicitly stated, assume that only those in design associated with dv
    #     design = Design(ivs=[style, exam_type], dv=exam_score)
    #     """

    # def test_design_to_sm(self): 
    #     # Example from Edibble (R package): 
    #     # des <- start_design(name = "Effective teaching") %>%
    #     # set_units(class = 4,
    #     #         student = nested_in(class, 30)) %>%
    #     # set_trts(style = c("flipped", "traditional"),
    #     #         exam = c("take-home", "open-book", "closed-book")) %>%
    #     # allocate_trts(style ~ class,
    #     #             exam ~ student) %>%
    #     # randomise_trts()

    #     # Corresponding Tisane code, doesn't care/ask about # of allocations: 
    #     design = Design(dv=exam_score)
    #     design.nest(student_id, classroom) # 30 students in classroom, if different numbers, provide more granular "nest" methods for each classroom val
    #     # design.nest(student_id, classroom, 30) # 30 students in classroom, if different numbers, provide more granular "nest" methods for each classroom val
    #     design.treat(classroom, style)
    #     design.treat(exam_type, student_id)

    # def test_design_to_graph(self): 
    #     design = Design(ivs=[age, tutoring], dv=sat_score, unit=student_id) # unit of obs, what rows correspond to, id?
    #     # Even if these IVs are not specified when creating Design object, they
    #     # are added when declared in this way.
    #     design.nest(student_id, classroom)
    #     design.assign(student_id, tutoring)
    #     # TODO: Should we somehow represent student_id has-a age?  (implied by unit=student_id?)
    #     # design.assign(age, student_id) # seems kinda weird to "assign"

    #     # TODO: During inference process, need to ask about interactions...
    #     gr = ts.infer_from(design, Graph())

    # def test_graph_to_design(self): 
    #     student_id = Variable('pid') # TODO: What happens if we dont have this? 
    #     classroom = Variable('class') # TODO: What happens if we dont have this? 
    #     age = Variable('age')
    #     tutoring = Variable('tutoring')
    #     sat_score = Variable('score')

    #     gr = Graph()
    #     gr = gr.correlate(age, sat_score)
    #     gr.cause(tutoring, sat_score)

    #     # TODO: Ask about nesting???
    #     design = ts.infer_from(gr, Design())

    # # TODO: Seems like would have to ask about data schema, data collection 
    # # TODO: Graph -> Experimental Design -> Statistical Model??
    # def test_graph_to_sm(self): 
    #     student_id = Variable('pid') # TODO: What happens if we dont have this? 
    #     classroom = Variable('class') # TODO: What happens if we dont have this? 
    #     age = Variable('age')
    #     tutoring = Variable('tutoring')
    #     sat_score = Variable('score')

    #     gr = Graph()
    #     gr = gr.correlate(age, sat_score)
    #     gr.cause(tutoring, sat_score)

    #     sm = ts.infer_from(gr, StatisticalModel()) # Might require thinking about how to collect data....?
        
    # # TODO: Do we want to support this use case? More of a use case for verification? Future work?
    # def test_graph_and_data_schema_to_design(self):
    #     student_id = Numeric('pid')
    #     classroom = Numeric('class')
    #     age = Numeric('age')
    #     sat_score = Numeric('score')

    #     gr = Graph()
    #     gr = gr.correlate(age, sat_score)
    #     gr.cause(tutoring, sat_score)

    #     design = ts.infer_from(gr, Design())
    # # def test_statistical_model_to_data_schema(self): 
    # #     stat_mod = ts.StatisticalModel( dv='SAT', 
    # #                                 main_effects=['Intelligence', 'Age'], 
    # #                                 interaction_effects=[], 
    # #                                 mixed_effects=[], 
    # #                                 link='identity', 
    # #                                 variance='Gaussian') 

    # # Interaction effect SM -> Data Schema

    # #     ts.query(input_obj=stat_mod, outcome='data schema')



# def test_statistical_model_to_variable_relationship_graph_main_effects_only(self): 
    #     # Could have a formula-based interface that parses to this object
    #     # E.g.: 
    #     # ts.StatisticalModel('SAT ~ Intelligence + Age', link='identity', variance='Gaussian')
    #     # or even something in the query function: ts.query('SAT ~ Intelligence + Age', outcome='variable relationship graph'...)
        
    #     sm = ts.StatisticalModel( dv='SAT_Score', 
    #                                 main_effects=['Intelligence', 'Age'], 
    #                                 interaction_effects=[], 
    #                                 mixed_effects=[], 
    #                                 link='identity', 
    #                                 variance='Gaussian') 
    
    #     # sm.to_logical_facts()
    #     sm.query(outcome='variable relationship graph')

    #     # Other important considerations: Currently assume categorical data is
    #     # represented in 1 variable, which is not what is happening
    #     # mathematically, could change this? 

    # def test_statistical_model_to_variable_relationship_graph_main_effects_interaction(self): 
        
    #     sm = ts.StatisticalModel( dv='SAT_Score', 
    #                                 main_effects=['Intelligence', 'Age'], 
    #                                 interaction_effects=[('Intelligence', 'Age')], 
    #                                 mixed_effects=[], 
    #                                 link='identity', 
    #                                 variance='Gaussian') 
        
    #     sm.query(outcome='variable relationship graph')