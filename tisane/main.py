from tisane.concept import Concept
from tisane.conceptual_graph import ConceptGraph, CONCEPTUAL_RELATIONSHIP

from enum import Enum 
from typing import Union
import copy 
import pandas as pd
import networkx as nx

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

class Data(object): 
    pass

class Tisane(object):
    task : TASK
    graph : ConceptGraph # Not clear this is necessary at the moment
    relationship: RELATIONSHIP
    data : Data

    def __init__(self, task:str):
        self.task = TASK.cast(task)
        self.graph = ConceptGraph() # TODO: graph structure might not be the right one?
        self.relationship = None # TODO: Not sure we want to default to none? 
        self.data = None
    
    def __repr__(self):
        pass
    
    def __str__(self):
        pass

    def addConcept(self, con: Concept): 
        # Do we need to create a graph ?
        if not self.graph: 
            self.graph = ConceptGraph()
        self.graph.addNode(con)    
    
    def addData(self, data: Union[str, pd.DataFrame]):
        raise NotImplementedError
        # May want to do something about CSV (create new object class/type?)
        self.data = data

    def relate(self, ivs:list, dv=list, relationship=str): 

        # add the ivs if they are already not part of the graph 
        gr = self.graph
        for i in ivs: 
            if gr.hasConcept(i): 
                pass
            else: 
                # copy elts already in graph
                gr = copy.deepcopy(gr)
                # add new elt to graph
                gr.addNode(i)

        # add the dv is they are already not part of the graph 
        assert(len(dv) == 1)
        d = dv[0] # get the Concept elt
        if gr.hasConcept(d): 
            pass 
        else: 
            # copy elts already in graph
            gr = copy.deepcopy(gr)
            # add new elt to graph
            gr.addNode(d)
        
        # add the relationship
        self.relationship = RELATIONSHIP.cast(relationship)
        
        # assign self.graph to new graph with elements (if it was created)
        self.graph = gr
    
    def between(self, con:Concept): 
        pass

    def addRelationship(self, lhs_con: Concept, rhs_con: Concept, relationship_type: str): 
        cr = CONCEPTUAL_RELATIONSHIP.cast(relationship_type)        
        self.graph.addEdge(lhs_con, rhs_con, cr)

