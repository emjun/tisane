from dash.dependencies import Output, Input, State, ALL, MATCH
import dash
from dash.exceptions import PreventUpdate
import dash_html_components as html
from tisane.gui.gui_components import GUIComponents
from tisane.gui.family_link_function_callbacks import createFamilyLinkFunctionCallbacks
from tisane.gui.random_effects_callbacks import createRandomEffectsCallbacks
import json
from tisane.gui.gui_helpers import getTriggeredFromContext
import logging


def createCallbacks(app, comp: GUIComponents = None):
    cont_to_interaction_effects_input = Input(
        "continue-to-interaction-effects", "n_clicks"
    )
    createMainEffectsProgressBarCallbacks(app, comp)
    createProgressBarCallbacks(
        app,
        "tab-2",
        "interaction-effects-progress",
        "continue-to-interaction-effects",
        "continue-to-random-effects",
        comp,
    )
    createProgressBarCallbacks(
        app,
        "tab-3",
        "random-effects-progress",
        "continue-to-random-effects",
        "continue-to-family-link-functions",
        comp,
    )
    createTabsCallbacks(app)
    createMainEffectsChecklistCallbacks(app, comp)
    createFamilyLinkFunctionsProgressCallbacks(app, comp)
    createInteractionEffectsChecklistCallbacks(app, comp)
    createFamilyLinkFunctionCallbacks(app, comp)
    createRandomEffectsCallbacks(app, comp)
    # createTestDivCallbacks(app)
    pass


def createTestDivCallbacks(app):
    @app.callback(Output("test-div-output", "children"), Input("test-div", "children"))
    def testDivCallback(children):
        return str(children)


# def getTriggeredFromContext(ctx):
#     if not ctx.triggered:
#         return False
#     return ctx.triggered[0]["prop_id"].split(".")[0]


def createTransitionCallback(
    app, tabA, tabB, tabA_id, progressA, progressB, continue_button_id
):
    def goToInteractionEffects(n_clicks):
        # print(n_clicks)
        if n_clicks:
            return True, True, "primary"
        return False, False, "secondary"

    app.callback(
        Output(progressB, "animated"),
        Output(progressB, "striped"),
        Output(progressB, "color"),
        [Input(continue_button_id, "n_clicks")],
    )(goToInteractionEffects)

    pass


def createTabsCallbacks(app):
    logger = logging.getLogger("werkzeug")

    def continueCallback(fromMain, fromInteraction, fromRandom):
        ctx = dash.callback_context
        triggered = getTriggeredFromContext(ctx)
        logger.debug("Continue callback: {}".format(triggered))
        if triggered:
            if triggered == "continue-to-interaction-effects":
                return "tab-2"
            elif triggered == "continue-to-random-effects":
                return "tab-3"
            elif triggered == "continue-to-family-link-functions":
                return "tab-4"
        raise PreventUpdate

    app.callback(
        Output("tabs", "active_tab"),
        Input("continue-to-interaction-effects", "n_clicks"),
        Input("continue-to-random-effects", "n_clicks"),
        Input("continue-to-family-link-functions", "n_clicks"),
    )(continueCallback)


mytabs = ["tab-1", "tab-2", "tab-3", "tab-4"]


def createMainEffectsChecklistCallbacks(app, comp: GUIComponents = None):
    logger = logging.getLogger("werkzeug")
    mainEffectCompIds = comp.getMainEffectCheckboxIds()
    inputs = [Input(id, "checked") for id in mainEffectCompIds]
    states = [State(id, "id") for id in mainEffectCompIds]

    @app.callback(
        Output("added-main-effects", "children"),
        Output("added-main-effects-store", "data"),
        inputs,
        states,
    )
    def addVariables(*args):
        if not comp:
            logger.warning("Cannot update added-main-effects")
            raise PreventUpdate

        # print(options)
        if not args:
            raise PreventUpdate
        assert (
            len(args) % 2 == 0
        ), "Weird length of args for added-main-effects callback"
        half = int(len(args) / 2)
        inputs = args[:half]
        states = args[half:]
        options = []
        for i in range(len(inputs)):
            id = states[i]
            checked = inputs[i]
            if checked and comp.hasMainEffectForComponentId(id):
                mainEffect = comp.getMainEffectFromComponentId(id)
                if mainEffect not in comp.output["main effects"]:
                    comp.output["main effects"].append(mainEffect)
                options.append(mainEffect)
                pass
            elif not checked and comp.hasMainEffectForComponentId(id):
                mainEffect = comp.getMainEffectFromComponentId(id)
                if mainEffect in comp.output["main effects"]:
                    comp.output["main effects"].remove(mainEffect)
            pass
        newChildren = [html.Li(o) for o in options]
        logger.debug("New children: {}".format(newChildren))
        return newChildren, json.dumps(comp.output)

    pass


