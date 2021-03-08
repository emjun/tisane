import tisane as ts

from z3 import *
import unittest

# TODO: Expressivity coverage: Look at and re-implement lmer test cases
# TODO: Examples: CCWA, Kreft and de Leeuw, Statistical Rethinking --> look for adversarial examples

class StatisticalModelTest(unittest.TestCase): 

    def test_initialize_main_only_1(self): 
        expl = ts.Nominal('explanation type')
        acc = ts.Numeric('accuracy')
        variables = [acc, expl]

        sm = ts.StatisticalModel(
            dv=acc,
            main_effects=[expl]
        )

        # The graph IR has all the variables
        for v in variables: 
            self.assertTrue(sm.graph.has_variable(v))
        
        # The graph IR has all the edges we expect
        self.assertTrue(sm.graph.has_edge(expl, acc, edge_type='unknown'))
        
    def test_initialize_main_only_2(self): 
        pass

    def test_initialize_main_interaction_1(self): 
        chronotype = ts.Nominal('Group chronotype')
        composition = ts.Nominal('Group composition')
        tod = ts.Nominal('Time of day')
        qtype = ts.Nominal('Question type')
        acc = ts.Numeric('Accuracy')
        group = ts.Nominal('Group')
        variables = [acc, chronotype, composition, tod, qtype]
        
        sm = ts.StatisticalModel(
            dv=acc,
            main_effects=[chronotype, composition, tod, qtype, group], 
            interaction_effects=[(qtype, tod)], 
            random_slopes=None, 
            random_intercepts=None
        )

        # The graph IR has all the variables
        for v in variables: 
            self.assertTrue(sm.graph.has_variable(v))
        
        # The graph IR has all the edges we expect
        # Main effects
        self.assertTrue(sm.graph.has_edge(chronotype, acc, edge_type='unknown'))
        self.assertTrue(sm.graph.has_edge(composition, acc, edge_type='unknown'))
        self.assertTrue(sm.graph.has_edge(tod, acc, edge_type='unknown'))
        self.assertTrue(sm.graph.has_edge(qtype, acc, edge_type='unknown'))
        self.assertTrue(sm.graph.has_edge(group, acc, edge_type='unknown'))

        # Interaction effects
        # TODO: If introduce a new node, we may want to change/update this
        self.assertTrue(sm.graph.has_edge(qtype, tod, edge_type='unknown'))
    
    def test_initialize_main_interaction_2(self): 
        pass
    
    def test_initialize_random_slopes_1(self): 
        pass

    def test_initialize_random_slopes_2(self): 
        pass

    def test_initialize_random_intercepts_1(self): 
        pos_aff = ts.Numeric('Positive Affect')
        es = ts.Numeric('Emotional Suppression')
        cr = ts.Numeric('Cognitive Reappraisal')
        gender = ts.Numeric('Gender')
        age = ts.Numeric('Age')
        time = ts.Numeric('Hours since 7am')
        participant = ts.Nominal('participant')
        # TODO: Update if add random slopes, random intercepts to the graph!
        variables = [pos_aff, es, cr, gender, age, time]

        sm = ts.StatisticalModel(
            dv=pos_aff,
            main_effects=[es, cr, age, gender, time],
            interaction_effects=[(es, time), (cr, time)],
            random_intercepts=[(participant)] # how to include as a random variable?   
        )

        # The graph IR has all the variables
        for v in variables: 
            self.assertTrue(sm.graph.has_variable(v))
        
        # The graph IR has all the edges we expect
        # Main effects
        self.assertTrue(sm.graph.has_edge(es, pos_aff, edge_type='unknown'))
        self.assertTrue(sm.graph.has_edge(cr, pos_aff, edge_type='unknown'))
        self.assertTrue(sm.graph.has_edge(age, pos_aff, edge_type='unknown'))
        self.assertTrue(sm.graph.has_edge(gender, pos_aff, edge_type='unknown'))
        self.assertTrue(sm.graph.has_edge(time, pos_aff, edge_type='unknown'))

        # Interations
        # TODO: Update if add a new node to IR
        self.assertTrue(sm.graph.has_edge(es, time, edge_type='unknown'))
        self.assertTrue(sm.graph.has_edge(cr, time, edge_type='unknown'))

        # Random intercepts
        self.assertTrue((participant) in sm.random_intercepts)

    def test_initialize_random_intercepts_2(self): 
        pass

    # Example from Kreft & de Leeuw 1989, NELS-88 dataset
    # 4.1.2: "The organizaiton of the four sessions"
    def test_initialize_null_model(self): 
        math = Numeric('MathAchievement', student) # interesting because no obvious unit, but probably student
        student = Nominal('id')
        school = Nominal('school')

        sm = ts.StatisticalModel(
            dv=math,
            fixed_ivs=None, 
            random_slopes=None, 
            random_intercepts=None,
            intercept_variances=[ts.Unit(student), ts.Unit(school)] # Establish intercept variances at level of student and level of school
            include_intercept=True # Default: Intercept is always estimated
            # no_intercept=True # An option? By default Intercept is always estimated
        )

    # Example from Kreft & de Leeuw 1989, NELS-88 dataset
    def test_initialize_fixed_1(self): 
        math = Numeric('MathAchievement', student) # interesting because no obvious unit, but probably student
        # Student-level variables 
        student = Nominal('id')
        ses = ('SES', student)
        hw = Numeric('HomeWork', student)
        race = ('Race', student)
        # student = Nominal('id').has(ses, hw, race)

        # School-level variables
        school = Nominal('school')
        edu = Nominal('Public', school) 
        ethnic = ('Percent-Minorities', school)
        class_size = ('Ratio', school)
        # school = Nominal('school').has(edu, ethnic, class_size)
        # Observation: Data schema contains so much information 

        # 4.2.3 # Effect of Homework to be the same in all schools
        sm = ts.StatisticalModel(
            dv=math, # as DV, unit doesn't matter except that it wouldn't make sense to include IVs at a "lower" level than the dv?
            fixed_ivs=[homework], 
            random_slopes=None, 
            random_intercepts=None
            # no_intercept=True # An option? By default Intercept is always estimated
        )

    # Example from Kreft & de Leeuw 1989, NELS-88 dataset
    def test_initialize_random_slope_1(self): 
        math = Numeric('MathAchievement', student) # interesting because no obvious unit, but probably student
        # Student-level variables 
        student = Nominal('id')
        ses = ('SES', student)
        hw = Numeric('HomeWork', student)
        race = ('Race', student)
        # student = Nominal('id').has(ses, hw, race)

        # School-level variables
        school = Nominal('school')
        edu = Nominal('Public', school) 
        ethnic = ('Percent-Minorities', school)
        class_size = ('Ratio', school)
        # school = Nominal('school').has(edu, ethnic, class_size)
        # Observation: Data schema contains so much information 

        # 4.2.4: Effect of Homework differs across schools 
        sm = ts.StatisticalModel(
            dv=math, # as DV, unit doesn't matter except that it wouldn't make sense to include IVs at a "lower" level than the dv?
            fixed_ivs=None, 
            random_slopes=[(hw, school)], # random slope for homework within each school
            random_intercepts=None
            # no_intercept=True # An option? By default Intercept is always estimated
        )

    # Example from Kreft & de Leeuw 1989, NELS-88 dataset
    def test_initialize_random_slope_fixed_1(self): 
        math = Numeric('MathAchievement', student) # interesting because no obvious unit, but probably student
        # Student-level variables 
        student = Nominal('id')
        ses = ('SES', student)
        hw = Numeric('HomeWork', student)
        race = ('Race', student)
        ped = ('ParentEducation', student)
        # student = Nominal('id').has(ses, hw, race)

        # School-level variables
        school = Nominal('school')
        edu = Nominal('Public', school) 
        ethnic = ('Percent-Minorities', school)
        class_size = ('Ratio', school)
        # school = Nominal('school').has(edu, ethnic, class_size)
        # Observation: Data schema contains so much information 

        # 4.2.4: Effect of Homework differs across schools 
        sm = ts.StatisticalModel(
            dv=math, # as DV, unit doesn't matter except that it wouldn't make sense to include IVs at a "lower" level than the dv?
            fixed_ivs=[ped], 
            random_slopes=[(hw, school)], # random slope for homework within each school
            random_intercepts=None
            # no_intercept=True # An option? By default Intercept is always estimated
        )

    # Example from Kreft & de Leeuw 1989, NELS-88 dataset
    def test_initialize_random_slope_fixed_2(self): 
        math = Numeric('MathAchievement', student) # interesting because no obvious unit, but probably student
        # Student-level variables 
        student = Nominal('id')
        ses = ('SES', student)
        hw = Numeric('HomeWork', student)
        race = ('Race', student)
        ped = ('ParentEducation', student)
        # student = Nominal('id').has(ses, hw, race)

        # School-level variables
        school = Nominal('school')
        edu = Nominal('Public', school) 
        ethnic = ('Percent-Minorities', school)
        class_size = ('Ratio', school)
        school_size = ('School Size', school)
        # school = Nominal('school').has(edu, ethnic, class_size)
        # Observation: Data schema contains so much information 

        # 4.2.4: Effect of Homework differs across schools 
        sm = ts.StatisticalModel(
            dv=math, # as DV, unit doesn't matter except that it wouldn't make sense to include IVs at a "lower" level than the dv?
            fixed_ivs=[school_size], 
            random_slopes=[(hw, school)], # random slope for homework within each school
            random_intercepts=None
            # no_intercept=True # An option? By default Intercept is always estimated
        )

    # Example from Kreft & de Leeuw 1989, NELS-88 dataset
    def test_initialize_random_slope_fixed_2(self): 
        math = Numeric('MathAchievement', student) # interesting because no obvious unit, but probably student
        # Student-level variables 
        student = Nominal('id')
        ses = ('SES', student)
        hw = Numeric('HomeWork', student)
        race = ('Race', student)
        ped = ('ParentEducation', student)
        # student = Nominal('id').has(ses, hw, race)

        # School-level variables
        school = Nominal('school')
        sector = Nominal('Public', school) 
        ethnic = ('Percent-Minorities', school)
        class_size = ('Ratio', school)
        school_size = ('School Size', school)
        # school = Nominal('school').has(edu, ethnic, class_size)
        # Observation: Data schema contains so much information 

        # 4.2.4: Effect of Homework differs across schools 
        sm = ts.StatisticalModel(
            dv=math, # as DV, unit doesn't matter except that it wouldn't make sense to include IVs at a "lower" level than the dv?
            fixed_ivs=[sector], 
            random_slopes=[(hw, school)], 
            random_intercepts=None
            # no_intercept=True # An option? By default Intercept is always estimated
        )

    # Example from Kreft & de Leeuw 1989, NELS-88 dataset
    def test_initialize_random_slope_fixed_crossed_1(self): 
        math = Numeric('MathAchievement', student) # interesting because no obvious unit, but probably student
        # Student-level variables 
        student = Nominal('id')
        ses = ('SES', student)
        hw = Numeric('HomeWork', student)
        race = ('Race', student)
        ped = ('ParentEducation', student)
        # student = Nominal('id').has(ses, hw, race)

        # School-level variables
        school = Nominal('school')
        sector = Nominal('Public', school) 
        ethnic = ('Percent-Minorities', school)
        class_size = ('Ratio', school)
        school_size = ('School Size', school)
        # school = Nominal('school').has(edu, ethnic, class_size)
        # Observation: Data schema contains so much information 

        # 4.2.4: Effect of Homework differs across schools 
        sm = ts.StatisticalModel(
            dv=math, # as DV, unit doesn't matter except that it wouldn't make sense to include IVs at a "lower" level than the dv?
            fixed_ivs=[sector], 
            random_slopes=[(hw, school)], 
            random_intercepts=None,
            interactions=[(sector, hw)] # --> (sector*hw, school) in random slopes because hw is a random variable (this is a crossed variable)
            # no_intercept=True # An option? By default Intercept is always estimated
        )

    # Example from Kreft & de Leeuw 1989, NELS-88 dataset
    def test_initialize_random_slope_fixed_3(self): 
        math = Numeric('MathAchievement', student) # interesting because no obvious unit, but probably student
        # Student-level variables 
        student = Nominal('id')
        ses = ('SES', student)
        hw = Numeric('HomeWork', student)
        race = ('Race', student)
        ped = ('ParentEducation', student)
        # student = Nominal('id').has(ses, hw, race)

        # School-level variables
        school = Nominal('school')
        sector = Nominal('Public', school) 
        ethnic = ('Percent-Minorities', school)
        class_size = ('Ratio', school)
        school_size = ('School Size', school)
        # school = Nominal('school').has(edu, ethnic, class_size)
        # Observation: Data schema contains so much information 

        # 4.3.7
        sm = ts.StatisticalModel(
            dv=math, # as DV, unit doesn't matter except that it wouldn't make sense to include IVs at a "lower" level than the dv?
            fixed_ivs=[sector, race], 
            random_slopes=[(hw, school)], 
            random_intercepts=None,
            interactions=None,
            # no_intercept=True # An option? By default Intercept is always estimated
        )

        # Example from Kreft & de Leeuw 1989, NELS-88 dataset
    def test_initialize_random_slope_fixed_4(self): 
        math = Numeric('MathAchievement', student) # interesting because no obvious unit, but probably student
        # Student-level variables 
        student = Nominal('id')
        ses = ('SES', student)
        hw = Numeric('HomeWork', student)
        race = ('Race', student)
        ped = ('ParentEducation', student)
        # student = Nominal('id').has(ses, hw, race)

        # School-level variables
        school = Nominal('school')
        sector = Nominal('Public', school) 
        ethnic = ('Percent-Minorities', school)
        class_size = ('Ratio', school)
        school_size = ('School Size', school)
        # school = Nominal('school').has(edu, ethnic, class_size)
        # Observation: Data schema contains so much information 

        # 4.3.7: "Adding a random part for 'White'"
        sm = ts.StatisticalModel(
            dv=math, # as DV, unit doesn't matter except that it wouldn't make sense to include IVs at a "lower" level than the dv?
            fixed_ivs=[sector], 
            random_slopes=[(hw, school), (race, school)],
            random_intercepts=None,
            interactions=None,
            # no_intercept=True # An option? By default Intercept is always estimated
        )
    
    # Example from Kreft & de Leeuw 1989, NELS-88 dataset
    def test_initialize_random_slope_fixed_5(self): 
        math = Numeric('MathAchievement', student) # interesting because no obvious unit, but probably student
        # Student-level variables 
        student = Nominal('id')
        ses = ('SES', student)
        hw = Numeric('HomeWork', student)
        race = ('Race', student)
        ped = ('ParentEducation', student)
        # student = Nominal('id').has(ses, hw, race)

        # School-level variables
        school = Nominal('school')
        sector = Nominal('Public', school) 
        ethnic = ('Percent-Minorities', school)
        class_size = ('Ratio', school)
        school_size = ('School Size', school)
        mean_ses = Numeric('MeanSES', school)
        # school = Nominal('school').has(edu, ethnic, class_size)
        # Observation: Data schema contains so much information 

        # 4.3.8: "Making the coefficient of 'White' fixed and adding 'MeanSES'"
        sm = ts.StatisticalModel(
            dv=math, # as DV, unit doesn't matter except that it wouldn't make sense to include IVs at a "lower" level than the dv?
            fixed_ivs=[sector, race, mean_ses], 
            random_slopes=[(hw, school)], 
            random_intercepts=None,
            interactions=None,
            # no_intercept=True # An option? By default Intercept is always estimated
        )

    # Example from Kreft & de Leeuw 1989, NELS-88 dataset
    def test_initialize_random_slope_fixed_6(self): 
        math = Numeric('MathAchievement', student) # interesting because no obvious unit, but probably student
        # Student-level variables 
        student = Nominal('id')
        ses = ('SES', student)
        hw = Numeric('HomeWork', student)
        race = ('Race', student)
        ped = ('ParentEducation', student)
        # student = Nominal('id').has(ses, hw, race)

        # School-level variables
        school = Nominal('school')
        sector = Nominal('Public', school) 
        ethnic = ('Percent-Minorities', school)
        class_size = ('Ratio', school)
        school_size = ('School Size', school)
        mean_ses = Numeric('MeanSES', school)
        # school = Nominal('school').has(edu, ethnic, class_size)
        # Observation: Data schema contains so much information 

        # 4.3.9: "Deleting the school characteristic 'Public'"
        sm = ts.StatisticalModel(
            dv=math, # as DV, unit doesn't matter except that it wouldn't make sense to include IVs at a "lower" level than the dv?
            fixed_ivs=[race, mean_ses], 
            random_slopes=[(hw, school)], 
            random_intercepts=None,
            interactions=None,
            # no_intercept=True # An option? By default Intercept is always estimated
        )

    # Example from Kreft & de Leeuw 1989, NELS-88 dataset
    def test_initialize_random_slope_fixed_7(self): 
        math = Numeric('MathAchievement', student) # interesting because no obvious unit, but probably student
        # Student-level variables 
        student = Nominal('id')
        ses = ('SES', student)
        hw = Numeric('HomeWork', student)
        race = ('Race', student)
        ped = ('ParentEducation', student)
        # student = Nominal('id').has(ses, hw, race)

        # School-level variables
        school = Nominal('school')
        sector = Nominal('Public', school) 
        ethnic = ('Percent-Minorities', school)
        class_size = ('Ratio', school)
        school_size = ('School Size', school)
        mean_ses = Numeric('MeanSES', school)
        # school = Nominal('school').has(edu, ethnic, class_size)
        # Observation: Data schema contains so much information 

        # 4.3.10: "Adding an interaction between 'HomeWork' and 'MeanSES'"
        sm = ts.StatisticalModel(
            dv=math, # as DV, unit doesn't matter except that it wouldn't make sense to include IVs at a "lower" level than the dv?
            fixed_ivs=[race, mean_ses], 
            random_slopes=[(hw, school)], 
            random_intercepts=None,
            interactions=[(hw, mean_ses)], # 4.3.10 uses an interaction variable named "HomeSES"
            # no_intercept=True # An option? By default Intercept is always estimated
        )

    # Example from Kreft & de Leeuw 1989, NELS-88 dataset
    def test_initialize_random_slope_fixed_8(self): 
        math = Numeric('MathAchievement', student) # interesting because no obvious unit, but probably student
        # Student-level variables 
        student = Nominal('id')
        ses = ('SES', student)
        hw = Numeric('HomeWork', student)
        race = ('Race', student)
        ped = ('ParentEducation', student)
        # student = Nominal('id').has(ses, hw, race)

        # School-level variables
        school = Nominal('school')
        sector = Nominal('Public', school) 
        ethnic = ('Percent-Minorities', school)
        class_size = ('Ratio', school)
        school_size = ('School Size', school)
        mean_ses = Numeric('MeanSES', school)
        # school = Nominal('school').has(edu, ethnic, class_size)
        # Observation: Data schema contains so much information 

        # 4.3.11: "Adding another student-level variable"
        sm = ts.StatisticalModel(
            dv=math, # as DV, unit doesn't matter except that it wouldn't make sense to include IVs at a "lower" level than the dv?
            fixed_ivs=[race, ses, sector], 
            random_slopes=[(hw, school)], 
            random_intercepts=None,
            interactions=None, 
            # no_intercept=True # Might be better to split into intercept=Levels(student, school, etc.)?  -- See
        )

    # Example from Kreft & de Leeuw 1989, NELS-88 dataset
    def test_initialize_random_slope_fixed_9(self): 
        math = Numeric('MathAchievement', student) # interesting because no obvious unit, but probably student
        # Student-level variables 
        student = Nominal('id')
        ses = ('SES', student)
        hw = Numeric('HomeWork', student)
        race = ('Race', student)
        ped = ('ParentEducation', student)
        # student = Nominal('id').has(ses, hw, race)

        # School-level variables
        school = Nominal('school')
        sector = Nominal('Public', school) 
        ethnic = ('Percent-Minorities', school)
        class_size = ('Ratio', school)
        school_size = ('School Size', school)
        mean_ses = Numeric('MeanSES', school)
        # school = Nominal('school').has(edu, ethnic, class_size)
        # Observation: Data schema contains so much information 

        # 4.4.1: "'SES' as a student-level explanatory variable"
        sm = ts.StatisticalModel(
            dv=math, # as DV, unit doesn't matter except that it wouldn't make sense to include IVs at a "lower" level than the dv?
            fixed_ivs=[ses], 
            random_slopes=None,
            random_intercepts=[(intercept, school)], # want random intercept in level 2
            interactions=None,
            # TODO: Ensure: want variance in Level 1 and Level 2 
            # no_intercept=True # TODO: Might be better to split into intercept=Levels(student, school, etc.)? -- what does glmer provide? 
        )

    # Example from Kreft & de Leeuw 1989, NELS-88 dataset
    def test_initialize_random_slope_10(self): 
        math = Numeric('MathAchievement', student) # interesting because no obvious unit, but probably student
        # Student-level variables 
        student = Nominal('id')
        ses = ('SES', student)
        hw = Numeric('HomeWork', student)
        race = ('Race', student)
        ped = ('ParentEducation', student)
        # student = Nominal('id').has(ses, hw, race)

        # School-level variables
        school = Nominal('school')
        sector = Nominal('Public', school) 
        ethnic = ('Percent-Minorities', school)
        class_size = ('Ratio', school)
        school_size = ('School Size', school)
        mean_ses = Numeric('MeanSES', school)
        # school = Nominal('school').has(edu, ethnic, class_size)
        # Observation: Data schema contains so much information 

        # 4.4.2: "Adding a random slope"
        sm = ts.StatisticalModel(
            dv=math, # as DV, unit doesn't matter except that it wouldn't make sense to include IVs at a "lower" level than the dv?
            fixed_ivs=None, 
            random_slopes=[(ses, school)],
            random_intercepts=[(intercept, school)], # want random intercept/'cons' in level 2
            interactions=None,
            # TODO: Ensure: want variance in Level 1 and Level 2 
            # no_intercept=True # TODO: Might be better to split into intercept=Levels(student, school, etc.)? -- what does glmer provide? 
        )
    
    # Example from Kreft & de Leeuw 1989, NELS-88 dataset
    def test_initialize_fixed_11(self): 
        math = Numeric('MathAchievement', student) # interesting because no obvious unit, but probably student
        # Student-level variables 
        student = Nominal('id')
        ses = ('SES', student)
        hw = Numeric('HomeWork', student)
        race = ('Race', student)
        ped = ('ParentEducation', student)
        # student = Nominal('id').has(ses, hw, race)

        # School-level variables
        school = Nominal('school')
        sector = Nominal('Public', school) 
        ethnic = ('Percent-Minorities', school)
        class_size = ('Ratio', school)
        school_size = ('School Size', school)
        mean_ses = Numeric('MeanSES', school)
        # school = Nominal('school').has(edu, ethnic, class_size)
        # Observation: Data schema contains so much information 

        # 4.4.3: "Adding 'PercentMinorities'""
        sm = ts.StatisticalModel(
            dv=math, # as DV, unit doesn't matter except that it wouldn't make sense to include IVs at a "lower" level than the dv?
            fixed_ivs=[ses, ethnic], 
            random_slopes=None,
            random_intercepts=[(intercept, school)], # want random intercept/'cons' in level 2
            interactions=None,
            # TODO: Ensure: want variance in Level 1 and Level 2 
            # no_intercept=True # TODO: Might be better to split into intercept=Levels(student, school, etc.)? -- what does glmer provide? 
        )

    # Example from Kreft & de Leeuw 1989, NELS-88 dataset
    def test_initialize_fixed_12(self): 
        math = Numeric('MathAchievement', student) # interesting because no obvious unit, but probably student
        # Student-level variables 
        student = Nominal('id')
        ses = ('SES', student)
        hw = Numeric('HomeWork', student)
        race = ('Race', student)
        ped = ('ParentEducation', student)
        # student = Nominal('id').has(ses, hw, race)

        # School-level variables
        school = Nominal('school')
        sector = Nominal('Public', school) 
        ethnic = ('Percent-Minorities', school)
        class_size = ('Ratio', school)
        school_size = ('School Size', school)
        mean_ses = Numeric('MeanSES', school)
        # school = Nominal('school').has(edu, ethnic, class_size)
        # Observation: Data schema contains so much information 

        # 4.4.4: "Adding 'MeanSES'""
        sm = ts.StatisticalModel(
            dv=math, # as DV, unit doesn't matter except that it wouldn't make sense to include IVs at a "lower" level than the dv?
            fixed_ivs=[ses, ethnic, mean_ses], 
            random_slopes=None,
            random_intercepts=[(intercept, school)], # want random intercept/'cons' in level 2
            interactions=None,
            # TODO: Ensure: want variance in Level 1 and Level 2 
            # no_intercept=True # TODO: Might be better to split into intercept=Levels(student, school, etc.)? -- what does glmer provide? 
        )

    # Example from Kreft & de Leeuw 1989, NELS-88 dataset
    # 4.5.1 Analysis with class size and a cross-level interaction
    def test_initialize_fixed_13(self): 
        math = Numeric('MathAchievement', student) # interesting because no obvious unit, but probably student
        # Student-level variables 
        student = Nominal('id')
        ses = ('SES', student)
        hw = Numeric('HomeWork', student)
        race = ('Race', student)
        ped = ('ParentEducation', student)
        # student = Nominal('id').has(ses, hw, race)

        # School-level variables
        school = Nominal('school')
        sector = Nominal('Public', school) 
        ethnic = ('Percent-Minorities', school)
        class_size = ('Ratio', school)
        school_size = ('School Size', school)
        mean_ses = Numeric('MeanSES', school)
        # school = Nominal('school').has(edu, ethnic, class_size)
        # Observation: Data schema contains so much information 

        # Pro: prioritize difference between random slope and random intercept
        # Pro: translation from Tisane SM to statsmodel or R is also clearer this way. 
        # Con: sources of variances are "hidden" because they are wrapped up/implied by the variables included in the random slopes/random intercepts
        sm = ts.StatisticalModel(
            dv=math, # as DV, unit doesn't matter except that it wouldn't make sense to include IVs at a "lower" level than the dv?
            fixed_ivs=[class_size], 
            random_slopes=[(hw, school)],
            random_intercepts=None, 
            interactions=None,
        )

        # Pro: priotizes/makes clear the source of explanation vs. variance (conceptually what's going on in a multilevel model)
        # Con: difficult, a bit awk? to differentiate between random slopes and random intercepts
        sm = ts.StatisticalModel(
            dv=math, 
            explanatory_ivs=[hw, class_size], # include interactions here
            variances=[ts.Variance(variable=hw, varies_within=school)]
            # variances=[ts.Variance(variable=hw, varies_within=school), ts.Variance(variable=student), ts.Variance(variable=school)], # student and school as units
            include_intercept=True, # Default: Intercept is always estimated
            intercept_variances=[ts.Unit(student), ts.Unit(school)] # Establish intercept variances at level of student and level of school, listed in order of level
        )

    # Example from Kreft & de Leeuw 1989, NELS-88 dataset
    # 4.5.2 Interaction between 'Ratio' and 'HomeWork'
    def test_initialize_fixed_13(self): 
        math = Numeric('MathAchievement', student) # interesting because no obvious unit, but probably student
        # Student-level variables 
        student = Nominal('id')
        ses = ('SES', student)
        hw = Numeric('HomeWork', student)
        race = ('Race', student)
        ped = ('ParentEducation', student)
        # student = Nominal('id').has(ses, hw, race)

        # School-level variables
        school = Nominal('school')
        sector = Nominal('Public', school) 
        ethnic = ('Percent-Minorities', school)
        class_size = ('Ratio', school)
        school_size = ('School Size', school)
        mean_ses = Numeric('MeanSES', school)
        # school = Nominal('school').has(edu, ethnic, class_size)
        # Observation: Data schema contains so much information 

        sm = ts.StatisticalModel(
            dv=math, # as DV, unit doesn't matter except that it wouldn't make sense to include IVs at a "lower" level than the dv?
            fixed_ivs=None, 
            random_slopes=[(hw, school)],
            random_intercepts=None, 
            interactions=[(class_size, hw)], # 4.5.2 creates and uses a new variable 'HomRatio'
        )

    def test_verify_(self): 
        # Determining the units seems to be a central part of study design specification
        # Unit = who/what the treatment applies to (in the case of experiment)
        # OR who/what the property or observation belongs to (in the case of
        # observational study)
        st = StudyDesign(
            ivs=[ts.IndependentVariable(variable=hw, unit=student), ts.IndependentVarible(variable=...)]
        )

    def test_verify_with_study_design_main_true(self): 
        expl = ts.Nominal('explanation type')
        acc = ts.Numeric('accuracy')
        participant = ts.Nominal('id')
        variables = [acc, expl, participant]

        sm = ts.StatisticalModel(
            dv=acc, 
            main_effects=[expl]
        )

        sd = ts.Design(
            dv = acc, 
            ivs = [expl.treat(participant)], # expl which was treated on participant
            groupings = None
        )

        verif = ts.verify(sm, sd)
        self.assertTrue(verif)

    def test_verify_with_study_design_main_false(self): 
        expl = ts.Nominal('explanation type')
        acc = ts.Numeric('accuracy')
        participant = ts.Nominal('id')
        variables = [acc, expl, participant]

        sm = ts.StatisticalModel(
            dv=acc, 
            main_effects=[expl, participant]
        )

        sd = ts.Design(
            dv = acc, 
            ivs = [expl.treat(participant)], # expl which was treated on participant
            groupings = None
        )

        verif = ts.verify(sm, sd)
        self.assertFalse(verif)

    def test_verify_with_study_design_interaction_true(self): 
        pass
    
    def test_verify_with_study_design_interaction_false(self): 
        pass
    
    def test_verify_with_study_design_random_slopes_true(self): 
        pass

    def test_verify_with_study_design_random_slopes_false(self): 
        pass

    def test_verify_with_study_design_random_intercepts_true(self): 
        pos_aff = ts.Numeric('Positive Affect')
        es = ts.Numeric('Emotional Suppression')
        cr = ts.Numeric('Cognitive Reappraisal')
        gender = ts.Numeric('Gender')
        age = ts.Numeric('Age')
        time = ts.Numeric('Hours since 7am')
        participant = ts.Nominal('participant')
        variables = [pos_aff, es, cr, gender, age, time, participant]

        sm = ts.StatisticalModel(
            dv=pos_aff,
            main_effects=[es, cr, age, gender, time],
            interaction_effects=[(es, time), (cr, time)],
            random_intercepts=[(participant)] # how to include as a random variable?   
        )

        sd = ts.Design(
            dv=pos_aff,
            ivs=[es, cr, age, gender, time],
            groupings=[participant.repeat(pos_aff, 12)] # the 12 should really be the cardinality of time
        )

        verif = ts.verify(sm, sd)
        self.assertTrue(verif)

    def test_verify_with_study_design_random_intercepts_false(self): 
        pass