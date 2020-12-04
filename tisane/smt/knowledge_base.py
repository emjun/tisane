from tisane.smt.statistical_model import StatisticalModel
from tisane.smt.property import *

""" Properties 
data_type(v, type): 
"""

# TODO: Does it make sense for initialize_all_properties() to be in smt.property or here? 

class KnowledgeBase(object):
    all_stat_models: list
    all_properties: dict
    
    def __init__(self, ivs: list, dvs: list): 
        self.all_stat_models = list()

        self.all_properties = initialize_all_properties(ivs, dvs)
        
        self.initialize_all_stat_models(ivs, dvs)

    def initialize_all_stat_models(self, ivs: list, dvs: list):
        
        self.all_stat_models.append(
            StatisticalModel(
                name='Multiple Linear Regression', 
                properties=[
                    self.all_properties['numeric_dv']
                ]))

    # Instantiate models with specific @param ivs and @param dvs
    def apply_vars(self, ivs: list, dvs: list):
        assert(len(dvs) == 1) # there is only one DV
        for m in self.all_stat_models: 
            m.__apply(ivs=ivs, dvs=dvs)

    # Look up something in the knowledge base (should support dual sided reasoning eventually)
    def query(self): 
        pass

"""
pearson_corr = StatisticalTest('pearson_corr', [x0, x1],
                                        test_properties=
                                        [bivariate],
                                        properties_for_vars={
                                            continuous: [[x0], [x1]],
                                            normal: [[x0], [x1]]
                                        })
"""