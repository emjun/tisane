import tisane as ts 

import unittest 

class KreftDeLeeuwExamples(unittest.TestCase): 

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

