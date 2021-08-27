"""
This file generates examples to use when developing and testing the Tisane GUI.

These examples are first tested in `test_candidate_json_generation.py` before being copied/pasted into this file to generate the JSON files.
"""
from os import write
import tisane as ts
from tisane.main import collect_model_candidates, write_to_json
from tisane.graph_inference import (
    infer_main_effects_with_explanations,
    infer_interaction_effects_with_explanations,
    infer_random_effects_with_explanations,
)
from tisane.family_link_inference import infer_family_functions, infer_link_functions
import os


def main_effects_only(path="./gui/example_inputs/", filename="main_only.json"):
    u0 = ts.Unit("Unit")
    m0 = u0.numeric("Measure_0")
    m1 = u0.numeric("Measure_1")
    dv = u0.numeric("Dependent_variable")

    design = ts.Design(dv=dv, ivs=[m0, m1])
    gr = design.graph

    (main_effects, main_explanations) = infer_main_effects_with_explanations(
        gr=gr, query=design
    )
    (
        interaction_effects,
        interaction_explanations,
    ) = infer_interaction_effects_with_explanations(
        gr=gr, query=design, main_effects=main_effects
    )
    (random_effects, random_explanations) = infer_random_effects_with_explanations(
        gr=gr,
        query=design,
        main_effects=main_effects,
        interaction_effects=interaction_effects,
    )
    family_candidates = infer_family_functions(query=design)
    link_candidates = set()
    family_link_paired = dict()
    for f in family_candidates:
        l = infer_link_functions(query=design, family=f)
        # Add Family: Link options
        assert f not in family_link_paired.keys()
        family_link_paired[f] = l

    # Combine explanations
    explanations = dict()
    explanations.update(main_explanations)
    explanations.update(interaction_explanations)
    explanations.update(random_explanations)

    # Get combined dict
    combined_dict = collect_model_candidates(
        query=design,
        main_effects_candidates=main_effects,
        interaction_effects_candidates=interaction_effects,
        random_effects_candidates=random_effects,
        family_link_paired_candidates=family_link_paired,
    )

    # Add explanations
    combined_dict["input"]["explanations"] = explanations

    # Output combined dict to @param path
    write_to_json(data=combined_dict, output_path=path, output_filename=filename)


def main_interaction(path="./gui/example_inputs/", filename="main_interaction.json"):
    u0 = ts.Unit("Unit")
    m0 = u0.numeric("Measure_0")
    m1 = u0.numeric("Measure_1")
    m2 = u0.numeric("Measure_2")
    dv = u0.numeric("Dependent_variable")

    m0.causes(dv)
    m1.causes(dv)
    m2.moderates(moderator=m1, on=dv)

    design = ts.Design(dv=dv, ivs=[m0, m1, m2])
    gr = design.graph

    (main_effects, main_explanations) = infer_main_effects_with_explanations(
        gr=gr, query=design
    )
    (
        interaction_effects,
        interaction_explanations,
    ) = infer_interaction_effects_with_explanations(
        gr=gr, query=design, main_effects=main_effects
    )
    (random_effects, random_explanations) = infer_random_effects_with_explanations(
        gr=gr,
        query=design,
        main_effects=main_effects,
        interaction_effects=interaction_effects,
    )
    family_candidates = infer_family_functions(query=design)
    link_candidates = set()
    family_link_paired = dict()
    for f in family_candidates:
        l = infer_link_functions(query=design, family=f)
        # Add Family: Link options
        assert f not in family_link_paired.keys()
        family_link_paired[f] = l

    # Combine explanations
    explanations = dict()
    explanations.update(main_explanations)
    explanations.update(interaction_explanations)
    explanations.update(random_explanations)

    combined_dict = collect_model_candidates(
        query=design,
        main_effects_candidates=main_effects,
        interaction_effects_candidates=interaction_effects,
        random_effects_candidates=random_effects,
        family_link_paired_candidates=family_link_paired,
    )

    # Add explanations
    combined_dict["input"]["explanations"] = explanations

    # Output combined dict to @param path
    write_to_json(data=combined_dict, output_path=path, output_filename=filename)


