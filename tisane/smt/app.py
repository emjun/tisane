import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import webbrowser  # For autoamtically opening the browser for the CLI

# Import other Python libraries for updating the app
from typing import List

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]


class App(object):
    app: dash.Dash

    def __init__(self):
        dirname = os.path.dirname(__file__)
        filename = os.path.join(dirname, "app.py")
        p = subprocess.Popen(
            ["python", "./tisane/smt/app.py"],
            cwd=os.getcwd(),
            stdout=DEVNULL,
            stderr=DEVNULL,
        )


app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# TODO: Get all elements on page
# TODO: Add logic for showing and hiding

app.layout = html.Div(
    id="main_effects",
    children=[
        # All elements from the top of the page
        html.Div(
            [
                html.H1(children="Main Effects"),
                html.Div(
                    id="include_main_effects",
                    children=[
                        html.H3(children="Do you want to include main effects?"),
                        dcc.RadioItems(
                            id="include_main_effects_radio",
                            options=[
                                {"label": "Yes", "value": "yes"},
                                {"label": "No", "value": "no"},
                            ],
                            value=None,
                            labelStyle={"display": "inline-block"},
                        ),
                    ],
                ),
                html.Div(
                    id="main_expand", children=[html.H1(children="add more here")]
                ),
            ]
        ),
        # New Div for all elements in the new 'row' of the page
        html.Div(
            [
                html.H1(children="Interaction Effects"),
                # html.Div(children='''
                #     Dash: A web application framework for Python.
                # '''),
                # dcc.Graph(
                #     id='graph2',
                #     figure=fig
                # ),
            ]
        ),
        # New Div for all elements in the new 'row' of the page
        html.Div(
            [
                html.H1(children="Family Distribution"),
                # html.Div(children='''
                #     Dash: A web application framework for Python.
                # '''),
                # dcc.Graph(
                #     id='graph2',
                #     figure=fig
                # ),
            ]
        ),
        # New Div for all elements in the new 'row' of the page
        html.Div(
            [
                html.H1(children="Link functions"),
                # html.Div(children='''
                #     Dash: A web application framework for Python.
                # '''),
                # dcc.Graph(
                #     id='graph2',
                # ),
            ]
        ),
    ],
)

# @app.callback(
#     Output('layout', 'children'),
#     [Input('add-element-button', 'n_clicks')],
#     [State('layout', 'children')],
# )
# def add_strategy_divison(val, children):
#     if val:
#         el = html.Div(id=f"heading_element_{val}", children=[html.H1(id=f"heading_{val}", children=f"{val} Heading")],)
#         children.append(el)
#         return children
#     else:
#         raise PreventUpdate

# app.scripts.config.serve_locally = True


@app.callback(
    Output("main_expand", "children"),
    [Input("include_main_effects_radio", "value")],
    [State("main_expand", "children")],
)
def expand_main_effects(radio_val, old_output):
    if radio_val == "yes":
        # This is where we would read the unsat queries, etc.
        generate_main_effects()
        return html.Div("expanding")
    if radio_val == "no":
        # console.log('hi')
        pass


# @app.callback(Output('main_effects', 'children'),
#               Input('include_main_effects_yes', 'n_clicks'),
#               Input('include_main_effects_no', 'n_clicks'))
# def displayClick(yes, no):
#     changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
#     if 'include_main_effects_yes' in changed_id:
#         msg = 'yes'
#     elif 'include_main_effects_no' in changed_id:
#         msg = 'no'
#     else:
#         msg = 'None of the buttons have been clicked yet'
#     return html.Div(msg)

# @app.callback(
#     Output('main_effects','children'),
#     [Input('inclusion','include')],
#     [State('main_effects','children')])
# def more_output(include,old_output):
#     if not include:
#         raise PreventUpdate
#     return old_output + [html.Div('Thing {}'.format(n_clicks))]

port = "8050"  # default dash port


def open_browser():
    webbrowser.open_new("http://localhost:{}".format(port))


open_browser()
app.run_server(debug=False, threaded=True)
# app.run_server(debug=False,dev_tools_ui=False,dev_tools_props_check=False)


def update_include():
    include = True
