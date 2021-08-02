from tisane.concept import Concept

# from tisane.concept_graph import ConceptGraph, CONCEPTUAL_RELATIONSHIP
from tisane.effect_set import EffectSet
from tisane.graph import Graph
from tisane.design import Design
from tisane.statistical_model import StatisticalModel

# from tisane.conceptual_model import ConceptualModel
from tisane.smt.results import AllStatisticalResults
import tisane.smt.rules as rules
from tisane.smt.query_manager import QM
from tisane.smt.synthesizer import Synthesizer
from tisane.smt.input_interface import InputInterface
from tisane.code_generator import *

from enum import Enum
from typing import List, Union
import copy
from itertools import chain, combinations
import pandas as pd
import networkx as nx
import json

##### Functions that are not associated with a class/object
def query(input_obj: Union[StatisticalModel, Design, Graph], output: str):
    output_obj = None
    # Set up
    if output.upper() == "VARIABLE RELATIONSHIP GRAPH":
        output_obj = Graph()
    elif output.upper() == "STATISTICAL MODEL":
        # TODO: if Graph -> SM, will have to pass dv differently since Graph has no attr DV
        output_obj = StatisticalModel(
            dv=input_obj.dv,
            main_effects=list(),
            interaction_effects=list(),
            mixed_effects=list(),
            link_func=None,
            variance_func=None,
        )
    elif output.upper() == "STUDY DESIGN":
        output_obj = Design()  # No dv, set DV during query process
    assert output_obj is not None

    # Query
    output_obj = QM.query(
        input_obj=input_obj, output_obj=output_obj
    )  # , output=output)

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
        if output_.upper() == "STUDY DESIGN":
            design = query(input_obj=input_, output=output_)

            return design
        elif output_.upper() == "VARIABLE RELATIONSHIP GRAPH":
            gr = query(input_obj=input_, output=output_)
            return gr
    elif isinstance(input_, Graph):
        if output_.upper() == "STUDY DESIGN":
            design = query(input_obj=input_, output=output_)
            return design
        elif isinstance(output_, StatisticalModel):
            sm = query(gr, StatisticalModel)


# @returns statistical model that reflects the study design
def synthesize_statistical_model(design: Design):
    ### Initial conceptual checks
    # TODO: Check that the IVs have a conceptual relationship (direct or transitive) with DV
    # TODO: Check that the DV does not cause one or more IVs
    synth = Synthesizer()

    ### Generate possible effects, family, and link based on input design (graph)
    main_effects_options = synth.generate_main_effects(design=design)
    interaction_effects_options = synth.generate_interaction_effects(design=design)
    random_effects_options = synth.generate_random_effects(design=design)
    # random_effects_options = list()
    # May want to load a dictionary of family to link
    family_link_options = synth.generate_family_link(design=design)
    default_family_link = synth.generate_default_family_link(design=design)
    # family_options = synth.generate_family_distributions(design=design)
    # link_options = synth.generate_link_functions(design=design)

    # Change to:
    # spec = InputInterface(main_effects_options, interaction_effects_options, random_effects_options, family_options, link_options)
    # spec is SM or some json dump -> SM -> code generated

    input_cli = InputInterface(
        main_effects_options,
        interaction_effects_options,
        random_effects_options,
        family_link_options,
        default_family_link,
        design=design,
        synthesizer=synth,
    )
    input_cli.start_app(
        main_effects_options,
        interaction_effects_options,
        random_effects_options,
        family_link_options,
        default_family_link,
        design=design,
    )

    # Read JSON file
    sm = None
    f = open("model_spec.json", "r")

    # Construct StatisticalModel from JSON spec
    model_json = f.read()
    sm = synth.create_statistical_model(model_json, design).assign_data(design.dataset)
    # sm = StatisticalModel().from_json(f.read())

    # Generate code from SM
    script = generate_code(sm)

    return scipt  # (TODO: look into replacing the code snippet in original program)


