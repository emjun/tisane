from tisane.concept import Concept
from tisane.concept_graph import ConceptGraph, CONCEPTUAL_RELATIONSHIP
from tisane.effect_set import EffectSet
from tisane.graph import Graph
from tisane.statistical_model import StatisticalModel
from tisane.asp.knowledge_base import KB, KnowledgeBase
import tisane.smt.rules as rules
from tisane.smt.query_manager import QM
from tisane.smt.results import AllStatisticalResults
from tisane.design import Design

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

# TODO: REVAMP API
class Tisane(object):
    task : TASK
    graph : ConceptGraph # Not clear this is necessary at the moment
    relationship: RELATIONSHIP
    data : Data
    knowledge_base : KnowledgeBase # optional

    def __init__(self, task:str, knowledge_base: KnowledgeBase=None):

        self.task = TASK.cast(task)
        self.graph = ConceptGraph() # TODO: graph structure might not be the right one?
        self.relationship = None # TODO: Not sure we want to default to none? 
        self.data = None
        self.knowledge_base = KB # use global KnowledgeBase
    
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
            # gr = copy.deepcopy(gr)
            # add new elt to graph
            gr.addNode(con)

        # assign self.graph to new graph with new concept (if created)
        self.graph = gr
    
    # Atomic add of list of Concepts
    def addConceptList(self, con_list: list): 
        if not self.graph: 
            self.graph = ConceptGraph()
        gr = self.graph

        # import pdb; pdb.set_trace()
        # add the ivs if they are already not part of the graph 
        for c in con_list:
            self.addConcept(c)
        
        self.graph = gr
    
    def addData(self, data: Union[str, pd.DataFrame]):
        raise NotImplementedError
        # May want to do something about CSV (create new object class/type?)
        self.data = data

    def relate(self, ivs:list, dv=list, relationship=str): 
        assert(len(dv) == 1)

        # all_cons = copy.deepcopy(ivs) + copy.deepcopy(dv) # deepcopy may not be necessary
        all_cons = ivs + dv # deepcopy may not be necessary
        self.addConceptList(all_cons)

        # add the relationship
        self.relationship = RELATIONSHIP.cast(relationship)
        
    def between(self, con:Concept): 
        pass

    def addRelationship(self, lhs_con: Concept, rhs_con: Concept, relationship_type: str): 
        # add all concepts to the graph (nodes before edges)
        # all_cons = [copy.deepcopy(lhs_con), copy.deepcopy(rhs_con)] # may not need deep copy
        all_cons = [lhs_con, rhs_con] # may not need deep copy

        # all_cons = [lhs_con, rhs_con] # may not need deep copy
        self.addConceptList(all_cons)

        # add Relationship (edge)
        cr = CONCEPTUAL_RELATIONSHIP.cast(relationship_type)
        self.graph.addEdge(lhs_con, rhs_con, cr)
    
    def relate(self, lhs: Concept, relationship_type: str, rhs: Concept): 
        self.addRelationship(lhs_con=lhs, rhs_con=rhs, relationship_type=relationship_type)

    # @returns Concept that has @param concept_name
    def get_concept(self, concept_name: str) -> Concept:  
        pass
            
        
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

    # @param effect_set is an EffectSet
    # @returns a list of assertions to use when querying the knowledge base
    def collect_assertions(self, effect_set) -> list: 
        # TODO: Probably can get rid of this if have Concepts in EffectSet (instead of str names)
        # TODO: At very least, could make this a helper function?
        # get Concepts for all corresponding effects in @param effect_set
        dv_concept = [effect_set.get_dv()]
        ivs_concepts = list()
        
        main_concepts = list()
        if effect_set.has_main_effects():
            main_effects = effect_set.get_main_effects().effect
            for m in main_effects: 
                assert(isinstance(m, str))
                main_concepts.append(self.graph.getConcept(m))
            ivs_concepts += main_concepts
        
        ivs_concepts = main_concepts

        interaction_concepts = list()
        if effect_set.has_interaction_effects():
            interaction_effects = effect_set.get_interaction_effects().effect
            for i in interaction_effects: 
                assert(isinstance(i, str))
                interaction_concepts.append(self.graph.getConcept(i))
            ivs_concepts += interaction_concepts

        mixed_concepts = list()
        if effect_set.has_mixed_effects():
            mixed_effects = effect_set.get_mixed_effects().effect
            for mi in mixed_effects: 
                assert(isinstance(mi, str))
                mixed_concepts.append(self.graph.getConcept(mi))
            ivs_concepts += mixed_concepts    

        # Collect assertions from Concepts
        all_assertions = list()
        # IVs
        for c in ivs_concepts: 
            c_assert = self.knowledge_base.get_concept_constraints(concept=c)
            all_assertions += c_assert

        # DV
        all_assertions += self.knowledge_base.get_concept_constraints(concept=dv_concept[0])

        # Collect assertions from Effect Set
        es_assert = self.knowledge_base.get_effect_set_constraints(effect_set=effect_set)
        all_assertions += es_assert
    
        return all_assertions


    # @param effect_set to use in order to model
    # @returns a set/list? of valid StatisticalModels for the @param effect_set
    def start_model(self, effect_set: EffectSet): 
        
        # get Concepts for all corresponding effects in @param effect_set
        dv_concept = [effect_set.get_dv()]
        ivs_concepts = list()
        
        main_concepts = list()
        if effect_set.has_main_effects():
            main_effects = effect_set.get_main_effects().effect
            for m in main_effects: 
                assert(isinstance(m, str))
                main_concepts.append(self.graph.getConcept(m))
            ivs_concepts += main_concepts
        
        ivs_concepts = main_concepts

        interaction_concepts = list()
        if effect_set.has_interaction_effects():
            interaction_effects = effect_set.get_interaction_effects().effect
            for i in interaction_effects: 
                assert(isinstance(i, str))
                interaction_concepts.append(self.graph.getConcept(a))
            ivs_concepts += interaction_concepts

        mixed_concepts = list()
        if effect_set.has_mixed_effects():
            mixed_effects = effect_set.get_mixed_effects().effect
            for mi in mixed_effects: 
                assert(isinstance(mi, str))
                mixed_concepts.append(self.graph.getConcept(mi))
            ivs_concepts += mixed_concepts    


        # dyamically generate constraints based on @param effect_set arity and variables
        self.knowledge_base.generate_constraints(name='test0', ivs=ivs_concepts, dv=dv_concept)

        # collect assertions (variable and effect set)
        assertions = self.collect_assertions(effect_set=effect_set)

        # query knowledge base
        res = self.knowledge_base.query(file_name='specific_constraints_test0.lp', assertions=assertions)
        # import pdb; pdb.set_trace()

        # if there's an error
        if res[1]: 
            # Interactive loop: dynamically, interactively figure out and get user input for additional constraints that underspecifed in current assertions. 
            return self.continue_model(file_name='specific_constraints_test0.lp', assertions=assertions)
        
        else: 
            # TODO: This could be moved to helper function outside of KnowledgeBase
            valid_models = self.knowledge_base.construct_models_from_query_result(query_result=res, effect_set=effect_set)

            return self.finish_model(valid_models)

    def continue_model(self, file_name, assertions): 
        raise NotImplementedError

    # Generates the output script and allows for execution of @param valid_models
    def finish_model(self, valid_models: List[StatisticalModel]): 
        return valid_models

    def model_idea0(self): 
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
    
