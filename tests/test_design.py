from tisane import *

import unittest

class DesignTest(unittest.TestCase): 
    def test_design_vis(self): 
        student_id = Numeric('student_id')
        sat_score = Numeric('sat_score')
        tutoring = Nominal('tutoring', cardinality=2) # Categorical('tutoring')
        
        design = Design(dv = sat_score)
        design.treat(student_id, tutoring, times=1)
        
        design.visualize_design() 