def main_interaction_random_intercepts(
    path="./gui/example_inputs/", filename="main_interaction_random_intercepts.json"
):
    u0 = ts.Unit("Unit")
    s0 = ts.SetUp("Time", order=[1, 2, 3, 4, 5])
    m0 = u0.numeric("Measure_0")
    m1 = u0.numeric("Measure_1")
    m2 = u0.numeric("Measure_2")
    dv = u0.numeric("Dependent_variable", number_of_instances=s0)

    m0.causes(dv)
    m1.causes(dv)
    s0.associates_with(dv)
    m2.moderates(moderator=m1, on=dv)

    design = ts.Design(dv=dv, ivs=[m0, m1, m2, s0])  # main effect of Time
    gr = design.graph

    (main_effects, main_explanations) = infer_main_effects_with_explanations(
        gr=gr, query=design
    )
    (
        interaction_effects,
        interaction_explanations,
    ) = infer_interaction_effects_with_explanations(
        gr=gr, query=design, main_effects=main_effects
    )
    (random_effects, random_explanations) = infer_random_effects_with_explanations(
        gr=gr,
        query=design,
        main_effects=main_effects,
        interaction_effects=interaction_effects,
    )
    family_candidates = infer_family_functions(query=design)
    link_candidates = set()
    family_link_paired = dict()
    for f in family_candidates:
        l = infer_link_functions(query=design, family=f)
        # Add Family: Link options
        assert f not in family_link_paired.keys()
        family_link_paired[f] = l

    # Combine explanations
    explanations = dict()
    explanations.update(main_explanations)
    explanations.update(interaction_explanations)
    explanations.update(random_explanations)

    combined_dict = collect_model_candidates(
        query=design,
        main_effects_candidates=main_effects,
        interaction_effects_candidates=interaction_effects,
        random_effects_candidates=random_effects,
        family_link_paired_candidates=family_link_paired,
    )

    # Add explanations
    combined_dict["input"]["explanations"] = explanations

    # Output combined dict to @param path
    write_to_json(data=combined_dict, output_path=path, output_filename=filename)


def main_interaction_random_slope_one_variable(
    path="./gui/example_inputs/",
    filename="main_interaction_random_slope_one_variable.json",
):
    u = ts.Unit("Unit")
    a = u.nominal(
        "Measure A", cardinality=2, number_of_instances=2
    )  # A is within-subjects
    b = u.nominal("Measure B", cardinality=2)  # B is between-subjects
    dv = u.numeric("Dependent_variable")

    a.causes(dv)
    b.causes(dv)
    a.moderates(moderator=[b], on=dv)

    design = ts.Design(dv=dv, ivs=[a, b])
    gr = design.graph

    (main_effects, main_explanations) = infer_main_effects_with_explanations(
        gr=gr, query=design
    )
    (
        interaction_effects,
        interaction_explanations,
    ) = infer_interaction_effects_with_explanations(
        gr=gr, query=design, main_effects=main_effects
    )
    (random_effects, random_explanations) = infer_random_effects_with_explanations(
        gr=gr,
        query=design,
        main_effects=main_effects,
        interaction_effects=interaction_effects,
    )
    family_candidates = infer_family_functions(query=design)
    link_candidates = set()
    family_link_paired = dict()
    for f in family_candidates:
        l = infer_link_functions(query=design, family=f)
        # Add Family: Link options
        assert f not in family_link_paired.keys()
        family_link_paired[f] = l

    # Combine explanations
    explanations = dict()
    explanations.update(main_explanations)
    explanations.update(interaction_explanations)
    explanations.update(random_explanations)

    combined_dict = collect_model_candidates(
        query=design,
        main_effects_candidates=main_effects,
        interaction_effects_candidates=interaction_effects,
        random_effects_candidates=random_effects,
        family_link_paired_candidates=family_link_paired,
    )

    # Add explanations
    combined_dict["input"]["explanations"] = explanations

    # Output combined dict to @param path
    write_to_json(data=combined_dict, output_path=path, output_filename=filename)


def main_interaction_random_slope_interaction(
    path="./gui/example_inputs/",
    filename="main_interaction_random_slope_interaction.json",
):
    u = ts.Unit("Unit")
    a = u.nominal(
        "Measure A", cardinality=2, number_of_instances=2
    )  # A is within-subjects
    b = u.nominal(
        "Measure B", cardinality=2, number_of_instances=2
    )  # B is within-subjects
    dv = u.numeric("Dependent_variable")

    a.causes(dv)
    b.causes(dv)
    a.moderates(moderator=[b], on=dv)

    design = ts.Design(dv=dv, ivs=[a, b])
    gr = design.graph

    (main_effects, main_explanations) = infer_main_effects_with_explanations(
        gr=gr, query=design
    )
    (
        interaction_effects,
        interaction_explanations,
    ) = infer_interaction_effects_with_explanations(
        gr=gr, query=design, main_effects=main_effects
    )
    (random_effects, random_explanations) = infer_random_effects_with_explanations(
        gr=gr,
        query=design,
        main_effects=main_effects,
        interaction_effects=interaction_effects,
    )
    family_candidates = infer_family_functions(query=design)
    link_candidates = set()
    family_link_paired = dict()
    for f in family_candidates:
        l = infer_link_functions(query=design, family=f)
        # Add Family: Link options
        assert f not in family_link_paired.keys()
        family_link_paired[f] = l

    # Combine explanations
    explanations = dict()
    explanations.update(main_explanations)
    explanations.update(interaction_explanations)
    explanations.update(random_explanations)

    combined_dict = collect_model_candidates(
        query=design,
        main_effects_candidates=main_effects,
        interaction_effects_candidates=interaction_effects,
        random_effects_candidates=random_effects,
        family_link_paired_candidates=family_link_paired,
    )

    # Add explanations
    combined_dict["input"]["explanations"] = explanations

    # Output combined dict to @param path
    write_to_json(data=combined_dict, output_path=path, output_filename=filename)


