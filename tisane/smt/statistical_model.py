from tisane.concept import Concept

import z3

class StatisticalModel(object):
    name: str # name of the statisitcal model
    properties: list # list of properties that the model assumes to be true/requirements
    # TODO: Does it make sense to have IVs and DV as concepts??
    ivs: list
    dv: Concept
    
    def __init__(self, name: str, properties: list): 
        self.name = name
        self.properties = properties

    def __apply(self, ivs: list, dvs: list):
        self.ivs = list
        assert(len(dvs) == 1)
        self.dv = dvs[0]
        