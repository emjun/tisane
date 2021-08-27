from tisane.family import SquarerootLink
from tisane.data import Dataset
from tisane.variable import AbstractVariable
from tisane.statistical_model import StatisticalModel
from tisane.random_effects import (
    RandomIntercept,
    RandomSlope,
    CorrelatedRandomSlopeAndIntercept,
    UncorrelatedRandomSlopeAndIntercept,
)

import os
from typing import List, Any, Tuple
import typing
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf


### GLOBALs
pymer4_preamble = """
# Tisane inferred the following statistical model based on this query:  {}

import pandas as pd
from pymer4.models import Lmer # supports Generalized linear models with or without mixed effects
import matplotlib.pyplot as plt # for visualizing residual plots to diagnose model fit
"""

statsmodels_preamble = """
# Tisane inferred the following statistical model based on this query:  {}

import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt # for visualizing residual plots to diagnose model fit
"""

model_function_wrapper = """ 
def fit_model(): 
"""

model_diagnostics_function_wrapper = """
# What should you look for in the plot? 
# If there is systematic bias in how residuals are distributed, you may want to try a new link or family function. You may also want to reconsider your conceptual and statistical models. 
# Read more here: https://sscc.wisc.edu/sscc/pubs/RegressionDiagnostics.html
def show_model_diagnostics(model): 
"""

main_function = """
if __name__ == "__main__":
    model = fit_model()
    show_model_diagnostics(model)
"""

load_data_from_csv_template = """
    df = pd.read_csv('{path}')
"""

load_data_from_dataframe_template = """
    # Dataframe is stored in local file: data.csv
    # You may want to replace the data path with an existing data file you already have.
    # You may also set df equal to a pandas dataframe you are already working with. 
    df = pd.read_csv('{path}') # Make sure that the data path is correct
"""

load_data_no_data_source = """
    # There was no data assigned to the Design. Add data below. 
    path = '' # Specify path to data if loading from a csv
    df = pd.read_csv(path)
    # If loading from a pandas Dataframe, alias dataframe with variable df
    # df = <your pandas Dataframe>
"""

pymer4_model_template = """
    model = Lmer(formula={formula}, family=\"{family_name}\", data=df)
    print(model.fit())
    return model
"""

statsmodels_model_template = """
    model = smf.glm(formula={formula}, data=df, family=sm.families.{family_name}(sm.families.links.{link_obj}))
    res = model.fit()
    print(res.summary())
    return model
"""

pymer4_model_diagnostics = """
    plt.scatter(model.fits, model.residuals)
    plt.title("Fitted values vs. Residuals")
    plt.xlabel("fitted values")
    plt.ylabel("residuals")
    plt.show()
"""

statsmodels_model_diagnostics = """
    res = model.fit()
    plt.clf()
    plt.grid(True)
    plt.plot(res.predict(linear=True), res.resid_pearson, 'o')
    plt.xlabel("Linear predictor")
    plt.ylabel("Residual")
    plt.show()
"""

pymer4_code_templates = {
    "preamble": pymer4_preamble,
    "model_function_wrapper": model_function_wrapper,
    "load_data_from_csv_template": load_data_from_csv_template,
    "load_data_from_dataframe_template": load_data_from_dataframe_template,
    "load_data_no_data_source": load_data_no_data_source,
    "model_template": pymer4_model_template,
    "model_diagnostics_function_wrapper": model_diagnostics_function_wrapper,
    "model_diagnostics": pymer4_model_diagnostics,
    "main_function": main_function,
}

statsmodels_code_templates = {
    "preamble": statsmodels_preamble,
    "model_function_wrapper": model_function_wrapper,
    "load_data_from_csv_template": load_data_from_csv_template,
    "load_data_from_dataframe_template": load_data_from_dataframe_template,
    "load_data_no_data_source": load_data_no_data_source,
    "model_template": statsmodels_model_template,
    "model_diagnostics_function_wrapper": model_diagnostics_function_wrapper,
    "model_diagnostics": statsmodels_model_diagnostics,
    "main_function": main_function,
}

