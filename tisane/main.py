from tisane.concept import Concept
from enum import Enum 
from typing import Union
import pandas as pd

class TASK(Enum): 
    EXPLANATION = 1
    PREDICTION = 2
    HYPOTHESIS_TESTING = 3 # Maybe hypothesis testing is a mode on top of explanation vs. prediction
    
    @classmethod
    def cast(self, type_str:str): 
        if type_str.upper() == 'EXPLANATION':
            return TASK.EXPLANATION
        elif type_str.upper() == 'PREDICTION': 
            return TASK.PREDICTION
        elif type_str.upper() == 'HYPOTHESIS TESTING': 
            return TASK.HYPOTHESIS_TESTING
        else: 
            raise ValueError(f"Data type {type_str} not supported! Try EXPLANATION, PREDICTION, or HYPOTHESIS TESTING")

class RELATIONSHIP(Enum): 
    LINEAR = 1
    # The choices below are arbitrary
    QUADRATIC = 2
    EXPONENTIAL = 3 

    @classmethod
    def cast(self, type_str:str): 
        if type_str.upper() == 'LINEAR':
            return RELATIONSHIP.LINEAR
        elif type_str.upper() == 'QUADRATIC':
            return RELATIONSHIP.QUADRATIC
        elif type_str.upper() == 'EXPONENTIAL': 
            return RELATIONSHIP.EXPONENTIAL
        else: 
            raise ValueError(f"Relationship type {type_str} not supported! Try LINEAR, QUADRATIC, or EXPONENTIAL")

class Graph(object): 
    def __init__(self): 
        self.elts = None

    def addNode(self, con: Concept): 
        raise NotImplementedError
    
    # May want a different signature...
    def addEdge(self, edge_type: str, start_con: Concept, end_con: Concept): 
        raise NotImplementedError
    

class Data(object): 
    pass

class Tisane(object):
    task : TASK
    graph : Graph # Not clear this is necessary at the moment
    relationship: RELATIONSHIP
    data : Data

    def __init__(self, task:str):
        self.task = task
        self.graph = None # TODO: graph structure might not be the right one?
        self.data = None
    
    def __repr__(self):
        pass
    
    def __str__(self):
        pass

    def addConcept(self, con: Concept): 
        self.graph.addNode(con)
    
    def addData(self, data: Union[str, pd.DataFrame]):
        raise NotImplementedError
        # May want to do something about CSV (create new object class/type?)
        self.data = data

    def relate(self, ivs:list, dv=list, type=str): 
        pass
    
    def between(self, con:Concept): 
        pass