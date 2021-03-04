import tisane as ts
from tisane.variable import Treatment, Nest, RepeatedMeasure

import unittest

class VerifyTest(unittest.TestCase): 
    
    # Sound
    def test_verify_design_and_conceptual_model_1(self): 
        classroom = ts.Nominal('class')
        pupil = ts.Nominal('pupil')
        extrav = ts.Numeric('extraversion')
        sex = ts.Nominal('sex')
        popularity = ts.Numeric('popularity')
        texp = ts.Numeric('teacher experience')

        design = ts.Design(
            dv=popularity, 
            ivs=[classroom, sex, extrav, texp], # fixed effects
            groupings=[sex.nested_under(classroom), extrav.nested_under(classroom)] # random slopes
        )

        cm = ts.ConceptualModel(
            associative_relationships=[sex.associate(popularity), extrav.associate(popularity), texp.associate(popularity)]
        )

        verif = ts.verify(design, cm)
        self.assertTrue(verif)

    # but not complete
    #  Summary: If study design does not address ''extraneous'' relationships in
    #  the conceptual model, verify will return False. 
    def test_verify_design_and_conceptual_model_2(self): 
        classroom = ts.Nominal('class')
        pupil = ts.Nominal('pupil')
        extrav = ts.Numeric('extraversion')
        sex = ts.Nominal('sex')
        popularity = ts.Numeric('popularity')
        texp = ts.Numeric('teacher experience')

        design = ts.Design(
            dv=popularity, 
            ivs=[classroom, sex, extrav, texp], # fixed effects
            groupings=[sex.nested_under(classroom), extrav.nested_under(classroom)] # random slopes
        )

        cm = ts.ConceptualModel(
            associative_relationships=[sex.associate(popularity), extrav.associate(popularity), texp.associate(popularity), sex.associate(extrav)]
        )

        verif = ts.verify(design, cm)
        self.assertFalse(verif)

    # Sound 
    def test_verify_statistical_model_and_conceptual_model_1(self): 
        classroom = ts.Nominal('class')
        pupil = ts.Nominal('pupil')
        extrav = ts.Numeric('extraversion')
        sex = ts.Nominal('sex')
        popularity = ts.Numeric('popularity')
        texp = ts.Numeric('teacher experience')

        cm = ts.ConceptualModel(
            associative_relationships=[sex.associate(popularity), extrav.associate(popularity), texp.associate(popularity), sex.associate(extrav)]
        )

        sm = ts.StatisticalModel(
            dv=popularity, 
            main_effects=[sex, extrav, texp], 
            interaction_effects=[(sex, extrav)], 
            mixed_effects=[], 
            link_func='identity', 
            variance_func='normal'
        ) 

        verif = ts.verify(cm, sm)
        self.assertTrue(verif)

    # but not complete 
    # Summary: If conceptual model contains relationship between two
    # variables, but an interaction is not introduced, then returns False
    def test_verify_statistical_model_and_conceptual_model_2(self): 
        classroom = ts.Nominal('class')
        pupil = ts.Nominal('pupil')
        extrav = ts.Numeric('extraversion')
        sex = ts.Nominal('sex')
        popularity = ts.Numeric('popularity')
        texp = ts.Numeric('teacher experience')

        cm = ts.ConceptualModel(
            associative_relationships=[sex.associate(popularity), extrav.associate(popularity), texp.associate(popularity), sex.associate(extrav)]
        )

        sm = ts.StatisticalModel(
            dv=popularity, 
            main_effects=[sex, extrav, texp], 
            interaction_effects=[], 
            mixed_effects=[], 
            link_func='identity', 
            variance_func='normal'
        ) 

        verif = ts.verify(cm, sm)
        self.assertFalse(verif)

    # Sound
    def test_study_design_and_statistical_model_1(self): 
        pass

    # but not complete
    def test_study_design_and_statistical_model_2(self): 
        pass