# Reference from:
pymer4_family_name_to_functions = {
    "GaussianFamily": "gaussian",
    "InverseGaussianFamily": "inverse_gaussian",
    "GammaFamily": "gamma",
    # Not implemented in pymer4 or lme4
    # "TweedieFamily": "Tweedie",
    "PoissonFamily": "poisson",
    "BinomialFamily": "binomial",
    # Not implemented in pymer4 or lme4
    # "NegativeBinomialFamily": "NegativeBinomial",
}

# Lme4 implements defaults for the link functions based on the family functions
pymer4_link_name_to_functions = {}

# Reference from: https://www.statsmodels.org/stable/glm.html#families
statsmodels_family_name_to_functions = {
    "GaussianFamily": "Gaussian",
    "InverseGaussianFamily": "InverseGaussian",
    "GammaFamily": "Gamma",
    "TweedieFamily": "Tweedie",
    "PoissonFamily": "Poisson",
    "BinomialFamily": "Binomial",
    "NegativeBinomialFamily": "NegativeBinomial",
}

statsmodels_link_name_to_functions = {
    "IdentityLink": "identity()",
    "InverseLink": "inverse_power()",
    "InverseSquaredLink": "inverse_squared()",
    "LogLink": "log()",
    "LogitLink": "logit()",
    "ProbitLink": "probit()",
    "CauchyLink": "cauchy()",
    "CLogLogLink": "cloglog()",
    "PowerLink": "Power()",
    "SquarerootLink": "Power(power=.5)",
    # Not currently implemented in statsmodels
    # "OPowerLink": "",
    "NegativeBinomialLink": "NegativeBinomial()",
    # Not currently implemented in statsmodels
    # "LogLogLink": "",
}

### HELPERS
def absolute_path(p: str) -> str:
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), p)


# Write data out to path
# Return path
def write_out_dataframe(data: Dataset) -> os.path:
    destinationDir = os.getcwd()
    output_filename = os.path.join(destinationDir, "data.csv")
    # path = absolute_path("data.csv")
    assert data.has_data()
    data.get_data().to_csv(output_filename)

    return output_filename


# @param target describes the backend for which to generate code
def generate_code(
    statistical_model: StatisticalModel, target: str = "PYTHON", **kwargs
):
    if target.upper() == "PYTHON":
        return generate_python_code(statistical_model=statistical_model, **kwargs)


def generate_python_code(statistical_model: StatisticalModel):
    global pymer4_code_templates

    if statistical_model.has_random_effects():
        return generate_pymer4_code(statistical_model=statistical_model)
    else:
        assert not statistical_model.has_random_effects()
        return generate_statsmodels_code(statistical_model=statistical_model)


def generate_pymer4_code(statistical_model: StatisticalModel):
    global pymer4_code_templates

    ### Specify preamble
    preamble = pymer4_code_templates["preamble"]

    ### Generate data code
    data_code = None
    if not statistical_model.has_data():
        data_code = pymer4_code_templates["load_data_no_data_source"]
    else:
        data = statistical_model.get_data()
        if data.has_data_path():
            data_code = pymer4_code_templates["load_data_from_csv_template"]
            data_code = data_code.format(path=str(data.data_path))
        else:
            assert not data.has_data_path()
            data_path = write_out_dataframe(data)
            data_code = pymer4_code_templates[
                "load_data_from_dataframe_template"
            ].format(path=data_path)

    ### Generate model code
    model_code = generate_pymer4_model(statistical_model=statistical_model)

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


def generate_pymer4_model(statistical_model: StatisticalModel):
    global pymer4_code_templates

    formula_code = generate_pymer4_formula(statistical_model=statistical_model)
    family_code = generate_pymer4_family(statistical_model=statistical_model)
    # link_code = generate_pymer4_link(statistical_model=statistical_model)
    model_code = pymer4_code_templates["model_template"].format(
        formula=formula_code, family_name=family_code
    )

    return model_code


