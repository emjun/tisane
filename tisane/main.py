from tisane.graph import Graph
from tisane.graph_inference import infer_main_effects, infer_interaction_effects, infer_random_effects
from tisane.family_link_inference import infer_family_functions, infer_link_functions
from tisane.design import Design
from tisane.statistical_model import StatisticalModel
from tisane.code_generator import *

from enum import Enum
from typing import List, Union
import copy
from itertools import chain, combinations
import pandas as pd
import networkx as nx
import json

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
    gr = design.graph

    ### Step 1: Initial conceptual checks
    # Check that the IVs have a conceptual relationship (direct or transitive) with DV
    check_design_ivs(design)
    # Check that the DV does not cause one or more IVs
    check_design_dv(design)


    ### Step 2: Candidate statistical model inference/generation
    main_effects_candidates = infer_main_effects(gr=gr, query=design)
    # Assume all the main effects will be selected 
    main_effects_candidates = list(main_effects_candidates)
    
    interaction_effects_candidates = infer_interaction_effects(gr=gr, query=design, main_effects=main_effects_candidates)
    interaction_effects_candidates = list(interaction_effects_candidates) 

    random_effects_candidates = infer_random_effects(gr=gr, query=design, main_effects=main_effects_candidates, interaction_effects=interaction_effects_candidates)

    family_candidates = infer_family_functions(query=design)
    for f in family_candidates: 
        # TODO: store the family-links somewhere!
        infer_link_functions(query=design, family=f)

    # Put everything together 


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


    ### Step 3: Disambiguation loop 
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

    ### Step 4: Code generation 
    # Construct StatisticalModel from JSON spec
    model_json = f.read()
    sm = synth.create_statistical_model(model_json, design).assign_data(
        design.dataset.dataset
    )

    # Generate code from SM
    script = generate_code(sm)

    return script