def createInteractionEffectsChecklistCallbacks(app, comp: GUIComponents = None):
    logger = logging.getLogger("werkzeug")
    if comp and comp.hasInteractionEffects():
        interactionEffectCompIds = comp.getInteractionEffectCheckboxIds()
        inputs = [Input(id, "checked") for id in interactionEffectCompIds]
        states = [State(id, "id") for id in interactionEffectCompIds]

        def addVariables(*args):
            if not comp:
                logger.warning("Cannot update added-interaction-effects")
                raise PreventUpdate
            if not args:
                raise PreventUpdate
            assert (
                len(args) % 2 == 0
            ), "Weird length of args for added-interaction-effects callback"
            half = int(len(args) / 2)
            inputs = args[:half]
            states = args[half:]
            options = []
            for i in range(len(inputs)):
                id = states[i]
                checked = inputs[i]
                if checked and comp.hasInteractionEffectForComponentId(id):
                    interactionEffect = comp.getInteractionEffectFromComponentId(id)
                    if interactionEffect not in comp.output["interaction effects"]:
                        comp.output["interaction effects"].append(interactionEffect)
                    options.append(interactionEffect)
                    pass
                elif not checked and comp.hasInteractionEffectForComponentId(id):
                    interactionEffect = comp.getInteractionEffectFromComponentId(id)
                    if interactionEffect in comp.output["interaction effects"]:
                        comp.output["interaction effects"].remove(interactionEffect)
                    pass
                pass
            newChildren = [html.Li(o) for o in options]
            logger.debug("New children: {}".format(newChildren))
            return newChildren, json.dumps(comp.output)

        app.callback(
            Output("added-interaction-effects", "children"),
            Output("added-interaction-effects-store", "data"),
            inputs,
            states,
        )(addVariables)


def createFamilyLinkFunctionsProgressCallbacks(app, comp: GUIComponents = None):
    logger = logging.getLogger("werkzeug")

    def animatedCallback(nclicks, active_tab):
        ctx = dash.callback_context
        if not ctx.triggered:
            raise PreventUpdate
        logger.debug(ctx.triggered)
        triggered = getTriggeredFromContext(ctx)
        if triggered == "tabs":
            mybool = active_tab == "tab-4" or (
                comp
                and comp.highestActiveTab >= mytabs.index("tab-4")
                and mytabs.index(active_tab) < mytabs.index("tab-4")
            )
            return mybool, mybool
        if triggered == "continue-to-family-link-functions":
            return True, True
        return False, False

    app.callback(
        Output("family-link-functions-progress", "animated"),
        Output("family-link-functions-progress", "striped"),
        Input("continue-to-family-link-functions", "n_clicks"),
        Input("tabs", "active_tab"),
    )(animatedCallback)

    def colorCallback(nclicksto, nclicksfrom, active_tab):
        ctx = dash.callback_context
        triggered = getTriggeredFromContext(ctx)
        if comp.highestActiveTab < mytabs.index(active_tab):
            comp.highestActiveTab = mytabs.index(active_tab)
        logger.debug(
            "{}, {}: {}, {}".format(
                "tab-4", "family-link-functions-progress", triggered, active_tab
            )
        )
        if triggered:
            if triggered == "generate-code" or (
                comp and comp.highestActiveTab > mytabs.index(active_tab)
            ):
                return "success"
            if triggered == "continue-to-family-link-functions" or mytabs.index(
                active_tab
            ) == mytabs.index("tab-4"):
                return "primary"
        raise PreventUpdate

    app.callback(
        Output("family-link-functions-progress", "color"),
        Input("generate-code", "n_clicks"),
        Input("continue-to-family-link-functions", "n_clicks"),
        Input("tabs", "active_tab"),
    )(colorCallback)


