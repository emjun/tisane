import tisane as ts 

import unittest

class SynthesizerTest(unittest.TestCase): 
    
    def test_one_level_fixed(self): 
        """
        Example from Bansal et al. CHI 2021
        """
        acc = ts.Numeric('accuracy')
        expl = ts.Nominal('explanation type')
        variables = [acc, expl]

        design = ts.Design(
            dv = acc, 
            ivs = ts.Level(identifier='id', measures=[expl])
        )

        ts.synthesize_statistical_model(design=design)