def generate_pymer4_formula(statistical_model: StatisticalModel):
    global pymer4_code_templates

    dv_code = "{dv} ~ "
    dv_code = dv_code.format(dv=statistical_model.dependent_variable.name)

    main_code = str()
    sm_main_effects_names = [var.name for var in statistical_model.main_effects]
    sm_main_effects_names.sort()  # Alphabetize
    for var_name in sm_main_effects_names:
        if len(main_code) == 0:
            main_code = f"{var_name}"
        else:
            main_code += f" + {var_name}"

    interaction_code = str()
    sm_interaction_effects_names = [
        var.name for var in statistical_model.interaction_effects
    ]
    sm_interaction_effects_names.sort()  # Alphabetize
    for var_name in sm_interaction_effects_names:
        if len(interaction_code) == 0:
            interaction_code = f"{var_name}"
        else:
            interaction_code += f" + {var_name}"

    # https://bbolker.github.io/mixedmodels-misc/glmmFAQ.html#model-specification
    random_code = str()
    for rc in statistical_model.random_effects:
        if isinstance(rc, RandomSlope):
            groups = rc.groups
            iv = rc.iv
            rc_code = f"(0+{iv.name}|{groups.name})"
        elif isinstance(rc, RandomIntercept):
            groups = rc.groups
            rc_code = f"(1|{groups.name})"
        elif isinstance(rc, CorrelatedRandomSlopeAndIntercept):
            groups = rc.random_slope.groups
            assert groups == rc.random_intercept.groups
            iv = rc.random_slope.iv
            rc_code = f"(1+{iv.name}|{groups.name})"
        else:
            assert isinstance(rc, UncorrelatedRandomSlopeAndIntercept)
            groups = rc.random_slope.groups
            assert groups == rc.random_intercept.groups
            iv = rc.random_slope.iv
            rc_code = f"(1|{groups.name}) + (0+{iv.name}|{groups.name})"

        if len(random_code) == 0:
            random_code = rc_code
        else:
            random_code += " + " + rc_code

    # Do we have both main effects and interaction effects?
    post_main_connector = ""
    if len(main_code) > 0:
        if len(interaction_code) > 0 or len(random_code) > 0:
            post_main_connector = " + "

    post_interaction_connector = ""
    if len(interaction_code) > 0:
        if len(random_code) > 0:
            post_interaction_connector = " + "

    return (
        "'"
        + dv_code
        + main_code
        + post_main_connector
        + interaction_code
        + post_interaction_connector
        + random_code
        + "'"
    )


def generate_pymer4_family(statistical_model: StatisticalModel) -> str:
    global pymer4_family_name_to_functions
    sm_family = statistical_model.family_function
    sm_family_name = type(sm_family).__name__

    return pymer4_family_name_to_functions[sm_family_name]


# def generate_pymer4_link(statistical_model=StatisticalModel) -> str:
#     return str()


def generate_statsmodels_code(statistical_model: StatisticalModel):
    global statsmodels_code_templates

    ### Specify preamble
    preamble = statsmodels_code_templates["preamble"]

    ### Generate data code
    data_code = None
    if not statistical_model.has_data():
        data_code = statsmodels_code_templates["load_data_no_data_source"]
    else:
        data = statistical_model.get_data()
        if data.data_path is not None:
            data_code = statsmodels_code_templates["load_data_from_csv_template"]
            data_code = data_code.format(path=str(data.data_path))
        else:
            assert data.data_path is None
            data_path = write_out_dataframe(data)
            data_code = statsmodels_code_templates[
                "load_data_from_dataframe_template"
            ].format(path=data_path)

    ### Generate model code
    formula_code = generate_statsmodels_formula(statistical_model=statistical_model)
    family_code = generate_statsmodels_family(statistical_model=statistical_model)
    link_code = generate_statsmodels_link(statistical_model=statistical_model)
    model_code = statsmodels_code_templates["model_template"].format(
        formula=formula_code, family_name=family_code, link_obj=link_code
    )
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


