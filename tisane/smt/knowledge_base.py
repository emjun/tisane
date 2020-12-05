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
                name='Linear Regression', 
                properties=[
                    self.all_properties['numeric_dv'],
                    self.all_properties['residual_normal_distribution']
                ]))

        self.all_stat_models.append(
            StatisticalModel(
                name='Logistic Regression',
                properties=[
                    # TODO: create binary_dv
                    # self.all_properties['binary_dv']
                ]
            )
        )

    # Instantiate models with specific @param ivs and @param dvs
    def apply_vars(self, ivs: list, dvs: list):
        assert(len(dvs) == 1) # there is only one DV
        for m in self.all_stat_models: 
            m.__apply(ivs=ivs, dvs=dvs)

    # Adds assertions to the knowledge base that are used for solving for a query
    def add_assertions(self, assertions: list): 
        raise NotImplementedError

    # Generic for looking up something in the knowledge base (should support dual sided reasoning eventually)
    def query(self, ivs: list, dvs: list): 
        pass

    # Concepts -> Models
    # Look up statistical models 
    def find_statistical_models(self, ivs: list, dvs: list, **kwargs) -> List[StatisticalModel]: 
        # TODO what happens if kwargs does not have an 'assertions' keyword?
        assertions = kwargs['assertions']
        self.add_assertions(assertions)

        # TODO: SOLVE

        return 99

    # Models -> Concepts
    def find_conceptual_models(self, stat_models: list):
        # TODO: Translate stat_models into (set of) assertions
        assertions = None

        self.add_assertions(assertions)

        # TODO: SOLVE 

        return -99 

# Concepts -> Models
# Look up statistical models 
def find_statistical_models(ivs: list, dvs: list, **kwargs): 
    kb = KnowledgeBase(ivs=ivs, dvs=dvs)

    return kb.find_statistical_models(ivs=ivs, dvs=dvs, **kwargs)

# Models -> Concepts
def find_conceptual_models(self, stat_models: list):
    # TODO what do we pass to the KnowledgeBase in the case where we have stats models to solve for...
    kb = KnowledgeBase()

    return kb.find_conceptual_models(stat_models)

"""
pearson_corr = StatisticalTest('pearson_corr', [x0, x1],
                                        test_properties=
                                        [bivariate],
                                        properties_for_vars={
                                            continuous: [[x0], [x1]],
                                            normal: [[x0], [x1]]
                                        })
"""