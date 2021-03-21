from tisane.concept import Concept
# from tisane.concept_graph import ConceptGraph, CONCEPTUAL_RELATIONSHIP
from tisane.effect_set import EffectSet
from tisane.graph import Graph
from tisane.design import Design
from tisane.statistical_model import StatisticalModel
from tisane.conceptual_model import ConceptualModel
from tisane.smt.results import AllStatisticalResults
import tisane.smt.rules as rules
from tisane.smt.query_manager import QM
from tisane.smt.synthesizer import Synthesizer
from tisane.smt.input_interface import InputInterface

from enum import Enum 
from typing import List, Union
import copy 
from itertools import chain, combinations
import pandas as pd
import networkx as nx

##### Functions that are not associated with a class/object
def query(input_obj: Union[StatisticalModel, Design, Graph], output: str): 
    output_obj = None
    # Set up 
    if output.upper() =='VARIABLE RELATIONSHIP GRAPH': 
        output_obj = Graph()
    elif output.upper() == 'STATISTICAL MODEL': 
        # TODO: if Graph -> SM, will have to pass dv differently since Graph has no attr DV
        output_obj = StatisticalModel(dv=input_obj.dv, main_effects=list(), interaction_effects=list(), mixed_effects=list(), link_func=None, variance_func=None)
    elif output.upper() == 'STUDY DESIGN': 
        output_obj = Design() # No dv, set DV during query process
    assert(output_obj is not None)        

    # Query 
    output_obj = QM.query(input_obj=input_obj, output_obj=output_obj)#, output=output)

    # Return results
    return output_obj

def infer_from(input_: Union[Design], output_: str): 
    
    if isinstance(input_, Design): 
        if output_.upper() == 'STATISTICAL MODEL':
            # Get main effects want to consider from end-user (separate from unsat framework)

            # Get interaction effects want to consider from end-user (fits into unsat framework)
            sm = query(input_obj=input_, output=output_)
            return sm 
        elif output_.upper() == 'VARIABLE RELATIONSHIP GRAPH': 
            gr = query(input_obj=input_, output=output_)
            return gr

    elif isinstance(input_, StatisticalModel):
        if output_.upper() == 'STUDY DESIGN': 
            design = query(input_obj=input_, output=output_)
            import pdb; pdb.set_trace()
            return design 
        elif output_.upper() == 'VARIABLE RELATIONSHIP GRAPH': 
            gr = query(input_obj=input_, output=output_)
            return gr
    elif isinstance(input_, Graph):
        if output_.upper() == 'STUDY DESIGN': 
            design = query(input_obj=input_, output=output_)
            return design 
        elif isinstance(output_, StatisticalModel): 
            sm = query(gr, StatisticalModel)

# @returns statistical model that reflects the study design 
def synthesize_statistical_model(design: Design): 
    synth = Synthesizer()
    input_cli = InputInterface(design=design, synthesizer=synth)
    return synth.synthesize_statistical_model(design=design)
    

def verify(input_: Union[Design, ConceptualModel, StatisticalModel], output_: Union[Design, ConceptualModel, StatisticalModel]): 
    if isinstance(input_, Design) and isinstance(output_, ConceptualModel): 
        return verify_design_and_conceptual_model(design=input_, cm=output_)
    elif isinstance(input_, ConceptualModel) and isinstance(output_, Design): 
        return verify_design_and_conceptual_model(design=output_, cm=input_) 
    elif isinstance(input_, Design) and isinstance(output_, StatisticalModel): 
        return verify_design_and_statistical_model(design=input_, sm=output_)
    elif isinstance(input_, StatisticalModel) and isinstance(output_, Design): 
        return verify_design_and_statistical_model(design=output_, sm=input_)
    elif isinstance(input_, StatisticalModel) and isinstance(output_, ConceptualModel): 
        return verify_statistical_model_and_conceptual_model(sm=input_, cm=output_)
    elif isinstance(input_, ConceptualModel) and isinstance(output_, StatisticalModel): 
        return verify_statistical_model_and_conceptual_model(sm=output_, cm=input_)
    else: 
        # TODO: If two objects of the same class are compared!
        raise NotImplementedError

def verify_design_and_conceptual_model(design: Design, cm: ConceptualModel): 
    d_graph = design.graph
    cm_graph = cm.graph

    cm_edges = cm_graph.get_edges()
    for (n0, n1, data) in cm_edges: 
        n0_var = cm_graph.get_variable(name=n0)
        n1_var = cm_graph.get_variable(name=n1)
        if data['edge_type'] == 'associate': 
            # check if there is a corresponding 'unknown' edge in the Study Design 
            if not d_graph.has_edge(start=n0_var, end=n1_var, edge_type='unknown'): 
                # Check both because Conceptual Models have bidirectional edges for 'associations'
                if not d_graph.has_edge(start=n1_var, end=n0_var, edge_type='unknown'): 
                    return False
        elif data['edge_type'] == 'cause': 
            # check if there is a corresponding 'unknown' edge in the Study Design 
            if not d_graph.has_edge(start=n0_var, end=n1_var, edge_type='unknown'): 
                return False
    return True

def verify_statistical_model_and_conceptual_model(sm: StatisticalModel, cm: ConceptualModel): 
    sm_graph = sm.graph 
    cm_graph = cm.graph 

    cm_edges = cm_graph.get_edges()
    for (n0, n1, data) in cm_edges: 
        n0_var = cm_graph.get_variable(name=n0)
        n1_var = cm_graph.get_variable(name=n1)
        if data['edge_type'] == 'associate': 
            # check if there is a corresponding 'unknown' edge in the Statistical Model 
            if not sm_graph.has_edge(start=n0_var, end=n1_var, edge_type='unknown'): 
                return False
        elif data['edge_type'] == 'cause': 
            # check if there is a corresponding 'unknown' edge in the Statistical Model
            if not sm_graph.has_edge(start=n0_var, end=n1_var, edge_type='unknown'): 
                return False
    return True
    
def verify_design_and_statistical_model(design: Design, sm: StatisticalModel): 
    # Catches missing info in design that should appear in statistical model &&
    # Catches info that appears in statistical model that should appear in design

    # Catches omitted groupings (mixed effects) that are in Design but missing in Statistical Model 
    
    # Catches groupigns (mixed effects) that are in Statistical Model but missing in Design? 

    pass 