##### Functions that are not associated with a class/object
def query(input_obj: Union[StatisticalModel, Design, Graph], output: str): 
    output_obj = None
    # Set up 
    if output.upper() =='VARIABLE RELATIONSHIP GRAPH': 
        output_obj = Graph()
    elif output.upper() == 'STATISTICAL MODEL': 
        # TODO: if Graph -> SM, will have to pass dv differently since Graph has no attr DV
        output_obj = StatisticalModel(dv=input_obj.dv, main_effects=list(), interaction_effects=list(), mixed_effects=list(), link_func=None, variance_func=None)
    else: 
        raise NotImplementedError
    assert(output_obj is not None)        

    # Query 
    output_obj = QM.query(input_obj=input_obj, output_obj=output_obj)#, output=output)

    # Return results
    return output_obj

def infer_from(input_: Union[Design], output_: str): 
    
    if isinstance(input_, Design): 
        if output_.upper() == "STATISTICAL MODEL":
            # Get main effects want to consider from end-user (separate from unsat framework)

            # Get interaction effects want to consider from end-user (fits into unsat framework)
            sm = query(input_obj=input_, output=output_)
            return sm 
        elif output_.upper() == "VARIABLE RELATIONSHIP GRAPH": 
            gr = query(input_obj=input_, output=output_)
            return gr

    elif isinstance(input_, StatisticalModel):
        if output_.upper() == "DESIGN": 
            raise NotImplementedError
            # gr = input_.get_graph_ir()
            # design = query(gr, Design())
        elif output_.upper() == "VARIABLE RELATIONSHIP GRAPH": 
            gr = query(input_obj=input_, output=output_)
            import pdb; pdb.set_trace()
            return gr
    elif isinstance(input_, Graph): 
        pass
        # if isinstance(output_, Design): 
        #     design = query(gr, Design())
        #     # What would the above query look like in terms of logical formula?
        # elif isinstance(output_, StatisticalModel): 
        #     sm = query(gr, StatisticalModel)
    



    