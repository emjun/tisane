from dash.dependencies import Output, Input, State, ALL, MATCH
import dash
from dash.exceptions import PreventUpdate
import dash_html_components as html
from tisane.gui.gui_components import GUIComponents, separateByUpperCamelCase

def createRandomEffectsCallbacks(app, comp: GUIComponents = None):
    # createRandomEffectsAddedCallbacks(app, comp)
    pass

def createRandomEffectsAddedCallbacks(app, comp: GUIComponents = None):
    inputs = [Input(id, "checked") for id in comp.getRandomEffectCheckboxIds()]
    states = [State(id, "id") for id in comp.getRandomEffectCheckboxIds()]
    @app.callback(
        Output("added-random-effects", "children"),
        inputs, states
    )
    def addRandomEffects(*args):
        assert len(args) % 2 == 0, "Length of args is weird: {}".format(args)
        if not comp:
            print("Cannot update added random effects")
            raise PreventUpdate
        if args:
            print("Adding random effects")
            half = int(len(args) / 2)
            inputs = args[:half]
            states = args[half:]
            print(inputs)
            checked = []
            for i in range(len(inputs)):
                id = states[i]
                input = inputs[i]
                if input and comp.hasRandomEffectForComponentId(id):
                    randomEffect = comp.getRandomEffectFromComponentId(id)
                    checked.append(randomEffect)
                    pass
                pass
            return [html.Li(str(c)) for c in checked]
        print("Could not add random effects")
        raise PreventUpdate
