from tisane.code_generator import generate_python_code

import os
from pathlib import Path
from itertools import chain, combinations
from typing import List, Any, Tuple, Dict
import json 
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf

### GLOBALs
formula_generation = """
ivs = list()
ivs.append({{main_effects}})
ivs.append({{interaction_effects}})
ivs.append({{random_effects}})
ivs_formula = "+".join(ivs)
dv_formula = "{{dependent_variable}} ~ "
formula = dv_formula + ivs_formula
"""

### Helper functions
def powerset(iterable, min_length=0, max_length=None):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    if max_length is not None: 
        return chain.from_iterable(combinations(s, r) for r in range(min_length, max_length+1))
    #else: 
    return chain.from_iterable(combinations(s, r) for r in range(min_length, len(s)+1))

# Write data to JSON file specified in @param output_path
def write_to_json(data: Dict, output_path: str, output_filename: str):
    assert output_filename.endswith(".json")
    path = Path(output_path, output_filename)
    # Output dictionary to JSON
    with open(path, "w+", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4, sort_keys=True)

    return path


# TODO: Borrow functions from code_generator functions 9e.g., generate_pymer4_code...
def construct_all_formulae(combined_dict: Dict[str, Any]) -> List[str]: 
    formulae = list() 
    
    return formulae

def construct_all_main_options(combined_dict: Dict[str, Any]) -> List[str]:
    input = combined_dict["input"]
    main_effects = input["generated main effects"]
    main_options = powerset(main_effects)

    return main_options

def construct_all_interaction_options(combined_dict: Dict[str, Any]) -> List[str]:
    pass 

def construct_all_family(combined_dict: Dict[str, Any]) -> List[str]: 
    family = list() 

    return family

def construct_all_link(combined_dict: Dict[str, Any]) -> List[str]: 
    link = list() 

    return link
    

def generate_multiverse_decisions(combined_dict: Dict[str, Any], decisions_path: os.PathLike, decisions_file: os.PathLike) -> os.PathLike: 
    
    # Generate formulae decisions
    formulae_options = construct_all_formulae(combined_dict=combined_dict)
    formulae_dict = dict() 
    formulae_dict["var"] = "formula"
    formulae_dict["options"] = formulae_options

    # Generate family decisions
    family_options = construct_all_family(combined_dict)
    family_dict = dict() 
    family_dict["var"] = "family" 
    family_dict["options"] = family_options

    # Generate link decisions
    link_options = construct_all_link(combined_dict)
    link_dict = dict() 
    link_dict["var"] = "link" 
    link_dict["options"] = link_options

    # Combine all the decisions
    decisions_dict = dict()
    decisions_dict["graph"] = list()
    decisions_dict["decisions"] = list()
    decisions_dict["decisions"].append(formulae_dict)
    decisions_dict["decisions"].append(family_dict)
    decisions_dict["decisions"].append(link_dict)
    # TODO: Add any bash commands?
    # decisions_dict["before_execute"] = "cp ./code/" 

    # Write out JSON
    path = write_to_json(data=decisions_dict, output_path=decisions_path, output_filename=decisions_file)
    
    return path 


# @param template_file is the output file where the code will be output
def generate_template_code(template_file: os.PathLike, decisions_file: os.PathLike, data_file: os.PathLike, target: str = "PYTHON", has_random_effects: bool = False):
    if target.upper() == "PYTHON": 
        return generate_template_python_code(template_file, decisions_file, data_file)

    #else
    assert(target.upper() == "R")
    return generate_template_r_code(template_file, decisions_file, data_file)

# TODO: Need to inject decisions into template file to use boba
def generate_template_python_code():
    # IF THERE ARE RANDOM EFFECTS USE....
    pass
        
def generate_template_r_code(): 
    # Output file is an R file
    pass