# Checks that the IVS for @param design have a conceptual relationship with the DV
# Issues a warning if an independent variable does not cause or associate with the DV
def check_design_ivs(design: Design):
    dv = design.dv
    for i in design.ivs:
        has_cause = design.graph.has_edge(start=i, end=dv, edge_type="cause")
        has_associate = design.graph.has_edge(start=i, end=dv, edge_type="associate")

        # Variable i has neither a cause nor an associate relationship with the DV
        if not has_cause and not has_associate:
            raise ValueError(
                f"The independent variable {i.name} does not have a conceptual relationship with the dependent variable {dv.name}. Every independent variable should either CAUSE or  ASSOCIATE_WITH the dependent variable."
            )


# Checks that the DV does not cause any of the IVs
# Issues a warning if dependent variable causes an independent variable
def check_design_dv(design: Design):
    dv = design.dv

    for i in design.ivs:
        dv_causes = design.graph.has_edge(start=dv, end=i, edge_type="cause")

        if dv_causes:
            raise ValueError(
                f"The dependent variable {dv.name} causes the independent variable {i.name}."
            )


# @returns statistical model that reflects the study design
def infer_statistical_model_from_design(design: Design):
    ### Initial conceptual checks
    # Check that the IVs have a conceptual relationship (direct or transitive) with DV
    check_design_ivs(design)
    # Check that the DV does not cause one or more IVs
    check_design_dv(design)

    synth = Synthesizer()

    ### Generate possible effects, family, and link based on input design (graph)
    gr = synth.transform_to_has_edges(design.graph)
    ivs = design.ivs
    dv = design.dv
    main_effects_options = synth.generate_main_effects_from_graph(gr, ivs, dv)
    interaction_effects_options = synth.generate_interaction_effects_from_graph(
        gr, ivs, dv
    )
    random_effects_options = synth.generate_random_effects_from_graph(gr, ivs, dv)

    # May want to load a dictionary of family to link
    family_link_options = synth.generate_family_link(design=design)
    default_family_link = synth.generate_default_family_link(design=design)

    input_cli = InputInterface(
        main_effects_options,
        interaction_effects_options,
        random_effects_options,
        family_link_options,
        default_family_link,
        design=design,
        synthesizer=synth,
    )
    input_cli.start_app(
        main_effects_options,
        interaction_effects_options,
        random_effects_options,
        family_link_options,
        default_family_link,
        design=design,
    )

    # Read JSON file
    sm = None
    f = open("model_spec.json", "r")

    # Construct StatisticalModel from JSON spec
    model_json = f.read()
    sm = synth.create_statistical_model(model_json, design).assign_data(
        design.dataset.dataset
    )

    # Generate code from SM
    script = generate_code(sm)

    return script


# @returns statistical model that reflects the study design
def infer_statistical_model(dv: AbstractVariable, ivs=List[AbstractVariable]):
    ### Initial conceptual checks
    # TODO: Check that the IVs have a conceptual relationship (direct or transitive) with DV
    # TODO: Check that the DV does not cause one or more IVs
    synth = Synthesizer()

    ### Generate possible effects, family, and link based on input design (graph)
    main_effects_options = synth.generate_main_effects(design=design)
    interaction_effects_options = synth.generate_interaction_effects(design=design)
    random_effects_options = synth.generate_random_effects(design=design)
    # random_effects_options = list()
    # May want to load a dictionary of family to link
    family_link_options = synth.generate_family_link(design=design)
    default_family_link = synth.generate_default_family_link(design=design)
    # family_options = synth.generate_family_distributions(design=design)
    # link_options = synth.generate_link_functions(design=design)

    # Change to:
    # spec = InputInterface(main_effects_options, interaction_effects_options, random_effects_options, family_options, link_options)
    # spec is SM or some json dump -> SM -> code generated

    input_cli = InputInterface(
        main_effects_options,
        interaction_effects_options,
        random_effects_options,
        family_link_options,
        default_family_link,
        design=design,
        synthesizer=synth,
    )
    input_cli.start_app(
        main_effects_options,
        interaction_effects_options,
        random_effects_options,
        family_link_options,
        default_family_link,
        design=design,
    )

    # Read JSON file
    sm = None
    f = open("model_spec.json", "r")

    # Construct StatisticalModel from JSON spec
    model_json = f.read()
    sm = synth.create_statistical_model(model_json, design).assign_data(design.dataset)
    # sm = StatisticalModel().from_json(f.read())

    # Generate code from SM
    script = generate_code(sm)

    return scipt


