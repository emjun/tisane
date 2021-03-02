import tisane as ts
from tisane.variable import Treatment, Nest, RepeatedMeasure

import unittest

class CCWATest(unittest.TestCase): 
    # Chapter 14.8
    def multilevel_interaction(self): 
        diet_prog = ts.Nominal('diet program')
        group = ts.Nominal('group') 
        motivation = ts.Ordinal('motivation', order=['low', 'medium', 'high']) # applies to individual 
        pounds_lost = ts.Numeric('weight loss')

        # Pounds_lost ~ diet_prog + motivation + diet_prog*motivation
        # ``Interaction'' (for motivation diet_prog) added interactively
        design = ts.Design(
            dv=pounds_lost, 
            ivs=[diet_prog.treat(group), motivation], # diet_prog as fixed_effect
            groupings=[motivation.nested_under(group)] # random slope for motivation
        ) # Pounds_lost = Diet_prog + Motivation; Can add Diet_prog*Motivation during interaction loop

        
        # design = ts.Design(
        #     dv=pounds_lost, 
        #     ivs=[diet_prog.treat(group), motivation], # How would "has" translate/apply to group? - use instead of Treatment?
        #     groupings=[motivation.nested_under(group)] # looks weird -- maybe have some notion of individual.nested_under(group), individual.has(motivation)?
        # ) # Pounds_lost = Diet_prog + Motivation; Can add Diet_prog*Motivation during interaction loop

        sm = ts.synthesize_statistical_model(design=design)

        print(sm.mathematize())

    # TODO: QUESTION
    # If data is nested, cannot treat units as a random intercept only (by design)
    def random_intercept_only(self):
        # Chapter 14.5
        diet_prog = ts.Nominal('diet program')
        group = ts.Nominal('group') 
        motivation = ts.Ordinal('motivation', order=['low', 'medium', 'high']) # applies to individual 
        pounds_lost = ts.Numeric('weight loss')

        design = ts.Design(
            dv=pounds_lost, 
            ivs=[motivation, group], # group as random intercept
            groupings=[motivation.nested_under(group)] # motivation as random slope
        ) 

        sm = ts.synthesize_statistical_model(design=design)

        print(sm.mathematize())

    # TODO: QUESTION
    def force_random_intercept_only(self):
        # Chapter 14.5
        diet_prog = ts.Nominal('diet program')
        group = ts.Nominal('group') 
        motivation = ts.Ordinal('motivation', order=['low', 'medium', 'high']) # applies to individual 
        pounds_lost = ts.Numeric('weight loss')

        design = ts.Design(
            dv=pounds_lost, 
            ivs=[motivation, group], # group as fixed effect, motivation as fixed effect
            groupings=[] 
        ) 

        sm = ts.synthesize_statistical_model(design=design)

        print(sm.mathematize())

        ## QUESTION: How evident should random slope vs. random intercept be from syntax of Study Design?
        # Seems more like a modeling decision, which could be elicited during the synthesis step.
        # If so, then detection algorithm:
        # Any nested, could be random slope or random intercept
        # If unit (e.g., motivation) is included as iv, know random intercept
        # If group (e.g., group) is included as iv, fixed effect
        # For each ``grouping,'' ask if random slope for unit (e.g., interaction)

        # Any repeated, could be random slope or random intercept?


        # More examples from outside CCWA?

        def test_lmer_example(self): 
            classroom = Nominal('class') # Unit('class')
            pupil = Nominal('pupil')
            extrav = Numeric('extraversion')
            sex = Nominal('sex')
            popularity = Numeric('popularity')
            texp = Numeric('teacher experience')

            design = ts.Design(
                dv=popularity, 
                ivs=[], 
                groupings=[]
            )

            # Associate unit with observation
            pupil.has(sex) #--> unit of observation in ctor: pupil = Nominal('pupil', is_unit=True) | pupil=Unit('pupil') (syntactic sugar for former & unit must be nominal), sex=Nominal('sex', unit=pupil) -- forces to declare units ahead of time
            pupil.has(extrav)
            classroom.has(texp)
            # Specify how units are related to one another
            pupil.nest_under(classroom)

            # popular ~ 1 + (1|class)
            ivs=[classroom], # 'group' as IV (without nest_under declaration below, would treat as fixed effect)
            groupings=[pupil.nest_under(classroom)] # Add classroom as random intercept
            
            # popular ~ 1 + sex + extrav + (1|class)
            ivs=[classroom, sex, extrav]
            groupings=[pupil.nest_under(classroom)] # Don't add pupil, but if know that classrom (in iv) is a grouping factor, add random intercept
            
            # popular ~ 1 + sex + extrav + texp + (1 | class)
            ivs=[classroom, sex, extrav, texp]
            groupings=[pupil.nest_under(classroom)] # Don't add pupil, but if know that classrom (in iv) is a grouping factor, add random intercept

            # popular ~ 1 + sex + extrav + texp + (1 + sex + extrav | class)
            ivs=[classroom, sex, extrav, texp] # fixed effects
            groupings=[sex.nest_under(classroom), extrav.nest_under(classroom)] # random slopes


            random intercept: in IV + group 
            random slope: in IV + unit
            cross-level interaction: in IV, unit --> ask about interaction (random intercept and slope)
            # unit have random slope + random intercept
            # group can oly have random intercept?



        (1|group) = random intercept
        # DOING: Synth:Design -> Model
        # TODO: Verify design + model 
        # Use this example as one to walk through nuances in advising meeting?
