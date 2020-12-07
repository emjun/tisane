from tisane.concept import Concept

import z3
import copy

class StatisticalModel(object):
    name: str # name of the statisitcal model
    properties: list # list of properties that the model assumes to be true/requirements
    # TODO: Does it make sense to have IVs and DV as concepts??
    ivs: list
    dv: Concept
    __z3__: z3.Bool
    
    def __init__(self, name: str, properties: list): 
        self.name = name
        self.properties = properties # TODO: May consider having different classes of properties
        self.__z3__ = z3.Bool(self.name)

    def __apply__(self, ivs: list, dvs: list):
        self.ivs = ivs
        assert(len(dvs) == 1)
        dv = dvs[0]
        self.dv = dv

    def query(self): 
        
        applied_properties = list() 
        for p in self.properties: 
            # import pdb; pdb.set_trace()
            all_vars = copy.deepcopy(self.ivs) + [self.dv]
            applied_properties.append(p(*all_vars))
        self.properties = applied_properties

        # import pdb; pdb.set_trace()

        # the validity of a StatisticalModel is the conjunction of all its properties
        conj = list()

        for p in self.properties: 
            conj += [p.__z3__]

        return conj
        

# def verify(self): 
        
#         # the validity of a StatisticalModel is the conjunction of all its properties
#         conj = list()

#         for p in self.properties: 
#             pz = p.verify()
#             conj += [pz]
        
#         # set this Statistical Model's z3 Bool
#         # TODO: may not need to save the result of this?
#         self.__z3__ = z3.And(*conj)
    
#         return self.__z3__