def generate_statsmodels_model(statistical_model: StatisticalModel):
    global statsmodels_code_templates

    formula_code = generate_statsmodels_formula(statistical_model=statistical_model)
    family_code = generate_statsmodels_family(statistical_model=statistical_model)
    link_code = generate_statsmodels_link(statistical_model=statistical_model)
    model_code = statsmodels_code_templates["model_template"].format(
        formula=formula_code, family_name=family_code, link_obj=link_code
    )

    return model_code


def generate_statsmodels_formula(statistical_model: StatisticalModel):
    dv_code = "{dv} ~ "
    dv_code = dv_code.format(dv=statistical_model.dependent_variable.name)

    main_code = str()
    sm_main_effects_names = [var.name for var in statistical_model.main_effects]
    sm_main_effects_names.sort()  # Alphabetize
    for var_name in sm_main_effects_names:
        if len(main_code) == 0:
            main_code = f"{var_name}"
        else:
            main_code += f" + {var_name}"

    interaction_code = str()
    sm_interaction_effects_names = [
        var.name for var in statistical_model.interaction_effects
    ]
    sm_interaction_effects_names.sort()  # Alphabetize
    for var_name in sm_interaction_effects_names:
        if len(interaction_code) == 0:
            interaction_code = f"{var_name}"
        else:
            interaction_code += f" + {var_name}"

    # Do we have both main effects and interaction effects?
    post_main_connector = ""
    if len(main_code) > 0:
        if len(interaction_code) > 0:
            post_main_connector = " + "

    return "'" + dv_code + main_code + post_main_connector + interaction_code + "'"


# @returns string of family function in statsmodels corresponding to @param statistical_model's family function (of AbstractFamily type)
def generate_statsmodels_family(statistical_model: StatisticalModel) -> str:
    global statsmodels_family_name_to_functions
    sm_family = statistical_model.family_function
    sm_family_name = type(sm_family).__name__

    return statsmodels_family_name_to_functions[sm_family_name]


def generate_statsmodels_link(statistical_model=StatisticalModel):
    global statsmodels_link_name_to_functions
    sm_link = statistical_model.link_function
    sm_link_name = type(sm_link).__name__

    return statsmodels_link_name_to_functions[sm_link_name]


