from tisane.concept import Concept
from tisane.concept_graph import ConceptGraph, CONCEPTUAL_RELATIONSHIP
from tisane.smt.results import AllStatisticalResults
from tisane.asp.knowledge_base import KnowledgeBase

from enum import Enum 
from typing import List, Union
import copy 
from itertools import chain, combinations
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

    def getGraph(self):
        return self.graph

    # atomic add of a single Concept
    def addConcept(self, con: Concept): 
        if not self.graph: 
            self.graph = ConceptGraph()
        gr = self.graph
        
        if gr.hasConcept(con): 
            pass
        else: 
            # copy elts already in graph
            gr = copy.deepcopy(gr)
            # add new elt to graph
            gr.addNode(con)

        # assign self.graph to new graph with new concept (if created)
        self.graph = gr
    
    # Atomic add of list of Concepts
    def addConceptList(self, con_list: list): 
        if not self.graph: 
            self.graph = ConceptGraph()
        gr = self.graph

        # add the ivs if they are already not part of the graph 
        for c in con_list:
            if gr.hasConcept(c): 
                pass
            else: 
                # copy elts already in graph
                gr = copy.deepcopy(gr)
                # add new elt to graph
                gr.addNode(c)
        
        self.graph = gr
    
    def addData(self, data: Union[str, pd.DataFrame]):
        raise NotImplementedError
        # May want to do something about CSV (create new object class/type?)
        self.data = data

    def relate(self, ivs:list, dv=list, relationship=str): 
        assert(len(dv) == 1)

        all_cons = copy.deepcopy(ivs) + copy.deepcopy(dv) # deepcopy may not be necessary
        self.addConceptList(all_cons)

        # add the relationship
        self.relationship = RELATIONSHIP.cast(relationship)
        
    def between(self, con:Concept): 
        pass

    def addRelationship(self, lhs_con: Concept, rhs_con: Concept, relationship_type: str): 
        # add all concepts to the graph (nodes before edges)
        all_cons = [copy.deepcopy(lhs_con), copy.deepcopy(rhs_con)] # may not need deep copy
        # all_cons = [lhs_con, rhs_con] # may not need deep copy
        self.addConceptList(all_cons)

        # add Relationship (edge)
        cr = CONCEPTUAL_RELATIONSHIP.cast(relationship_type)
        self.graph.addEdge(lhs_con, rhs_con, cr)
        
    """
    Prediction: Use sets of variables that have BOTH causal and correlational relationships with DV
    """
    def predict(self, dv: Concept): 
        pass
    
    def predictWith(self, dv: Concept, ivs_to_include: list): 
        pass

    def predictWithOnly(self, dv: Concept, ivs_to_include_only: list): 
        pass

    def predictWithout(self, dv: Concept, ivs_to_exclude: list): 
        pass
    
    """
    Explanation: Use sets of variables that have ONLY causal relationships with DV
    """
    # FOR DEBUGGING
    # def generate_main_effects(self, dv: Concept):
    #     pass

    # def generate_main_effects(self, dv: Concept):
    #     pass

    def generate_effects_sets(self, ivs: List[Concept], dv: Concept):
        return self.graph.generate_effects_sets(dv=dv)
    
    def generate_effects_sets_with_ivs(self, ivs: List[Concept], dv: Concept): 
        return self.graph.generate_effects_sets_with_ivs(ivs=ivs, dv=dv)

    def model(self): 
        effects_sets = self.generate_effects_sets_with_ivs(ivs=ivs, dv=dv)    
        
        for es in effects_sets: 
            es_name = str() # TODO come up with some name for the effects (maybe just list them all out)
            # kb.generate_constraints(name=es_name, ivs=es.ivs, dv=es.dv)

            get_valid_statistical_models(self, es)
            
        """
        # TODO: KB should keep track of all the sets of constraints for each effects set as well as any "GLOBAL" constraints that are true/false

        - keep a dict or something of all sets of constraints
        - keep a list/dict of all constraints or something 
        # TODO: Update all the files with asserted constraints
        - this may require coming up with a set of checks to do on the variables for all effects sets
        # TODO: Find answer sets (valid models) for each file with asserted constraints

        # TODO: Generate outputs for valid models for each effects sets
        
        # Question: Do we have to check all the properties? What if there are some properties that we would not have to check if some are already invalid?  
        """

    def get_valid_statistical_models(self, effects_sets): 
        kb = KnowledgeBase()

        # Step: Interactions for getting all the properties for the Concepts/Variables (using data if there is data)
        # Collect assertions
        
        # TODO: Start up editor if not already open or move model to the Editor (latter is probably better)
        model = InteractiveTisaneEditor(self)

        # Step: Dynamically generate constriants for KB with assertions about the properties from Interactions (Step above)
        # Could probably call KB function? 
        valid_statistical_models = list()

        # Step: Get valid tests and then 
        models = self.construct_statistical_models(effects_sets=effects_sets, valid_statistical_models=valid_statistical_models)

        return (kb, models) # may not want to return KnowledgeBase

    def construct_statistical_models(self, effects_sets, valid_statistical_models): 
        pass

    def pretty_print_effects_sets(self, dv: Concept):
        effects_sets = self.generate_effects_sets(dv=dv)

        import pdb; pdb.set_trace()

        for es in effects_sets:
            for effect in es:
                if len(effect) > 1:
                    import pdb; pdb.set_trace()
                assert(len(effect) <= 1)

    def explain(self, dv: Concept): 

        effects_sets = self.graph.generate_effects_sets(dv=dv)

        all_valid_stat_models = AllStatisticalResults()


        # for m in comb_main: 
        #     model = create_model(m)
        #     if check_model(model): # check that model satisfy model requirements
        #         collect_models.append(model)
        
        return all_valid_stat_models
    
    def explainWith(self, dv: Concept, ivs_to_include: list): 
        pass

    def explainWithOnly(self, dv: Concept, ivs_to_include_only: list): 
        pass

    def explainWithout(self, dv: Concept, ivs_to_exclude: list): 
        pass

    # @param property is used to parse/generate the constraints
    def assume_property(self, property: str): 
        raise NotImplementedError

    # Asserts the @param prop in the knowledge base
    # @param prop is used to parse/generate the constraints
    def assert_property(self, prop: str): 
        # TODO: Should we have a distinction between assumed and asserted? 
        # assumed: still check (including visually)
        # asserted: stop modeling if data does not fit this property
        
        kb.assert_property(property=prop)