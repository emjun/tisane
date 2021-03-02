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