def generate_statsmodels_glm_code(statistical_model: StatisticalModel, **kwargs) -> str:
    has_random = len(statistical_model.random_ivs) > 0
    assert has_random is False

    # Intercept added automatically with formula unless specified otherwise
    if "no_intercept" in kwargs:
        model = sm.GLM

        # TODO: Might not need to get data again, just reuse existing code in "outer" code gen function
    else:
        ## Build FORMULA
        model = "model = smf.glm"
        y = statistical_model.dv
        y_code = f"{y.name}"
        xs_code = None
        for f in statistical_model.fixed_ivs:
            if xs_code is None:
                xs_code = f"{f.name}"
            else:
                xs_code += f" + {f.name}"

        for interaction in statistical_model.interactions:
            ixn_terms = list()
            for e in interaction:
                assert isinstance(e, AbstractVariable)
                ixn_terms.append(e.name)
            mult = "*"
            if xs_code is None:
                xs_code = f"{mult.join(ixn_terms)}"
            else:
                xs_code += f" + {mult.join(ixn_terms)}"

        formula_code = "formula=" + '"' + y_code + " ~ " + xs_code + '"'
        data_code = "data=df"
        model_code = model + "(" + formula_code + "," + data_code + ","

    ## LINK
    link = statistical_model.link_function.upper()
    link_code = "sm.families.links."
    if "IDENTITY" in link:
        link_code += "identity()"
    elif "LOG" in link and "LOGLOG" not in link:
        link_code += "log()"
    elif "CLOGLOG" in link:
        link_code += "cloglog()"
    elif "SQUAREROOT" in link:
        raise NotImplementedError
    elif "INVERSE" in link and "SQUARED" not in link:
        link_code += "inverse_power()"
    elif "INVERSESQUARED" in link:
        link_code += "inverse_squared()"
    elif "POWER" in link:
        link_code += "Power()"
    elif "CAUCHY" in link:
        link_code += "cauchy()"
    elif "LOGLOG" in link:
        link_code += ""
    elif "PROBIT" in link:
        link_code += "probit()"
    elif "LOGIT" in link:
        # The default link for the Binomial family is the logit link. Available links are logit, probit, cauchy, log, and cloglog.
        link_code += "Logit()"
    elif "NEGATIVEBINOMIAL" in link:
        # Optional parameter to pass to underlying nbinom function
        if "alpha" in kwargs:
            link_code += f"nbinom({alpha})"
        link_code += "nbinom()"

    ## FAMILY
    family = statistical_model.family.upper()
    # BINOMIAL
    if "BINOMIAL" in family.upper() and "NEGATIVE" not in family.upper():
        family_code = f"sm.families.Binomial({link_code})"
    # GAMMA
    elif "GAMMA" in family.upper():
        family_code = f"sm.families.Gamma({link_code})"
    # GAUSSIAN
    elif "GAUSSIAN" in family.upper() and "INVERSE" not in family.upper():
        family_code = f"sm.families.Gaussian({link_code})"
    # INVERSEGAUSSIAN
    elif "INVERSEGAUSSIAN" in family.upper():
        family_code = f"sm.families.InverseGaussian({link_code})"
    # NEGATIVEBINOMIAL
    elif "NEGATIVEBINOMIAL" in family.upper():
        # Optional parameter to pass to family function
        if "alpha" in kwargs:
            alpha = kawrgs["alpha"]
            family_code = f"sm.families.NegativeBinomial({link_code}, {alpha})"
        family_code = f"sm.families.NegativeBinomial({link_code})"
    # POISSON
    elif "POISSON" in family.upper():
        family_code = f"sm.families.Poisson({link_code})"
    # TWEEDIE
    elif "TWEEDIE" in family.upper():
        # Optional parameter to pass to underlying nbinom function Notes in
        # statssmodels v0.12.2 doc: "If True, the Extended Quasi-Likelihood is used,
        # else the likelihood is used (however the latter is not
        # implemented). If eql is True, var_power must be between 1 and 2."
        if "var_power" in kwargs:
            var_power = int(kwargs["var_power"])
            if var_power > 1 and var_power < 2:
                family_code = f"sm.families.Tweedie({link_code}, {var_power}, eql=True)"
        family_code = f"sm.families.Tweedie({link_code})"

    ## Assemble and update model
    model_code += "family=" + family_code + ")"

    return model_code


