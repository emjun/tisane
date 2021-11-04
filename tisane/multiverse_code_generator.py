from tisane.code_generator import generate_python_code

import os
from typing import List, Any, Tuple
import typing
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf

# TODO: Borrow functions from code_generator functions 9e.g., generate_pymer4_code...


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