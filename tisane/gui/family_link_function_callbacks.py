from dash.dependencies import Output, Input, State, ALL, MATCH
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

def filterOutput(comp: GUIComponents):
    logger = logging.getLogger("werkzeug")
    logger.debug("Raw output: {}".format(json.dumps(comp.output, indent=4)))
    newOutput = {
        "main effects": sorted(comp.output["main effects"]),
        "interaction effects": sorted(comp.output["interaction effects"]),
        "dependent variable": comp.output["dependent variable"],
        "family": comp.output["family"],
        "link": comp.output["link"],
        "random effects": {}
    }
    if "random effects" in comp.output:
        for group, randomEffects in comp.output["random effects"].items():
            groupDict = {}
            if "random intercept" in randomEffects:
                randIntercept = randomEffects["random intercept"]
                if "unavailable" in randIntercept:
                    if not randIntercept["unavailable"]:
                        groupDict["random intercept"] = {key: value for key, value in randIntercept.items() if key != "unavailable"}
                        pass
                    pass
                else:
                    groupDict["random intercept"] = randIntercept
                pass
            if "random slope" in randomEffects:
                randSlope = randomEffects["random slope"]
                for rs in randSlope:
                    if "unavailable" in rs:
                        if not rs["unavailable"]:
                            if "random slope" not in groupDict:
                                groupDict["random slope"] = []
                                pass
                            groupDict["random slope"].append(
                                {key: value for key, value in rs.items() if key != "unavailable"}
                            )
                            pass
                        pass
                    else:
                        groupDict["random slope"].append(rs)
                        pass
                    pass
                pass
            if groupDict:
                if "random slope" in groupDict:
                    groupDict["random slope"] = sorted(groupDict["random slope"], key=lambda rs: rs["iv"])
                newOutput["random effects"][group] = groupDict
            pass
        pass
    return newOutput

def createGenerateCodeCallback(app, comp: GUIComponents = None):
    @app.callback(
        Output("modal-data-store", "data"), Input("generate-code", "n_clicks")
    )
    def generateCodeCallback(nclicks):
        if comp and nclicks:
            result = comp.generateCode()
            if result:
                resultObject = {
                    "path": str(result)
                }
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
        State("code-generated-modal", "is_open")
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
                                dcc.Clipboard(target_id="copy-target-id",
                                              style={
                                                  "position": "absolute",
                                                  "top": 0,
                                                  "right": 10
                                              })
                            ],
                        #     style={
                        #         "position": "relative"
                        #     }
                        # ),
                        className="bg-light",
                        style={
                            "position": "relative",
                            "padding": "5px"
                        }
                    )
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
        Input("family-options", "value"),
    )
    def updateLinkOptions(value):
        if not comp:
            print("Cannot update")
            raise PreventUpdate
        comp.output["family"] = value
        familyLinks = comp.getGeneratedFamilyLinkFunctions()
        logger.debug("{}: {}".format(value, type(value)))
        if value and isinstance(value, str):
            logger.debug(familyLinks)
            if value in familyLinks:
                defaultLink = comp.getDefaultLinkForFamily(value)
                familyName = " ".join(separateByUpperCamelCase(value)[:-1])
                return (
                    [
                        {
                            "label": " ".join(separateByUpperCamelCase(str(l)))
                            + ("*" if defaultLink == l else ""),
                            "value": str(l),
                        }
                        for l in familyLinks[value]
                    ],
                    defaultLink,
                    "Family: {}".format(familyName),
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