# def verify(
#     input_: Union[Design, ConceptualModel, StatisticalModel],
#     output_: Union[Design, ConceptualModel, StatisticalModel],
# ):
#     if isinstance(input_, Design) and isinstance(output_, ConceptualModel):
#         return verify_design_and_conceptual_model(design=input_, cm=output_)
#     elif isinstance(input_, ConceptualModel) and isinstance(output_, Design):
#         return verify_design_and_conceptual_model(design=output_, cm=input_)
#     elif isinstance(input_, Design) and isinstance(output_, StatisticalModel):
#         return verify_design_and_statistical_model(design=input_, sm=output_)
#     elif isinstance(input_, StatisticalModel) and isinstance(output_, Design):
#         return verify_design_and_statistical_model(design=output_, sm=input_)
#     elif isinstance(input_, StatisticalModel) and isinstance(output_, ConceptualModel):
#         return verify_statistical_model_and_conceptual_model(sm=input_, cm=output_)
#     elif isinstance(input_, ConceptualModel) and isinstance(output_, StatisticalModel):
#         return verify_statistical_model_and_conceptual_model(sm=output_, cm=input_)
#     else:
#         # TODO: If two objects of the same class are compared!
#         raise NotImplementedError


# def verify_design_and_conceptual_model(design: Design, cm: ConceptualModel):
#     d_graph = design.graph
#     cm_graph = cm.graph

#     cm_edges = cm_graph.get_edges()
#     for (n0, n1, data) in cm_edges:
#         n0_var = cm_graph.get_variable(name=n0)
#         n1_var = cm_graph.get_variable(name=n1)
#         if data["edge_type"] == "associate":
#             # check if there is a corresponding 'unknown' edge in the Study Design
#             if not d_graph.has_edge(start=n0_var, end=n1_var, edge_type="unknown"):
#                 # Check both because Conceptual Models have bidirectional edges for 'associations'
#                 if not d_graph.has_edge(start=n1_var, end=n0_var, edge_type="unknown"):
#                     return False
#         elif data["edge_type"] == "cause":
#             # check if there is a corresponding 'unknown' edge in the Study Design
#             if not d_graph.has_edge(start=n0_var, end=n1_var, edge_type="unknown"):
#                 return False
#     return True


# def verify_statistical_model_and_conceptual_model(
#     sm: StatisticalModel, cm: ConceptualModel
# ):
#     sm_graph = sm.graph
#     cm_graph = cm.graph

#     cm_edges = cm_graph.get_edges()
#     for (n0, n1, data) in cm_edges:
#         n0_var = cm_graph.get_variable(name=n0)
#         n1_var = cm_graph.get_variable(name=n1)
#         if data["edge_type"] == "associate":
#             # check if there is a corresponding 'unknown' edge in the Statistical Model
#             if not sm_graph.has_edge(start=n0_var, end=n1_var, edge_type="unknown"):
#                 return False
#         elif data["edge_type"] == "cause":
#             # check if there is a corresponding 'unknown' edge in the Statistical Model
#             if not sm_graph.has_edge(start=n0_var, end=n1_var, edge_type="unknown"):
#                 return False
#     return True


def verify_design_and_statistical_model(design: Design, sm: StatisticalModel):
    # Catches missing info in design that should appear in statistical model &&
    # Catches info that appears in statistical model that should appear in design

    # Catches omitted groupings (mixed effects) that are in Design but missing in Statistical Model

    # Catches groupigns (mixed effects) that are in Statistical Model but missing in Design?

    pass