def generate_statsmodels_glmm_code(statistical_model: StatisticalModel, **kwargs):
    family = statistical_model.family
    link = statistical_model.link_function

    # Intercept added automatically with formula unless specified otherwise
    if "no_intercept" in kwargs:
        model = sm.GLM

        # TODO: Might not need to get data again, just reuse existing code in "outer" code gen function
    else:
        pass

    model = "model = "
    ## FAMILY
    # BINOMIAL
    if "BINOMIAL" in family.upper() and "NEGATIVE" not in family.upper():
        model += f"BinomialBayesMixedGLM"
    # GAMMA
    elif "GAMMA" in family.upper():
        raise NotImplementedError
    # GAUSSIAN
    elif "GAUSSIAN" in family.upper() and "INVERSE" not in family.upper():
        # model += f'smf.mixedlm'
        # TODO: CHECK THAT LINK IS IDENTITY AS WELL
        model += f"sm.MixedLM.from_formula"
    # INVERSEGAUSSIAN
    elif "INVERSEGAUSSIAN" in family.upper():
        raise NotImplementedError
    # NEGATIVEBINOMIAL
    elif "NEGATIVEBINOMIAL" in family.upper():
        raise NotImplementedError
    # POISSON
    elif "POISSON" in family.upper():
        model += f"PoissonBayesMixedGLM"

    ## Build FORMULA
    y = statistical_model.dv
    y_code = f"{y.name}"
    xs_code = None
    for f in statistical_model.fixed_ivs:
        if xs_code is None:
            xs_code = f"{f.name}"
        else:
            xs_code += f" + {f.name}"
    for interaction in statistical_model.interactions:
        ixn_terms = list()
        for e in interaction:
            assert isinstance(e, AbstractVariable)
            ixn_terms.append(e.name)
        mult = "*"
        if xs_code is None:
            xs_code = f"{mult.join(ixn_terms)}"
        else:
            xs_code += f" + {mult.join(ixn_terms)}"

    # Ex: vc = {'classroom': '0 + C(classroom)'}
    vc = "vc_formula = {"  # For storing the variance components or random intercepts and slopes
    vc_started = False
    groups = "groups = "  # For random slopes
    re_formula = 're_formula = "1'
    exactly_one_group = False

    for re in statistical_model.random_ivs:
        if isinstance(re, RandomIntercept):
            if vc_started:
                vc += " , "
            vc += f'"{re.groups.name}" : ' + f'"0 + C({re.groups.name})"'
            vc_started = True

        elif isinstance(re, CorrelatedRandomSlopeAndIntercept):
            group = re.groups
            if vc_started:
                vc += " , "
            vc += f'"{re.groups.name}" : ' + f'"0 + C({re.groups.name})"'
            vc_started = True
            groups += f'"{group.name}"'
            exactly_one_group = not exactly_one_group

            iv = re.iv
            assert iv.name in xs_code  # Make sure the iv is included as an IV/X already
            re_formula += " + " + f'{iv.name}"'
        elif isinstance(re, UncorrelatedRandomSlopeAndIntercept):
            group = re.groups
            if vc_started:
                vc += " , "
            vc += f'"{re.groups.name}" : ' + f'"0 + C({re.groups.name})"'
            vc_started = True
            groups += f'"{group.name}"'
            exactly_one_group = not exactly_one_group

            iv = re.iv
            assert iv.name in xs_code  # Make sure the iv is included as an IV/X already
        elif isinstance(re, RandomSlope):
            group = re.groups
            random_slope = f'"{group.name}"'
            groups += random_slope
            exactly_one_group = not exactly_one_group

            iv = re.iv
            # if iv.name not in xs_code:
            #     import pdb; pdb.set_trace()
            # assert(iv.name in xs_code) # Make sure the iv is included as an IV/X already
            re_formula += " + " + f'{iv.name}"'
        # print(re)

    vc += "}"  # Add closing curly brace

    formula_code = "formula=" + '"' + y_code + " ~ " + xs_code + '"'
    data_code = "data=df"
    model_code = (
        model
        + "("
        + formula_code
        + ","
        + vc
        + ","
        + re_formula
        + ","
        + groups
        + ","
        + data_code
        + ")"
    )

    return model_code


# def generate_statsmodels_model_code(statistical_model: StatisticalModel, **kwargs):
#     model_code = str()

#     has_fixed = len(statistical_model.fixed_ivs) > 0
#     has_interactions = len(statistical_model.interactions) > 0
#     has_random = len(statistical_model.random_ivs) > 0
#     has_data = statistical_model.data is not None  # May not have data

#     # Does the statistical model have random effects (slope or intercept) that we should take into consideration?
#     if has_random:
#         return generate_statsmodels_glmm_code(statistical_model=statistical_model)
#     else:
#         # GLM: Fixed, interactions, no random; Other family
#         return generate_statsmodels_glm_code(statistical_model=statistical_model)
