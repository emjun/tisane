from tisane.code_generator import *

import os
from pathlib import Path
from itertools import chain, combinations
from typing import List, Any, Tuple, Dict, Union
import json 
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf

### GLOBALs
formula_generation_code = """
    ivs = list()
    ivs.append({{main_effects}})
    ivs.append({{interaction_effects}})
    ivs.append({{random_effects}})
    ivs_formula = "+".join(ivs)
    dv_formula = "{{dependent_variable}} ~ "
    formula = dv_formula + ivs_formula
"""

family_link_specification_code = """
    family = {{family_link_pair}}[0]
    link = {{family_link_pair}}[1]
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

def write_to_path(code: str, output_path: os.PathLike):
    # Output @param code to .py script
    with open(output_path, "w+", encoding="utf-8") as f:
        f.write(code)
    print("Writing out path")
    return output_path


# def generate_all_formulae(combined_dict: Dict[str, Any]) -> List[str]: 
#     formulae = list() 
    
#     return formulae

def construct_all_main_options(combined_dict: Dict[str, Any]) -> List[str]:
    input = combined_dict["input"]
    main_effects = input["generated main effects"]
    main_options = powerset(main_effects)

    return list(main_options)

def construct_all_interaction_options(combined_dict: Dict[str, Any]) -> List[str]:
    input = combined_dict["input"]
    interaction_effects = input["generated interaction effects"]
    interaction_options = powerset(interaction_effects)

    return list(interaction_options)

def construct_all_random_options(combined_dict: Dict[str, Any]) -> List[str]:
    input = combined_dict["input"]
    random_effects = input["generated random effects"]
    random_options = powerset(random_effects)

    return list(random_options)

def construct_all_family_link_options(combined_dict: Dict[str, Any], has_random_effects: bool = False) -> List[List[str]]: 
    global pymer4_family_name_to_functions

    input = combined_dict["input"]

    family_link_options = list()
    for family, links in input["generated family, link functions"].items(): 
        for l in links: 
            if has_random_effects: 
                # Use pymer4
                family_func = pymer4_family_name_to_functions[family]
                
                link_func = l
            else:
                # Use statsmodels
                family_func = statsmodels_family_name_to_functions[family]
                link_func = statsmodels_link_name_to_functions[l]
            
            family_link_options.append([family_func, link_func])
    
    return family_link_options

def generate_multiverse_decisions(combined_dict: Dict[str, Any], decisions_path: os.PathLike, decisions_file: os.PathLike) -> os.PathLike: 
    # Generate formulae decisions modularly
    # Construct main options
    main_options = construct_all_main_options(combined_dict=combined_dict)
    main_dict = dict() 
    main_dict["var"] = "main_effects"
    main_dict["options"] = main_options

    # Construct interaction options
    interaction_options = construct_all_interaction_options(combined_dict=combined_dict)
    interaction_dict = dict() 
    interaction_dict["var"] = "interaction_effects"
    interaction_dict["options"] = interaction_options

    # Construct random options
    random_options = construct_all_random_options(combined_dict=combined_dict)
    random_dict = dict() 
    random_dict["var"] = "random_effects"
    random_dict["options"] = random_options

    # Construct family and link pair decisions
    family_link_options = construct_all_family_link_options(combined_dict)
    family_link_dict = dict() 
    family_link_dict["var"] = "family, link pairs" 
    family_link_dict["options"] = family_link_options

    # Combine all the decisions
    decisions_dict = dict()
    decisions_dict["graph"] = list()
    decisions_dict["decisions"] = list()
    decisions_dict["decisions"].append(main_dict)
    decisions_dict["decisions"].append(interaction_dict)
    decisions_dict["decisions"].append(random_dict)
    decisions_dict["decisions"].append(family_link_dict)
    # TODO: Add any bash commands?
    # decisions_dict["before_execute"] = "cp ./code/" 

    # Write out JSON
    path = write_to_json(data=decisions_dict, output_path=decisions_path, output_filename=decisions_file)
    
    return path 

# @param template_file is the output file where the code will be output
def generate_template_code(template_path: os.PathLike, decisions_path: os.PathLike, data_path: Union[os.PathLike, None], target: str = "PYTHON", has_random_effects: bool = False):
    if target.upper() == "PYTHON": 
        code = generate_template_python_code(template_path, decisions_path, data_path, has_random_effects)
    else: 
        assert(target.upper() == "R")
        code =  generate_template_r_code(template_path, decisions_path, data_path, has_random_effects)
    
    # Write generated code out
    path = write_to_path(code, template_path)
    return path

# TODO: Need to inject decisions into template file to use boba
def generate_template_python_code(template_path: os.PathLike, decisions_path: os.PathLike, data_path: Union[os.PathLike, None], target: str = "PYTHON", has_random_effects: bool = False):
    if has_random_effects:
        return generate_template_pymer4_code(template_path, decisions_path, data_path)
    #else: 
    return generate_template_statsmodels_code(template_path, decisions_path, data_path)
        
def generate_template_r_code(template_path: os.PathLike, decisions_path: os.PathLike, data_path: Union[os.PathLike, None], target: str = "PYTHON", has_random_effects: bool = False):
    # Output file is an R file
    raise NotImplementedError

def generate_template_pymer4_code(template_path: os.PathLike, decisions_path: os.PathLike, data_path: Union[os.PathLike, None]):
    global pymer4_code_templates

    ### Specify preamble
    preamble = pymer4_code_templates["preamble"]

    ### Generate data code
    if not data_path: 
        data_code = pymer4_code_templates["load_data_no_data_source"]
    else:
        data_code = pymer4_code_templates["load_data_from_csv_template"]
        data_code = data_code.format(path=str(data_path))

    ### Generate model code
    model_code = generate_template_pymer4_model()

    ### Generate model diagnostics code for plotting residuals vs. fitted
    model_diagnostics_code = pymer4_code_templates["model_diagnostics"]

    ### Put everything together
    model_function_wrapper = pymer4_code_templates["model_function_wrapper"]
    model_diagnostics_function_wrapper = pymer4_code_templates[
        "model_diagnostics_function_wrapper"
    ]
    main_function = pymer4_code_templates["main_function"]

    assert data_code is not None
    # Return string to write out to script
    return (
        preamble
        + "\n"
        + model_function_wrapper
        + data_code
        + "\n"
        + model_code
        + "\n"
        + model_diagnostics_function_wrapper
        + model_diagnostics_code
        + "\n"
        + main_function
    )

def generate_template_statsmodels_code(template_path: os.PathLike, decisions_path: os.PathLike, data_path: Union[os.PathLike, None]):
    global statsmodels_code_templates

    ### Specify preamble
    preamble = statsmodels_code_templates["preamble"]

    ### Generate data code
    if not data_path: 
        data_code = statsmodels_code_templates["load_data_no_data_source"]
    else:
        data_code = statsmodels_code_templates["load_data_from_csv_template"]
        data_code = data_code.format(path=str(data_path))

    ### Generate model code
    model_code = generate_template_statsmodels_model()

    ### Generate model diagnostics code for plotting residuals vs. fitted
    model_diagnostics_code = statsmodels_code_templates["model_diagnostics"]

    ### Put everything together
    model_function_wrapper = statsmodels_code_templates["model_function_wrapper"]
    model_diagnostics_function_wrapper = statsmodels_code_templates[
        "model_diagnostics_function_wrapper"
    ]
    main_function = statsmodels_code_templates["main_function"]

    assert data_code is not None
    # Return string to write out to script
    return (
        preamble
        + "\n"
        + model_function_wrapper
        + data_code
        + "\n"
        + model_code
        + "\n"
        + model_diagnostics_function_wrapper
        + model_diagnostics_code
        + "\n"
        + main_function
    )


def generate_template_pymer4_model(): 
    global pymer4_code_templates, formula_generation_code, family_link_specification_code

    formula_code = "formula"
    family_code = "{family}"
    
    model_code = formula_generation_code + pymer4_code_templates["model_template"].format(
        formula=formula_code, family_name=family_code
    ) + family_link_specification_code
    return model_code


def generate_template_statsmodels_model(): 
    global statsmodels_code_templates, formula_generation_code, family_link_specification_code

    formula_code = "formula"
    family_code = "{family}"
    link_code = "{link}"
    
    model_code = formula_generation_code + statsmodels_code_templates["model_template"].format(
        formula=formula_code, family_name=family_code, link_obj=link_code
    ) + family_link_specification_code
    return model_code