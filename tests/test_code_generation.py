import tisane as ts
from tisane.code_generator import *

from z3 import *
import pandas as pd
import numpy as np
import unittest

class TestCodeGeneration(unittest.TestCase): 
    def test_generate_slr(self): 
        math = ts.Numeric('MathAchievement')
        # Student-level variables 
        student = ts.Nominal('id')
        hw = ts.Numeric('HomeWork')
        race = ts.Nominal('Race')

        df =  pd.DataFrame({
                'MathAchievement': np.random.randn(50),
                'HomeWork': np.random.randn(50)+1},
                # 'Race': ,
                # 'SES': ,
                # 'MeanSES': 
            )

        sm = ts.StatisticalModel(
            dv=math,
            fixed_ivs=[hw], 
            random_ivs=None, 
            interactions=None
        ).assign_data(df)
        
        script = generate_statsmodel_code(sm)
        
        # Add test case about script that is generated.
        with open(script, 'r') as f: 
            pass
        
    def test_generate_mlr(self): 
        math = ts.Numeric('MathAchievement')
        # Student-level variables 
        student = ts.Nominal('id')
        hw = ts.Numeric('HomeWork')
        race = ts.Nominal('Race')

        sm = ts.StatisticalModel(
            dv=math,
            fixed_ivs=[hw, race], 
            random_ivs=None, 
            interactions=None
        )

    def test_generate_slr_with_interaction(self): 
        pass

    def test_generate_mlr_with_interaction(self): 
        pass
