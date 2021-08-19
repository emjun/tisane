from dash.dependencies import Output, Input, State, ALL, MATCH
import dash
from dash.exceptions import PreventUpdate
import dash_html_components as html
from tisane.gui.gui_components import GUIComponents, separateByUpperCamelCase


def createFamilyLinkFunctionCallbacks(app, comp: GUIComponents = None):
    createLinkFunctionCallbacks(app, comp)
    pass

def createLinkFunctionCallbacks(app, comp: GUIComponents = None):
    @app.callback(
        Output("link-options", "options"),
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
                return [
                    {
                        "label": " ".join(separateByUpperCamelCase(str(l))),
                        "value": str(l)
                    } for l in familyLinks[value]
                ]
            pass
        print("Cannot update for some reason")
        raise PreventUpdate
