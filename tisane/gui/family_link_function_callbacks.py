from dash.dependencies import Output, Input, State, ALL, MATCH
import dash
from dash.exceptions import PreventUpdate
import dash_html_components as html
from tisane.gui.gui_components import GUIComponents, separateByUpperCamelCase
import numpy as np
import plotly.graph_objects as go
import tweedie
from scipy.special import logit
from scipy import stats
import pandas as pd
from tisane.gui.gui_helpers import simulate_data_dist


def createFamilyLinkFunctionCallbacks(app, comp: GUIComponents = None):
    createLinkFunctionCallbacks(app, comp)
    createChartCallbacks(app, comp)
    pass

def createLinkFunctionCallbacks(app, comp: GUIComponents = None):
    @app.callback(
        Output("link-options", "options"),
        Output("link-options", "value"),
        Input("family-options", "value")
    )
    def updateLinkOptions(value):
        if not comp:
            print("Cannot update")
            raise PreventUpdate
        familyLinks = comp.getGeneratedFamilyLinkFunctions()
        print("{}: {}".format(value, type(value)))
        if value and isinstance(value, str):
            print(familyLinks)
            if value in familyLinks:
                assert "Identity"
                return [
                    {
                        "label": " ".join(separateByUpperCamelCase(str(l))),
                        "value": str(l)
                    } for l in familyLinks[value]
                ], "IdentityLink"
            pass
        print("Cannot update for some reason")
        raise PreventUpdate


def createChartCallbacks(app, comp: GUIComponents = None):
    @app.callback(
        Output("family-link-chart", "figure"),
        Input("family-options", "value")
    )
    def update_chart_family(family):
        if family is not None and comp:
            assert isinstance(family, str)

            return comp.createFigure(family)

        else:
            raise PreventUpdate

def transform_data_from_fact(data: np.ndarray, link_fact: str):
    if "IdentityLink" == link_fact:
        # Do nothing
        return data
    elif "LogLink" == link_fact:
        return np.log(data)
    elif "CLogLogLink" == link_fact:
        raise np.log(-np.log(1 - data))
    elif "SquarerootLink" == link_fact:
        return np.sqrt(data)
    elif "InverseLink" == link_fact:
        raise NotImplementedError
    elif "InverseSquaredLink" == link_fact:
        raise NotImplementedError
    elif "PowerLink" == link_fact:
        transformed_data = stats.boxcox(data["data"])[0]
        return pd.DataFrame(data=transformed_data)
    elif "CauchyLink" == link_fact:
        raise NotImplementedError
    elif "LogLogLink" == link_fact:
        raise NotImplementedError
    elif "ProbitLink" == link_fact:
        raise NotImplementedError
    elif "LogitLink" == link_fact:
        # TODO: make sure that the values are numbers
        transformed_data = logit(data["data"])
        return transformed_data
    elif "NegativeBinomialLink" == link_fact:
        raise NotImplementedError