def createProgressBarCallbacks(
    app, triggered_tab, progressid, continuefrom_id, continueto_id, comp: GUIComponents
):
    logger = logging.getLogger("werkzeug")

    def animatedCallback(nclicks, active_tab):
        ctx = dash.callback_context
        index = mytabs.index(active_tab)
        if not ctx.triggered:
            return True, True
        logger.debug(ctx.triggered)
        triggered = getTriggeredFromContext(ctx)
        if triggered == "tabs":
            myBool = active_tab == triggered_tab or (
                comp
                and comp.highestActiveTab >= mytabs.index(triggered_tab)
                and mytabs.index(active_tab) < mytabs.index(triggered_tab)
            )
            return myBool, myBool
        return False, False

    app.callback(
        Output(progressid, "animated"),
        Output(progressid, "striped"),
        Input(continueto_id, "n_clicks"),
        Input("tabs", "active_tab"),
    )(animatedCallback)

    def colorCallback(nclicksto, nclicksfrom, active_tab):
        ctx = dash.callback_context
        triggered = getTriggeredFromContext(ctx)
        tabIndex = mytabs.index(active_tab)
        if comp and comp.highestActiveTab < tabIndex:
            comp.highestActiveTab = tabIndex
        logger.debug(
            "{}, {}: {}, {}".format(triggered_tab, progressid, triggered, active_tab)
        )
        if triggered:
            if (
                triggered == continueto_id
                or mytabs.index(active_tab) > mytabs.index(triggered_tab)
                or (
                    comp
                    and comp.highestActiveTab >= 0
                    and comp.highestActiveTab > mytabs.index(triggered_tab)
                )
            ):
                return "success"
            if triggered == continuefrom_id or mytabs.index(
                triggered_tab
            ) == mytabs.index(active_tab):
                return "primary"
        raise PreventUpdate

    app.callback(
        Output(progressid, "color"),
        Input(continueto_id, "n_clicks"),
        Input(continuefrom_id, "n_clicks"),
        Input("tabs", "active_tab"),
    )(colorCallback)


def createMainEffectsProgressBarCallbacks(app, comp: GUIComponents = None):
    logger = logging.getLogger("werkzeug")

    def animatedCallback(nclicks_main, nclicks_interaction, active_tab):
        ctx = dash.callback_context
        if not ctx.triggered:
            return True, True
        logger.debug(ctx.triggered)
        triggered = getTriggeredFromContext(ctx)
        if triggered == "tabs":
            return active_tab == "tab-1", active_tab == "tab-1"
        return False, False

    app.callback(
        Output("main-effects-progress", "animated"),
        Output("main-effects-progress", "striped"),
        Input("continue-to-interaction-effects", "n_clicks"),
        Input("continue-to-random-effects", "n_clicks"),
        Input("tabs", "active_tab"),
    )(animatedCallback)

    def colorCallback(nclicks_main, active_tab):
        if comp and comp.highestActiveTab < mytabs.index(active_tab):
            comp.highestActiveTab = mytabs.index(active_tab)
        ctx = dash.callback_context
        triggered = getTriggeredFromContext(ctx)
        if triggered:
            if triggered == "continue-to-interaction-effects" or active_tab != "tab-1":
                return "success"
        raise PreventUpdate

    app.callback(
        Output("main-effects-progress", "color"),
        Input("continue-to-interaction-effects", "n_clicks"),
        Input("tabs", "active_tab"),
    )(colorCallback)


def createButtonCallback(app):
    logger = logging.getLogger("werkzeug")

    def buttonCallback(nclicks_main, nclicks_interaction):
        ctx = dash.callback_context
        if not ctx.triggered:
            return ""
        else:
            logger.debug(ctx.triggered)
            clicked_button = ctx.triggered[0]["prop_id"].split(".")[0]

        return "{}, {}".format(nclicks_main, nclicks_interaction)

    app.callback(
        Output("added-variables-paragraph", "children"),
        Input("continue-to-interaction-effects", "n_clicks"),
        Input("continue-to-random-effects", "n_clicks"),
    )(buttonCallback)


def goToInteractionEffects(n_clicks):
    logger = logging.getLogger("werkzeug")
    logger.debug(n_clicks)
    if n_clicks:
        return "tab-2", True, False, False, "success", True, True, "primary"
    return "tab-1", False, True, True, "primary", False, False, "secondary"


def disableMainEffectsTab(n_clicks):
    return True if n_clicks else False
