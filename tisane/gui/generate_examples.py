from os import write
import tisane as ts
from tisane.main import collect_model_candidates, write_to_json
from tisane.family_link_inference import infer_family_functions, infer_link_functions

def main_effects_only(path="./gui/example_inputs/", filename="main_only.json"): 
    u0 = ts.Unit("Unit")
    m0 = u0.numeric("Measure 0")
    m1 = u0.numeric("Measure 1")
    dv = u0.numeric("Dependent variable")

    query = ts.Design(dv=dv, ivs=[m0, m1])

    main_effects = set()
    main_effects.add(m0)
    main_effects.add(m1)

    interaction_effects = set()
    random_effects = set()
    family_candidates = infer_family_functions(query=query)
    link_candidates = set()
    family_link_paired = dict()
    for f in family_candidates: 
        l = infer_link_functions(query=query, family=f)
        # Add Family: Link options 
        assert(f.__class__ not in family_link_paired.keys())
        family_link_paired[f.__class__] = l

    # Get combined dict
    combined_dict = collect_model_candidates(query=query, main_effects_candidates=main_effects, interaction_effects_candidates=interaction_effects, random_effects_candidates=random_effects, family_link_paired_candidates=family_link_paired)

    # Output combined dict to @param path 
    write_to_json(data=combined_dict, output_path=path, output_filename=filename)

main_effects_only()