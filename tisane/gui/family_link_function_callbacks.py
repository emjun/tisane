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

def assertHasKey(k, d):
    assert k in d, f"Could not find {k} in {d}"

def createFamilyLinkFunctionCallbacks(app, comp: GUIComponents = None):
    createLinkFunctionCallbacks(app, comp)
    createChartCallbacks(app, comp)
    createGenerateCodeCallback(app, comp)
    createQuestionCallback(app, comp)
    pass

def createQuestionCallback(app, comp: GUIComponents = None):
    def questionWithoutFollowUpCallback(questionDropdownValue):
        if not questionDropdownValue:
            return ([], True, "")
        assert comp is not None, "comp none in createQuestionCallback"
        typesOfData = comp.getTypesOfData()
        assert typesOfData is not None
        assertHasKey("answers", typesOfData)
        assertHasKey(questionDropdownValue, typesOfData["answers"])
        # assert questionDropdownValue in typesOfData["answers"], f"Could not find {questionDropdownValue} in {typesOfData}"
        assertHasKey("family-options", typesOfData["answers"][questionDropdownValue])

        familyOptionsOptions = comp.createFamilyOptionsFromValues(typesOfData["answers"][questionDropdownValue]["family-options"])

        return (familyOptionsOptions, False, "")

        pass

    def questionWithFollowUpCallback(questionDropdownValue, followUpLabel):
        if not questionDropdownValue:
            return ([], True, followUpLabel)
        assert comp is not None, "comp none in createQuestionCallback"
        typesOfData = comp.getTypesOfData()
        assert typesOfData is not None
        assert "answers" in typesOfData
        assertHasKey(questionDropdownValue, typesOfData["answers"])
        # assert questionDropdownValue in typesOfData["answers"], f"Could not find {questionDropdownValue} in {typesOfData}"
        assertHasKey("follow-up", typesOfData["answers"][questionDropdownValue])
        followUps = typesOfData["answers"][questionDropdownValue]["follow-up"]

        # nonFalse = [k for k in followUps if k != "false"]
        # assert len(nonFalse) == 1, f"Expected exactly one non-false option, but found {nonFalse}"
        # followUpTitle = comp.strings("types-of-data", "follow-ups", nonFalse)
        followUpTitle = followUps["question"]
        followUpOptions = [dict(disabled=False,
                                label=comp.strings("types-of-data", "display-types", k),
                                value=k) for k in followUps["answers"]]

        return (followUpOptions,
                False,
                followUpTitle + " ")

    def followUpCallback(followUpQuestionValue, questionValue, followUpLabel):
        assert comp is not None, "comp none in createQuestionCallback"
        if followUpQuestionValue == "":
            return (
                # [],
                # True,
                # "",
                #comp.strings("types-of-data", "follow-ups", "default"),
                followUpLabel,
                True,
                "",
                [],
                {}
            )
        typesOfData = comp.getTypesOfData()
        assert typesOfData, f"Expected typesOfData to be non-none/non-empty, but got {typesOfData}"
        assertHasKey("answers", typesOfData)
        current = typesOfData["answers"]
        assert questionValue in current, f"Expected questionValue to be in typesOfData, but got {questionValue}, {current}"
        current = current[questionValue]
        assertHasKey("follow-up", current)
        current = current["follow-up"]
        assertHasKey("answers", current)

        current = current["answers"]

        assert followUpQuestionValue in current, "Expected followUpQuestionValue to be in typesOfData[answers][questionValue][follow-up][answers], but got {}, {}".format(followUpQuestionValue, current)

        for k in ["question", "answers"]:
            assertHasKey(k, typesOfData["answers"][questionValue]["follow-up"])
        print(current)

        current = current[followUpQuestionValue]

        if "follow-up" in current:
            return (
                # [], True, "",
                followUpLabel, False, current["follow-up"]["question"], [dict(value=k, label=comp.strings("types-of-data", "display-types", k)) for k in current["follow-up"]["answers"]],
                {}
            )

        assertHasKey("family-options", current)

        families = current["family-options"]
        familyOptions = comp.createFamilyOptionsFromValues(families)
        familyDisabled = False
        familyValue = "" if len(families) != 1 else families[0]

        hideFollowUpDiv = True

        storeUpdate = {
            "options": familyOptions,
            "disabled": familyDisabled,
            "value": familyValue
        }

        return (
            # familyOptions, familyDisabled, familyValue,
            followUpLabel, hideFollowUpDiv, "", [], storeUpdate
        )

    def updateFollowUpLabel(store1, store2, currentLabel):
        context = dash.callback_context

        if not context.triggered:
            return currentLabel

        triggerers = ["follow-up-label-store-1", "follow-up-label-store-2"]

        storeTriggers = [t for t in context.triggered if any(t["prop_id"].startswith(tr) for tr in triggerers)]

        assert len(storeTriggers) >= 1, f"Expected at least one triggering store for context {context}"

        first = storeTriggers[0]

        if not all(s["value"] == first["value"] for s in storeTriggers):
            assert len(storeTriggers) == 1, f"Expected only one triggering store, but got {storeTriggers}"

        triggered = storeTriggers[0]
        assert triggered["prop_id"].find(".") != -1, "Could not find \".\" in {}".format(triggered["prop_id"])
        storeId = triggered["prop_id"].split(".")[0]
        if storeId.endswith("1"):
            return store1
        return store2


    def updateFamilyOptions(store1, options, disabled, value):
        context = dash.callback_context
        if not context.triggered or not store1:
            return (options, disabled, value)
        triggerIds = ["family-options-store-1", "family-options-store-2"]

        storeTriggers = [t for t in context.triggered if any(t["prop_id"].startswith(tr) for tr in triggerIds)]

        assert len(storeTriggers) >= 1, f"Expected at least one triggering store for context {context}"

        first = storeTriggers[0]
        id = first["prop_id"].split(".")[0]
        retVal = (store1["options"], store1["disabled"], store1["value"])
        if id.endswith("1"):
            return retVal
        return retVal




    if comp.shouldEnableTypesOfDataControls():
        if comp.shouldEnableFollowUp():
            app.callback(
                Output("family-options", "options"),
                Output("family-options", "disabled"),
                Output("family-options", "value"),
                Input("family-options-store-1", "data"),
                State("family-options", "options"),
                State("family-options", "disabled"),
                State("family-options", "value")
            )(updateFamilyOptions)
            app.callback(
                Output("follow-up-options", "options"),
                Output("follow-up-options", "disabled"),
                Output("follow-up-label-store-1", "data"),
                Input("question-options", "value"),
                State("follow-up-label", "children")
                )(questionWithFollowUpCallback)

            app.callback(
                # Output("family-options", "options"),
                # Output("family-options", "disabled"),
                # Output("family-options", "value"),
                Output("follow-up-label-store-2", "data"),
                Output("follow-up-1-div", "hidden"),
                Output("follow-up-label-1", "children"),
                Output("follow-up-options-1", "options"),
                Output("family-options-store-1", "data"),
                Input("follow-up-options", "value"),
                State("question-options", "value"),
                State("follow-up-label", "children")
            )(followUpCallback)

            app.callback(
                Output("follow-up-label", "children"),
                Input("follow-up-label-store-1", "data"),
                Input("follow-up-label-store-2", "data"),
                State("follow-up-label", "children")
            )(updateFollowUpLabel)
            pass
        else:
            app.callback(
                Output("family-options", "options"),
                Output("family-options", "disabled"),
                Output("family-options", "value"),
                Input("question-options", "value")
                )(questionWithoutFollowUpCallback)

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
                            html.Code(
                                str(dataObject["path"]), id="copy-target-id"),
                            dcc.Clipboard(
                                target_id="copy-target-id",
                                style={"position": "absolute",
                                       "top": 0, "right": 10},
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
        Output("link-options", "disabled"),
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
        buttonDisabledStyle = {"pointer-events": "none"}
        buttonEnabledStyle = {}
        if oldFamily and not value:
            return [], "", True, "", True, buttonDisabledStyle, ""
        familyLinks = comp.getGeneratedFamilyLinkFunctions()
        logger.debug("{}: {}".format(value, type(value)))
        if value and isinstance(value, str):
            # print("Updating...")
            logger.debug(familyLinks)
            if value in familyLinks:
                defaultLink = comp.getDefaultLinkForFamily(value)
                comp.output["link"] = defaultLink
                fls = comp.getFamilyLinkFunctions()
                assert value in fls, "Family {} not found in {}".format(
                    value, fls)
                familyName = " ".join(separateByUpperCamelCase(value)[:-1])
                return (
                    [
                        {
                            "label": " ".join(separateByUpperCamelCase(str(l))[:-1])
                            + ("*" if defaultLink == l else ""),
                            "value": str(l),
                            "disabled": str(l) not in fls[value]["links"],
                            }
                        for l in familyLinks[value]
                        ],
                    defaultLink,
                    False,
                    "Family: {}".format(familyName),
                    False,
                    buttonEnabledStyle,
                    "tooltip-hide",
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
    # @app.callback(
    #     Output("family-link-chart", "figure"), Input("family-options", "value")
    # )
    # def update_chart_family(family):
    #     if family is not None and comp:
    #         assert isinstance(family, str)
    #         # return comp.createGraph(family)
    #         return comp.createFigure(family)
    #
    #     else:
    #         raise PreventUpdate
    pass


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
