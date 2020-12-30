from tisane.smt.statistical_model import StatisticalModel
from tisane.smt.property import *
from tisane.smt.statistical_variable import StatVar

import copy

""" Properties 
data_type(v, type): 
"""

# TODO: Does it make sense for initialize_all_properties() to be in smt.property or here? 

class KnowledgeBase(object):
    all_stat_models: list
    all_properties: dict

    sv_ivs: List[StatVar]
    sv_dvs: List[StatVar]
    
    def __init__(self, ivs: list, dvs: list): 
        self.all_stat_models = list()

        self.sv_ivs = self.cast_vars(ivs)
        self.sv_dvs = self.cast_vars(dvs)
        
        self.all_properties = initialize_all_properties(self.sv_ivs, self.sv_dvs)
        
        self.initialize_all_stat_models(self.sv_ivs, self.sv_dvs)

    def cast_vars(self, vars_list: list): 
        cast_vars_list = list()

        for v in vars_list: 
            cast_v = StatVar(v)

            cast_vars_list.append(cast_v)

        return cast_vars_list

    def initialize_all_stat_models(self, ivs: list, dvs: list):
        
        self.all_stat_models.append(
            StatisticalModel(
                name='Linear Regression', 
                properties=[
                    self.all_properties['numeric_dv'],
                    self.all_properties['normal_distribution_residuals']
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

    def get_all_stat_models(self): 
        return self.all_stat_models

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
    def find_statistical_models(self, **kwargs) -> List[StatisticalModel]: 
        
        ivs = self.sv_ivs
        dvs = self.sv_dvs

        # Are there any assertions to make before solving?
        if 'assertions' in kwargs: 
            assertions = kwargs['assertions']
            self.add_assertions(assertions)

        # TODO: SOLVE
        valid_statistical_models = list() # TODO: May want a better data structure for representing all valid statistical models

        solver = z3.Solver()

        # all_vars = copy.deepcopy(ivs) + copy.deepcopy(dvs)
        # for prop in self.all_properties: 
        #     prop._update(len(all_vars))

        # Apply all tests to the variables we are considering now in combined_data
        for sm in self.get_all_stat_models(): 
            sm.__apply__(ivs=ivs, dvs=dvs)

        solver.push() # Create backtracking point
        solver_model = None # Store model

        # For each test, add it to the solver as a constraint. 
        # Add the tests and their properties
        for sm in self.get_all_stat_models():
            solver.add(sm.__z3__ == z3.And(*sm.query()))
            solver.add(sm.__z3__ == z3.BoolVal(True))
        
            # Check the model 
            result = solver.check()
            if result == z3.unsat:
                solver.pop() 
            elif result == z3.unknown:
                print("failed to solve")
                try:
                    pass
                except z3.Z3Exception:
                    return
            else:
                model = solver.model()
                if model and z3.is_true(model.evaluate(sm.__z3__)):
                    # TODO implement this part
                    pass

        # Final check 
        solver.check()
        model = solver.model()  


        # Create output
        for sm in self.get_all_stat_models(): 
            if model and z3.is_true(model.evaluate(sm.__z3__)):
                # TODO: don't output just name but object? 
                valid_statistical_models.append(sm.name)
            elif not model: # No test applies
                pass

        # import pdb; pdb.set_trace()

        # TODO: Output new result data structure!
        return valid_statistical_models

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

    return kb.find_statistical_models(**kwargs)

# Models -> Concepts
def find_conceptual_models(self, stat_models: list):
    # TODO what do we pass to the KnowledgeBase in the case where we have stats models to solve for...
    kb = KnowledgeBase()
    kb.

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