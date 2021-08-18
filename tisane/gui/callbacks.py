from dash.dependencies import Output, Input, State, ALL, MATCH
import dash
from dash.exceptions import PreventUpdate

def createCallbacks(app):
    cont_to_interaction_effects_input = Input("continue-to-interaction-effects", "n_clicks")
    createMainEffectsProgressBarCallbacks(app)
    createProgressBarCallbacks(app, "tab-2", "interaction-effects-progress", "continue-to-interaction-effects", "continue-to-random-effects")
    createProgressBarCallbacks(app, "tab-3", "random-effects-progress", "continue-to-random-effects", "continue-to-family-link-functions")
    createTabsCallbacks(app)
    createFamilyLinkFunctionsProgressCallbacks(app)
    pass

def getTriggeredFromContext(ctx):
    if not ctx.triggered:
        return False
    return ctx.triggered[0]['prop_id'].split('.')[0]

def createTransitionCallback(app, tabA, tabB, tabA_id, progressA, progressB, continue_button_id):
    def goToInteractionEffects(n_clicks):
        # print(n_clicks)
        if n_clicks:
            return True, True, "primary"
        return False, False, "secondary"
    app.callback(
        Output(progressB, "animated"),
        Output(progressB, "striped"),
        Output(progressB, "color"),
        [Input(continue_button_id, "n_clicks")])(goToInteractionEffects)


    pass

def createTabsCallbacks(app):
    def continueCallback(fromMain, fromInteraction, fromRandom):
        ctx = dash.callback_context
        triggered = getTriggeredFromContext(ctx)
        print("Continue callback: {}".format(triggered))
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
        Input("continue-to-family-link-functions", "n_clicks")
    )(continueCallback)

mytabs = ["tab-1", "tab-2", "tab-3", "tab-4"]

def createFamilyLinkFunctionsProgressCallbacks(app):
    def animatedCallback(nclicks, active_tab):
        ctx = dash.callback_context
        if not ctx.triggered:
            raise PreventUpdate
        print(ctx.triggered)
        triggered = getTriggeredFromContext(ctx)
        if triggered == "tabs":
            return active_tab == "tab-4", active_tab == "tab-4"
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
        print("{}, {}: {}, {}".format("tab-4", "family-link-functions-progress", triggered, active_tab))
        if triggered:
            if triggered == "generate-code" or mytabs.index(active_tab) > mytabs.index("tab-4"):
                return "success"
            if triggered == "continue-to-family-link-functions" or mytabs.index(active_tab) == mytabs.index("tab-4"):
                return "primary"
        raise PreventUpdate
    app.callback(
        Output("family-link-functions-progress", "color"),
        Input("generate-code", "n_clicks"),
        Input("continue-to-family-link-functions", "n_clicks"),
        Input("tabs", "active_tab")
    )(colorCallback)


def createProgressBarCallbacks(app, triggered_tab, progressid, continuefrom_id, continueto_id):
    def animatedCallback(nclicks, active_tab):
        ctx = dash.callback_context
        if not ctx.triggered:
            return True, True
        print(ctx.triggered)
        triggered = getTriggeredFromContext(ctx)
        if triggered == "tabs":
            return active_tab == triggered_tab, active_tab == triggered_tab
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
        print("{}, {}: {}, {}".format(triggered_tab, progressid, triggered, active_tab))
        if triggered:
            if triggered == continueto_id or mytabs.index(active_tab) > mytabs.index(triggered_tab):
                return "success"
            if triggered == continuefrom_id or mytabs.index(triggered_tab) == mytabs.index(active_tab):
                return "primary"
        raise PreventUpdate
    app.callback(
        Output(progressid, "color"),
        Input(continueto_id, "n_clicks"),
        Input(continuefrom_id, "n_clicks"),
        Input("tabs", "active_tab")
    )(colorCallback)

def createMainEffectsProgressBarCallbacks(app):
    def animatedCallback(nclicks_main, nclicks_interaction, active_tab):
        ctx = dash.callback_context
        if not ctx.triggered:
            return True, True
        print(ctx.triggered)
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
        ctx = dash.callback_context
        triggered = getTriggeredFromContext(ctx)
        if triggered:
            if triggered == "continue-to-interaction-effects" or active_tab != "tab-1":
                return "success"
        raise PreventUpdate
    app.callback(
        Output("main-effects-progress", "color"),
        Input("continue-to-interaction-effects", "n_clicks"),
        Input("tabs", "active_tab")
    )(colorCallback)


def createButtonCallback(app):
    def buttonCallback(nclicks_main, nclicks_interaction):
        ctx = dash.callback_context
        if not ctx.triggered:
            return ""
        else:
            print(ctx.triggered)
            clicked_button = ctx.triggered[0]['prop_id'].split('.')[0]

        return "{}, {}".format(nclicks_main, nclicks_interaction)
    app.callback(
        Output("added-variables-paragraph", "children"),
        Input("continue-to-interaction-effects", "n_clicks"),
        Input("continue-to-random-effects", "n_clicks"),
    )(buttonCallback)


def goToInteractionEffects(n_clicks):
    print(n_clicks)
    if n_clicks:
        return "tab-2", True, False, False, "success", True, True, "primary"
    return "tab-1", False, True, True, "primary", False, False, "secondary"

def disableMainEffectsTab(n_clicks):
    return True if n_clicks else False