def main_interaction_random_intercept_slope_correlated(
    path="./gui/example_inputs/",
    filename="main_interaction_random_intercept_slope_correlated.json",
):
    subject = ts.Unit("Subject", cardinality=12)
    word = ts.Unit("Word", cardinality=4)
    condition = subject.nominal("Word_type", cardinality=2, number_of_instances=2)
    reaction_time = subject.numeric("Time", number_of_instances=word)  # repeats
    condition.has(word, number_of_instances=2)

    condition.causes(reaction_time)

    design = ts.Design(dv=reaction_time, ivs=[condition])
    gr = design.graph

    (main_effects, main_explanations) = infer_main_effects_with_explanations(
        gr=gr, query=design
    )
    (
        interaction_effects,
        interaction_explanations,
    ) = infer_interaction_effects_with_explanations(
        gr=gr, query=design, main_effects=main_effects
    )
    (random_effects, random_explanations) = infer_random_effects_with_explanations(
        gr=gr,
        query=design,
        main_effects=main_effects,
        interaction_effects=interaction_effects,
    )
    family_candidates = infer_family_functions(query=design)
    link_candidates = set()
    family_link_paired = dict()
    for f in family_candidates:
        l = infer_link_functions(query=design, family=f)
        # Add Family: Link options
        assert f not in family_link_paired.keys()
        family_link_paired[f] = l

    # Combine explanations
    explanations = dict()
    explanations.update(main_explanations)
    explanations.update(interaction_explanations)
    explanations.update(random_explanations)

    combined_dict = collect_model_candidates(
        query=design,
        main_effects_candidates=main_effects,
        interaction_effects_candidates=interaction_effects,
        random_effects_candidates=random_effects,
        family_link_paired_candidates=family_link_paired,
    )

    # Add explanations
    combined_dict["input"]["explanations"] = explanations

    # Output combined dict to @param path
    write_to_json(data=combined_dict, output_path=path, output_filename=filename)


def main_interaction_multiple_random_slopes(
    path="./gui/example_inputs/",
    filename="main_interaction_multiple_random_slopes.json",
):
    u = ts.Unit("Unit")
    a = u.nominal("Measure A", cardinality=2)  # A is between-subjects
    b = u.nominal(
        "Measure B", cardinality=2, number_of_instances=2
    )  # B is within-subjects
    c = u.nominal(
        "Measure C", cardinality=2, number_of_instances=2
    )  # B is within-subjects
    dv = u.numeric("Dependent_variable")

    a.causes(dv)
    b.causes(dv)
    c.causes(dv)
    b.associates_with(c)
    a.moderates(moderator=[b], on=dv)  # AB --> get B
    a.moderates(moderator=[c], on=dv)  # AC --> get C
    b.moderates(moderator=[c], on=dv)  # BC --> get BC
    a.moderates(moderator=[b, c], on=dv)  # BC --> get BC

    design = ts.Design(dv=dv, ivs=[a, b])
    gr = design.graph

    (main_effects, main_explanations) = infer_main_effects_with_explanations(
        gr=gr, query=design
    )
    (
        interaction_effects,
        interaction_explanations,
    ) = infer_interaction_effects_with_explanations(
        gr=gr, query=design, main_effects=main_effects
    )
    (random_effects, random_explanations) = infer_random_effects_with_explanations(
        gr=gr,
        query=design,
        main_effects=main_effects,
        interaction_effects=interaction_effects,
    )
    family_candidates = infer_family_functions(query=design)
    link_candidates = set()
    family_link_paired = dict()
    for f in family_candidates:
        l = infer_link_functions(query=design, family=f)
        # Add Family: Link options
        assert f not in family_link_paired.keys()
        family_link_paired[f] = l

    # Combine explanations
    explanations = dict()
    explanations.update(main_explanations)
    explanations.update(interaction_explanations)
    explanations.update(random_explanations)

    combined_dict = collect_model_candidates(
        query=design,
        main_effects_candidates=main_effects,
        interaction_effects_candidates=interaction_effects,
        random_effects_candidates=random_effects,
        family_link_paired_candidates=family_link_paired,
    )

    # Add explanations
    combined_dict["input"]["explanations"] = explanations

    # Output combined dict to @param path
    write_to_json(data=combined_dict, output_path=path, output_filename=filename)


os.chdir(os.path.dirname(__file__))
os.chdir("..")

main_effects_only()
main_interaction()
main_interaction_random_intercepts()
main_interaction_random_slope_one_variable()
main_interaction_random_slope_interaction()
main_interaction_random_intercept_slope_correlated()
main_interaction_multiple_random_slopes()
