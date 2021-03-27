import tisane as ts
from tisane.code_generator import *

from z3 import *
import pandas as pd
import numpy as np
import random
import unittest

random.seed(2)

def absolute_path(p: str) -> str:
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), p)

class TestCodeGeneration(unittest.TestCase): 
    def test_generate_slinear(self): 
        math = ts.Numeric('MathAchievement')
        # Student-level variables 
        student = ts.Nominal('id')
        hw = ts.Numeric('HomeWork')
        race = ts.Nominal('Race')

        sm = ts.StatisticalModel(
            dv=math,
            fixed_ivs=[hw], 
            random_ivs=None, 
            interactions=None,
            family='Gaussian', 
            link_function='Identity'
        ).assign_data(DataForTests.df)
        
        tests_path = absolute_path('generated_code/')
        file_path = os.path.join(tests_path, 'slm_model.py')
        script = generate_code(sm, file_path=file_path)
        
        # Add test case about script that is generated.
        with open(script, 'r') as f: 
            pass
        
    def test_generate_mlinear(self): 
        math = ts.Numeric('MathAchievement')
        # Student-level variables 
        student = ts.Nominal('id')
        hw = ts.Numeric('HomeWork')
        ses = ts.Numeric('SES')
        race = ts.Nominal('Race')

        sm = ts.StatisticalModel(
            dv=math,
            fixed_ivs=[hw, ses], 
            random_ivs=None, 
            interactions=None,
            family='Gaussian', 
            link_function='Identity'
        ).assign_data(DataForTests.df)

        # script = generate_statsmodel_code(sm, file_name='mlr_model.py')
        tests_path = absolute_path('generated_code/')
        file_path = os.path.join(tests_path, 'mlm_model.py')
        script = generate_code(sm, file_path=file_path)
        
        # Add test case about script that is generated.
        with open(script, 'r') as f: 
            pass
        
    def test_generate_mlinear_with_interaction(self): 
        math = ts.Numeric('MathAchievement')
        # Student-level variables 
        student = ts.Nominal('id')
        hw = ts.Numeric('HomeWork')
        ses = ts.Numeric('SES')
        race = ts.Nominal('Race')

        sm = ts.StatisticalModel(
            dv=math,
            fixed_ivs=[hw, ses, race], 
            random_ivs=None, 
            interactions=[(hw, race)],
            family='Gaussian', 
            link_function='Identity'
        ).assign_data(DataForTests.df)

        # script = generate_statsmodel_code(sm, file_name='mlr_interaction_model.py')
        tests_path = absolute_path('generated_code/')
        file_path = os.path.join(tests_path, 'mlm_interaction_model.py')
        script = generate_code(sm, file_path=file_path)
        
        # Add test case about script that is generated.
        with open(script, 'r') as f: 
            pass

class DataForTests(): 
    def random_float_list(lb: int, ub: int, num: int): 
        rlist = list() 

        for i in range(num): 
            val = ub*random.random() + lb
            rlist.append(val)
        
        assert(len(rlist) == num)
        return rlist

    math = random_float_list(lb=0, ub=101, num=50)
    race = random.choices(['White', 'Hispanic', 'Black', 'Asian', 'Indigenous'], k=50)
    df =  pd.DataFrame({
                'MathAchievement': math,
                'HomeWork': np.random.randint(0, 24, 50),
                'SES': np.random.randint(10000, 150000, 50),
                'Race': race
                # 'SES': ,
                # 'MeanSES': 
    })