from dash.dependencies import Output, Input, State, ALL, MATCH, ClientsideFunction
import dash
from dash.exceptions import PreventUpdate
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from tisane.gui.gui_components import GUIComponents, separateByUpperCamelCase
import numpy as np
import plotly.graph_objects as go
import tweedie
from scipy.special import logit
from scipy import stats
import pandas as pd
from tisane.gui.gui_helpers import simulate_data_dist, getTriggeredFromContext
import json
import os
import logging


def createFamilyLinkFunctionCallbacks(app, comp: GUIComponents = None):
    createLinkFunctionCallbacks(app, comp)
    createChartCallbacks(app, comp)
    createGenerateCodeCallback(app, comp)
    pass


def createGenerateCodeCallback(app, comp: GUIComponents = None):
    @app.callback(
        Output("modal-data-store", "data"), Input("generate-code", "n_clicks")
    )
    def generateCodeCallback(nclicks):
        if comp and nclicks:
            result = comp.generateCode()
            if result:
                resultObject = {"path": str(result)}
                comp.highestActiveTab = 5
            else:
                resultObject = {
                    "error": "No code generator provided. Did you not run the GUI using `tisane.infer_statistical_model_from_design`?"
                }
            return json.dumps(resultObject)
            # newOutput = filterOutput(comp)
            #
            # with open("model_spec.json", "w") as f:
            #     f.write(json.dumps(newOutput, indent=4, sort_keys=True))
            #     pass
            # pass
        raise PreventUpdate

    @app.callback(
        Output("code-generated-modal", "is_open"),
        Output("close-code-generated-modal", "n_clicks"),
        Output("code-generated-modal-header", "children"),
        Output("code-generated-modal-body", "children"),
        Input("close-code-generated-modal", "n_clicks"),
        Input("modal-data-store", "data"),
        State("code-generated-modal", "is_open"),
    )
    def closeModal(n_clicks, data, is_open):
        ctx = dash.callback_context
        triggered = getTriggeredFromContext(ctx)
        codeGenerated = "Code Generated!"
        if triggered:
            if triggered == "close-code-generated-modal" and n_clicks > 0:
                return (False, 0, "Code Generated!", "Placeholder")
            dataObject = json.loads(data) if data else {}
            if "path" in dataObject:
                bodyText = [
                    "Code has been generated! The model script is located at",
                    html.Div(
                        # dbc.CardBody(
                        [
                            html.Code(str(dataObject["path"]), id="copy-target-id"),
                            dcc.Clipboard(
                                target_id="copy-target-id",
                                style={"position": "absolute", "top": 0, "right": 10},
                            ),
                        ],
                        #     style={
                        #         "position": "relative"
                        #     }
                        # ),
                        className="bg-light",
                        style={"position": "relative", "padding": "5px"},
                    ),
                ]
                return (True, 0, codeGenerated, bodyText)
            elif "error" in dataObject:
                header = "Error!"
                body = dcc.Markdown(dataObject["error"])
                return (True, 0, header, body)
            pass
        raise PreventUpdate


def createLinkFunctionCallbacks(app, comp: GUIComponents = None):
    logger = logging.getLogger("werkzeug")

    @app.callback(
        Output("link-options", "options"),
        Output("link-options", "value"),
        Output("overview-family", "children"),
        Output("generate-code", "disabled"),
        Output("generate-code", "style"),
        Output("generate-code-tooltip", "className"),
        Input("family-options", "value"),
    )
    def updateLinkOptions(value):
        if not comp:
            logger.warning("Cannot update")
            raise PreventUpdate
        oldFamily = comp.output["family"]
        comp.output["family"] = value
        buttonDisabledStyle = {
            "pointer-events": "none"
        }
        buttonEnabledStyle = {}
        if oldFamily and not value:
            return [], "", "", True, buttonDisabledStyle, ""
        familyLinks = comp.getGeneratedFamilyLinkFunctions()
        logger.debug("{}: {}".format(value, type(value)))
        if value and isinstance(value, str):
            # print("Updating...")
            logger.debug(familyLinks)
            if value in familyLinks:
                defaultLink = comp.getDefaultLinkForFamily(value)
                comp.output["link"] = defaultLink
                fls = comp.getFamilyLinkFunctions()
                assert value in fls, "Family {} not found in {}".format(value, fls)
                familyName = " ".join(separateByUpperCamelCase(value)[:-1])
                return (
                    [
                        {
                            "label": " ".join(separateByUpperCamelCase(str(l))[:-1])
                            + ("*" if defaultLink == l else ""),
                            "value": str(l),
                            "disabled": str(l) not in fls[value]["links"]
                        }
                        for l in familyLinks[value]
                    ],
                    defaultLink,
                    "Family: {}".format(familyName),
                    False,
                    buttonEnabledStyle,
                    "tooltip-hide"
                )
            pass
        logger.warning("Cannot update for some reason")
        raise PreventUpdate

    @app.callback(Output("overview-link", "children"), Input("link-options", "value"))
    def updateLinkOverview(value):
        if comp:
            comp.output["link"] = value
        if value:
            return "Link: {}".format(" ".join(separateByUpperCamelCase(value)[:-1]))
        raise PreventUpdate


def createChartCallbacks(app, comp: GUIComponents = None):
    @app.callback(
        Output("family-link-chart", "figure"), Input("family-options", "value")
    )
    def update_chart_family(family):
        if family is not None and comp:
            assert isinstance(family, str)
            # return comp.createGraph(family)
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
