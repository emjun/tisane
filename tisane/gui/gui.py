from flask import request
import logging
import json
import plotly.figure_factory as ff
import plotly.express as px
import dash
import dash_daq as daq
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input, State, ALL, MATCH
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go
import webbrowser  # For autoamtically opening the browser for the CLI
import socket  # For finding next available socket

external_stylesheets = [dbc.themes.BOOTSTRAP]

# Find socket info
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(("", 0))
addr = s.getsockname()
port = addr[1]
s.close()

# For logging Dash output
log = logging.getLogger("werkzeug")
log.setLevel(logging.ERROR)

# port = '0' # FYI: default dash port is 8050
def open_browser():
    global port
    webbrowser.open_new("http://localhost:{}".format(port))

# Write data to a file
def write_data(data: dict):
    with open("model_spec.json", "w") as f:
        f.write(json.dumps(data))

class TisaneGUI():
    app: dash.Dash

    def __init__(self):
        pass

    def start_app(self):
        ### Create app
        app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

        ### Populate app
        # Get components
        progress = self.progress() # TODO: Add callback to update progress according to tabs
        generate_code_button = dbc.Button("✨Generate code✨", color="dark", className="mr-1", disabled=True) # TODO: Add callback that enables this button once all the tabs/sections have been completed
        overview = self.overview()
        model_tabs = self.model_tabs()

        # Layout components that require special formatting
        # Build progress row
        progress_row = list()
        for card in progress: 
            # TODO: Add callback for each card that when the tab/section is completed, the card changes color to "success." The callback could by tied to "locking" each tab/section? 
            progress_row.append(dbc.Col(card, width=2)) # TODO: Try to get each card to be the same size despite different text inside. Maybe shorten text, style card, etc.
        progress_row.append(dbc.Col(generate_code_button, width=2))

        # Add all components to main app's layout
        app.layout = dbc.Container(
            [
                html.H1("🌺 Tisane"),
                dbc.Row(progress_row),
                html.Br(),
                # Split screen between overview and model specification tabs
                dbc.Row([
                    dbc.Col(overview, width=4),
                    dbc.Col(model_tabs, width=8),
                ])
                
                # Header("Dash Heart Disease Prediction with AIX360", app),
                # html.Hr(),
                # dbc.Row([dbc.Col(card) for card in cards]),
                # html.Br(),
                # dbc.Row([dbc.Col(graph) for graph in graphs]),
            ],
            fluid=False,
        )

        ### Start and run app on local server
        self.app = app
        open_browser()
        app.run_server(debug=False, threaded=True, port=port)
    
    def progress(self):
        # TODO: Trying to make this feel like overview of installation progress on Mac
        progress = [
            dbc.Card([
                html.P("Look over main effects")
            ],
            body=True, 
            ),
            dbc.Card([
                html.P("Look over interaction effects")
            ],
            body=True, 
            ),
            dbc.Card([
                html.P("Look over random effects")
            ],
            body=True, 
            ),
            dbc.Card([
                html.P("Pick family and link functions")
            ],
            body=True, 
            ),
            
        ]

        return progress

    def model_tabs(self): 
        # Many different ways to create tabs: https://dash-bootstrap-components.opensource.faculty.ai/docs/components/tabs/
        tab1_content = dbc.Card(
                dbc.CardBody(
                    [
                        html.P("Main", className="card-text"),
                        dbc.Button("Click here", color="success"),

                        # TODO: Maybe some kind of variable/explanation list like this?: https://dash-bootstrap-components.opensource.faculty.ai/docs/components/list_group/

                    ]
                ),
                className="mt-3",
            )

        tab2_content = dbc.Card(
            dbc.CardBody(
                [
                    html.P("Interactions", className="card-text"),
                    dbc.Button("Don't click here", color="danger"),
                ]
            ),
            className="mt-3",
        )

        tab2_content = dbc.Card(
            dbc.CardBody(
                [
                    html.P("Random", className="card-text"),
                    dbc.Button("Don't click here", color="danger"),
                ]
            ),
            className="mt-3",
        )

        tab2_content = dbc.Card(
            dbc.CardBody(
                [
                    html.P("Family, Link", className="card-text"),
                    dbc.Button("Don't click here", color="danger"),
                ]
            ),
            className="mt-3",
        )


        tabs = dbc.Tabs(
            [
                dbc.Tab(tab1_content, label="Main effects", tab_style={"marginLeft": "auto"}),
                dbc.Tab(tab2_content, label="Interaction effects", tab_style={"marginLeft": "auto"}),
                dbc.Tab(tab2_content, label="Random effects", tab_style={"marginLeft": "auto"}),
                dbc.Tab(tab2_content, label="Family, Link functions", tab_style={"marginLeft": "auto"})
            ]
        )
        return tabs

    def overview(self): 
        overview = dbc.Card(
            dbc.CardBody(
                [
                    html.P("Variables expressed in query:"),
                    # TODO: Add List of variables
                    html.P("Variables added:")
                    # TODO: Add list of variables as analyst selects them in the tabs
                ]
            ),
            color="light"
        )

        return overview