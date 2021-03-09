import tisane as ts 

import unittest 

        # Variables
        # Tisane Statistical Model 
        # LMER R formula
        # Statsmodels formula/function call 
        # Tisane Study Design 
        # Tisane Conceptual Model

class KreftDeLeeuwExamples(unittest.TestCase): 
    """
    Examples from Chapter 4 of Kreft & de Leeu 1989 ''Introducing Multilevel Modeling''
    Dataset: NELS-8 dataset
    """

    # 4.1.2: "The organizaiton of the four sessions"
    def test_initialize_null_model(self): 
        # Variables
        math = Numeric('MathAchievement')
        student = Nominal('id')
        school = Nominal('school')

        # Tisane Statistical Model
        # Assumption that math is at the 'student' level 
        sm = ts.StatisticalModel(
            dv=math, # assumed to be student level
            fixed_ivs=None, # could be 'main_effects' instead?
            interactions=None,
            random_slopes=None, 
            random_intercepts=[school], # Establish intercept variances at level of student and level of school
            # no_intercept=True # An option? By default Intercept is always estimated
        )

        # LMER R formula
        # math ~ (1|school)

        # TODO: Statsmodels formula/function call 
        
        # Tisane Study Design 
        sd = Design(
            dv=math.unit(student), 
            ivs=[student, school],
            groupings=[student.nest_under(school)]
        )

        sd = ts.Design(
            dv=math,
            ivs=
                ts.Level(id=student, measures=None).nest_under(
                ts.Level(id=school, measures=None))
        )

        # Tisane Conceptual Model 
        student.associate(math)
        school.associate(math)
        student.nest_under(group) # TODO: Add this construct in the conceptual model?


    # 4.2.3 'HomeWork' and 'MathAchievement'
    def test_initialize_fixed_1(self): 
        # Variables
        math = Numeric('MathAchievement')
        # Student-level variables 
        student = Nominal('id')
        hw = Numeric('HomeWork', student)

        # School-level variables
        school = Nominal('school')
        
        # Tisane Statistical Model 
        sm = ts.StatisticalModel(
            dv=math,
            fixed_ivs=[hw],
            interactions=None, 
            random_slopes=None, 
            random_intercepts=[school]
        )

        # LMER R formula
        # math ~ hw
        
        # TODO: Statsmodels formula/function call 

        # Tisane Study Design 
        sd = ts.Design(
            dv=math, 
            ivs=[hw.unit(student), student, school],
            groupings=[student.nest_under(school)]
        )

        # Tisane Conceptual Model
        student.associate(math)
        school.associate(math)
        hw.associate(math)
        student.nest_under(group) # TODO: Add this construct in the conceptual model?

    # 4.2.4 Random slope for 'HomeWork'
    def test_initialize_random_slope_1(self): 
        # Variables
        math = Numeric('MathAchievement')
        # Student-level variables 
        student = Nominal('id')
        hw = Numeric('HomeWork')

        # School-level variables
        school = Nominal('school')
        
        # Tisane Statistical Model 
        sm = ts.StatisticalModel(
            dv=math, 
            fixed_ivs=None, 
            interactions=None,
            random_slopes=[(hw, school)], # random slope for homework within each school
            random_intercepts=None
        )

        # LMER R formula
        # math ~ (0 + hw|school)
        
        # TODO: Statsmodels formula/function call 

        # Tisane Study Design 
        sd = ts.Design(
            dv=math, 
            ivs=[hw.unit(student), student, school],
            groupings=[student.nest_under(school)]
        )

        # Tisane Conceptual Model
        student.associate(math)
        school.associate(math)
        hw.associate(math)
        student.nest_under(group) # TODO: Add this construct in the conceptual model?

        
    # 4.2.5 Adding 'ParentEducation'
    def test_initialize_random_slope_fixed_1(self): 
        # Variables
        math = Numeric('MathAchievement') # interesting because no obvious unit, but probably student
        # Student-level variables 
        student = Nominal('id')
        hw = Numeric('HomeWork')
        ped = Nominal('ParentEducation')
        # School-level variables
        school = Nominal('school')

        # Tisane Statistical Model 
        sm = ts.StatisticalModel(
            dv=math, 
            fixed_ivs=[ped], 
            interactions=None,
            random_slopes=[(hw, school)], 
            random_intercepts=None
        )

        # LMER R formula
        # math ~ ped + (0 + hw|school) # correlated random intercept and slope

        # TODO: Statsmodels formula/function call 
        
        # Tisane Study Design 
        sd = ts.Design(
            dv=math, 
            ivs=[hw.unit(student), ped.unit(student), student, school],
            groupings=[student.nest_under(school)]
        )

        # Tisane Conceptual Model
        student.associate(math)
        school.associate(math)
        hw.associate(math)
        ped.associate(math)
        student.nested_in(group) # TODO: Add this construct in the conceptual model?
        # TODO: Add hw.from(student), ped.from(student) or something like that?


    # 4.2.6 Traditional regresion analysis 
    # NOTE: This IGNORES the nesting nature of the data and would be "incorrect"
    def test_regression(self): 
        math = Numeric('MathAchievement', student)
        # Variables
        student = Nominal('id')
        hw = Numeric('HomeWork', student)
        ped = ('ParentEducation', student)

        # Tisane Statistical Model 
        sm = ts.StatisticalModel(
            dv=math, 
            fixed_ivs=[hw, ped],
            interactions=None, 
            random_slopes=None, 
            random_intercepts=None
        )

        # LMER R formula
        # math ~ hw + ped

        # TODO: Statsmodels formula/function call 
        
        # Tisane Study Design 
        sd = ts.Design(
            dv=math, 
            ivs=[hw.unit(student), ped.unit(student)],
            groupings=None # Note: The end-user omitted the student.nest_under(school), which causes this to be a traditional regression analysis
        )

        # Tisane Conceptual Model
        student.associate(math)
        school.associate(math)
        hw.associate(math)
        ped.associate(math)
        student.nested_in(group) # TODO: Add this construct in the conceptual model?

    # 4.3.2 A model with 'SchoolSize'
    def test_initialize_random_slope_fixed_2(self): 
        # Variables
        math = Numeric('MathAchievement', student) # interesting because no obvious unit, but probably student
        # Student-level variables 
        student = Nominal('id')
        hw = Numeric('HomeWork', student)
        # School-level variables
        school = Nominal('school')
        school_size = ('School Size', school)

        # Tisane Statistical Model 
        sm = ts.StatisticalModel(
            dv=math,
            fixed_ivs=[school_size], 
            random_slopes=[(hw, school)], # random slope for homework within each school
            random_intercepts=None
            # no_intercept=True # An option? By default Intercept is always estimated
        )

        # LMER R formula
        # math ~ school_size + (0 + hw|school)

        # TODO: Statsmodels formula/function call 

        # Tisane Study Design 
        sd = ts.Design(
            dv=math, 
            ivs=[hw.unit(student), school_size.unit(school)],
            groupings=[student.nest_under(school)]
        )

        # Tisane Conceptual Model
        student.associate(math)
        school.associate(math)
        hw.associate(math)
        school_size.associate(math)
        student.nested_in(group) # TODO: Add this construct in the conceptual model?


    # 4.3.3 Changing 'SchoolSize' to 'Public'
    def test_initialize_random_slope_fixed_2(self): 
        # Variables
        math = Numeric('MathAchievement') # interesting because no obvious unit, but probably student
        # Student-level variables 
        student = Nominal('id')
        hw = Numeric('HomeWork')
        # School-level variables
        school = Nominal('school')
        sector = Nominal('Public') 

        # Tisane Statistical Model 
        sm = ts.StatisticalModel(
            dv=math, # as DV, unit doesn't matter except that it wouldn't make sense to include IVs at a "lower" level than the dv?
            fixed_ivs=[sector], 
            random_slopes=[(hw, school)], 
            random_intercepts=None
        )

        # LMER R formula
        # math ~ sector + (0 + hw|school)

        # TODO: Statsmodels formula/function call 
        
        # Tisane Study Design 
        sd = ts.Design(
            dv=math, 
            ivs=[hw.unit(student), sector.unit(school)],
            groupings=[student.nest_under(school)]
        )

        # Tisane Conceptual Model
        student.associate(math)
        school.associate(math)
        hw.associate(math)
        sector.associate(math)

    # 4.3.4 Adding a cross-level interaction with 'Public'
    def test_initialize_random_slope_fixed_crossed_1(self): 
        # Variables
        math = Numeric('MathAchievement', student) # interesting because no obvious unit, but probably student
        # Student-level variables 
        student = Nominal('id')
        hw = Numeric('HomeWork')
        # School-level variables
        school = Nominal('school')
        sector = Nominal('Public', school) 

        # Tisane Statistical Model 
        # Focus is on effects structure
        sm = ts.StatisticalModel(
            dv=math, 
            fixed_ivs=[sector], 
            random_slopes=[(hw, school)], 
            random_intercepts=None,
            interactions=[(sector, hw)] # Note: From interaction
        )

        # TODO: Syntactic alternative for SM OR SD???
        sm = ts.StatisticalModel(
            dv=math,
            individual_ivs=[
                ts.Level(unit=student, fixed=None, random_slope=[hw], random_intercetp=[hw]),
                ts.Level(unit=school, fixed=[sector], random_slope=None, random_intercept=None) # random_slope and random_intercept are none for highest/last Level
            ]
            interactions=[(sector, hw)]
        )

        # LMER R formula
        # math ~ sector*hw + (0 + hw|school) == math ~ sector + hw + sector:hw + (0 + hw|school)

        # TODO: Statsmodels formula/function call 
        
        # Tisane Study Design 
        sd = ts.Design(
            dv=math, 
            ivs=[hw.unit(student), sector.unit(school)], 
            groupings=[student.nest_under(school)]
        )

        # Syntactic alternative: Focus is on measurement struture
        sm = ts.Design(
            dv=math,
            ivs=
                ts.Level(id=student, measures=[hw]).nest_under(
                ts.Level(id=school, measures=[sector]))
        )

        # Tisane Conceptual Model
        student.associate(math)
        school.associate(math)
        hw.associate(math)
        sector.associate(math)

    # 4.3.6 Deleting 'HomePublic' and adding 'White' using the small data set again
    def test_initialize_random_slope_fixed_3(self): 
        # Variables
        math = Numeric('MathAchievement', student) # interesting because no obvious unit, but probably student
        # Student-level variables 
        student = Nominal('id')
        hw = Numeric('HomeWork', student)
        race = ('Race', student)
        # School-level variables
        school = Nominal('school')
        sector = Nominal('Public', school) 

        # Tisane Statistical Model 
        sm = ts.StatisticalModel(
            dv=math, # as DV, unit doesn't matter except that it wouldn't make sense to include IVs at a "lower" level than the dv?
            fixed_ivs=[sector, race], 
            random_slopes=[(hw, school)], 
            random_intercepts=None,
            interactions=None,
            # no_intercept=True # An option? By default Intercept is always estimated
        )

        # LMER R formula
        # math ~ sector + race + (0 + hw|school)

        # TODO: Statsmodels formula/function call 

        # Tisane Study Design 
        sd = ts.Design(
            dv=math, 
            ivs=ts.Level(id=student, measures=[hw, race]).nest_under(
                ts.Level(id=school, measures=[sector]))
        )

        # TODO: Tisane Conceptual Model

    
    # 4.3.7 Adding a random part for 'White'
    def test_initialize_random_slope_fixed_4(self): 
        # Variables
        math = Numeric('MathAchievement', student) # interesting because no obvious unit, but probably student
        # Student-level variables 
        student = Nominal('id')
        ses = ('SES', student)
        hw = Numeric('HomeWork', student)
        race = ('Race', student)
        ped = ('ParentEducation', student)

        # School-level variables
        school = Nominal('school')
        sector = Nominal('Public', school) 
        ethnic = ('Percent-Minorities', school)
        class_size = ('Ratio', school)
        school_size = ('School Size', school)
        # school = Nominal('school').has(edu, ethnic, class_size)
        # Observation: Data schema contains so much information 

        # Tisane Statistical Model 
        sm = ts.StatisticalModel(
            dv=math, # as DV, unit doesn't matter except that it wouldn't make sense to include IVs at a "lower" level than the dv?
            fixed_ivs=[sector], 
            random_slopes=[(hw, school), (race, school)],
            random_intercepts=None,
            interactions=None,
            # no_intercept=True # An option? By default Intercept is always estimated
        )

        # LMER R formula
        # math ~ sector + (0 + hw|school) + (0 + race|school)

        # TODO: Statsmodels formula/function call 

        # Tisane Study Design 
        sd = ts.Design(
            dv=math, 
            ivs=
                ts.Level(id=student, measures=[hw, race]).nest_under(
                ts.Level(id=school, measures=[sector]))
        )

        # TODO: Tisane Conceptual Model
    
    # 4.3.8: Making the coefficient of 'White' fixed and adding 'MeanSES'
    def test_initialize_random_slope_fixed_5(self): 
        # Variables
        math = Numeric('MathAchievement')
        # Student-level variables 
        student = Nominal('id')
        hw = Numeric('HomeWork')
        race = ('Race')
        # School-level variables
        school = Nominal('school')
        sector = Nominal('Public')
        mean_ses = Numeric('MeanSES')

        # Tisane Statistical Model 
        sm = ts.StatisticalModel(
            dv=math,
            fixed_ivs=[sector, race, mean_ses], 
            random_slopes=[(hw, school)], 
            random_intercepts=None,
            interactions=None
        )

        # LMER R formula
        # math ~ sector + race + mean_ses + (0 + hw|school)

        # TODO: Statsmodels formula/function call 

        # Tisane Study Design 
        sd = ts.Design(
            dv=math, 
            ivs=ts.Level(id=student, measures=[hw, race]).nest_under(
                ts.Level(id=school, measures=[sector, mean_ses]),
            # data=data if there is data
            )
        )

        # TODO: Tisane Conceptual Model

    # 4.3.9 Deleting the school characteristic 'Public'
    def test_initialize_random_slope_fixed_6(self): 
        # Variables 
        math = Numeric('MathAchievement')
        # Student-level variables 
        student = Nominal('id')
        hw = Numeric('HomeWork')
        race = ('Race', student)
        # School-level variables
        school = Nominal('school')
        mean_ses = Numeric('MeanSES')

        # Tisane Statistical Model
        sm = ts.StatisticalModel(
            dv=math, # as DV, unit doesn't matter except that it wouldn't make sense to include IVs at a "lower" level than the dv?
            fixed_ivs=[race, mean_ses], 
            random_slopes=[(hw, school)], 
            random_intercepts=None,
            interactions=None,
            # no_intercept=True # An option? By default Intercept is always estimated
        )

        # LMER R formula
        # math ~ race + mean_ses + (0 + hw|school)

        # TODO: Statsmodels formula/function call 
        
        # Tisane Study Design 
        sd = ts.Design(
            dv=math, 
            ivs=ts.Level(id=student, measures=[race, hw]).nest_under(
                ts.level(id=school, measures=[mean_ses]))
        )
        
        # TODO: Tisane Conceptual Model

    # 4.3.10 Adding an Interaction between 'HomeWork' and 'MeanSES'
    def test_initialize_random_slope_fixed_7(self): 
        # Variables
        math = Numeric('MathAchievement', student) # interesting because no obvious unit, but probably student
        # Student-level variables 
        student = Nominal('id')
        hw = Numeric('HomeWork', student)
        race = ('Race', student)

        # School-level variables
        school = Nominal('school')
        mean_ses = Numeric('MeanSES', school)

        # Tisane Statistical Model
        sm = ts.StatisticalModel(
            dv=math,
            fixed_ivs=[race, mean_ses], 
            random_slopes=[(hw, school)], 
            random_intercepts=None,
            interactions=[(hw, mean_ses)], # 4.3.10 uses an interaction variable named "HomeSES"
        )

        sm = ts.StatisticalModel(
            dv=math, 
            fixed_ivs=[ts.FixedVariable(race), ts.FixedVaraible(mean_ses)],
            random_ivs=[ts.RandomSlope(slope_for_each=hw, slopes_vary_among=school), 
                        ts.RandomIntercept(intercept_for_each=hw, intercepts_vary_among=school)],
            interaction_ivs=[ts.Interaction(hw, mean_ses)]
        )

        sm = ts.StatisticalModel(
            dv=math, 
            ivs=[   ts.FixedVariable(race), 
                    ts.FixedVaraible(mean_ses),
                    ts.RandomSlope(slope_for_each=hw, slopes_vary_among=school), 
                    ts.RandomIntercept(intercept_for_each=hw, intercepts_vary_among=school),
                    ts.Interaction(hw, mean_ses)
            ]
        )

        # LMER R formula
        # math ~ race + mean_ses + (0+hw|school) + hw*mean_ses

        # TODO: Statsmodels formula/function call 

        # Tisane Study Design 
        sd = ts.Design(
            dv=math, 
            ivs=ts.Level(id=student, measures=[race, hw]).nest_under(
                ts.Level(id=school, measures=[mean_ses])
            )
        )

        # TODO: Tisane Conceptual Model

    # 4.3.11 Adding another student-level variable
    def test_initialize_random_slope_fixed_8(self): 
        # Variables
        math = Numeric('MathAchievement')
        # Student-level variables 
        student = Nominal('id')
        ses = ('SES', student)
        hw = Numeric('HomeWork', student)
        race = ('Race', student)
        # School-level variables
        school = Nominal('school')
        sector = Nominal('Public', school) 

        # Tisane Statistical Model 
        sm = ts.StatisticalModel(
            dv=math,
            fixed_ivs=[race, ses, sector], 
            random_slopes=[(hw, school)], 
            random_intercepts=None,
            interactions=None, 
        )

        # LMER R formula
        # math ~ race + ses + sector + (0 + hw | school)

        # TODO: Statsmodels formula/function call 

        # Tisane Study Design 
        sd = ts.Design(
            dv=math, 
            ivs=ts.Level(id=student, measures=[ses, hw, race]).nest_under(
                ts.Level(id=school, measures=[sector])
            )
        )
        
        # TODO: Tisane Conceptual Model

    # TODO: START HERE! Example from Kreft & de Leeuw 1989, NELS-88 dataset
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

