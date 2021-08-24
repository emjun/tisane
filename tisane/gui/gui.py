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
from tisane.gui.gui_components import GUIComponents
from tisane.gui.callbacks import createCallbacks

external_stylesheets = [
    dbc.themes.BOOTSTRAP,
    {
        "rel": "stylesheet",
        "href": "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.5.0/font/bootstrap-icons.css",
    },
]

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


# open_browser()
# Write data to a file
def write_data(data: dict):
    with open("model_spec.json", "w") as f:
        f.write(json.dumps(data))


class TisaneGUI:
    app: dash.Dash

    def __init__(self):
        pass

    # @param input is a json file that has all the data to read in
    def read_input(self, input: str):
        self.components = GUIComponents(input)
        pass

    # @param input is a json file that has all the data to read in
    def start_app(self, input: str):
        ### Read in input data
        self.read_input(input)

        ### Create app
        app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

        ### Populate app
        # Get components
        progress = self.progress()
        # TODO: Add callback that enables this button once all the tabs/sections have been completed
        # generate_code_button = dbc.Button(
        #     "✨Generate code✨", color="dark", className="mr-1", disabled=True
        # )
        overview = self.overview()
        model_tabs = self.model_tabs()

        # Layout components that require special formatting
        # Build progress row

        progress_row = [
            dbc.Col(
                dbc.Progress(
                    [
                        dbc.Progress(
                            "Look over main effects",
                            value=25,
                            animated=True,
                            striped=True,
                            bar=True,
                            id="main-effects-progress",
                        ),
                        dbc.Progress(
                            "Look over interaction effects",
                            value=25,
                            animated=False,
                            bar=True,
                            id="interaction-effects-progress",
                            color="secondary",
                        ),
                        dbc.Progress(
                            "Look over random effects",
                            value=25,
                            animated=False,
                            bar=True,
                            id="random-effects-progress",
                            color="secondary",
                        ),
                        dbc.Progress(
                            "Pick family and link functions",
                            value=25,
                            animated=False,
                            bar=True,
                            id="family-link-functions-progress",
                            color="secondary",
                        ),
                    ],
                    multi=True,
                    style={"height": "2rem"},
                ),
                width=12,
            )
        ]

        # Add all components to main app's layout
        app.layout = dbc.Container(
            [
                html.H1("🌺 Tisane"),
                dbc.Row(progress_row),
                html.Br(),
                # Split screen between overview and model specification tabs
                dbc.Row(
                    [
                        dbc.Col(overview, width=4),
                        dbc.Col(model_tabs, width=8),
                    ]
                ),
                dcc.Store(id="added-main-effects-store"),
                dcc.Store(id="added-interaction-effects-store"),
                dcc.Store(id="random-effects-check-store"),
            ]
            + self.components.createEffectPopovers(),
            fluid=False,
        )

        ### Start and run app on local server
        self.app = app
        createCallbacks(app, self.components)
        # open_browser()
        app.run_server(debug=False, threaded=True, port=port)

    def progress(self):
        # TODO: Trying to make this feel like overview of installation progress on Mac
        progress = [
            dbc.Card(
                [html.P("Look over main effects")],
                body=True,
            ),
            dbc.Card(
                [html.P("Look over interaction effects")],
                body=True,
            ),
            dbc.Card(
                [html.P("Look over random effects")],
                body=True,
            ),
            dbc.Card(
                [html.P("Pick family and link functions")],
                body=True,
            ),
        ]

        return progress

    def model_tabs(self):
        # Many different ways to create tabs: https://dash-bootstrap-components.opensource.faculty.ai/docs/components/tabs/
        tab1_content = self.components.getMainEffectsCard()

        tab2_content = self.components.getInteractionEffectsCard()

        tab3_content = self.components.getRandomEffectsCard()

        tab4_content = self.components.getFamilyLinkFunctionsCard()

        tabs = dbc.Tabs(
            [
                dbc.Tab(
                    tab1_content,
                    label="Main effects",
                    tab_style={"marginLeft": "auto"},
                    tab_id="tab-1",
                    id="main-effects-tab",
                ),
                dbc.Tab(
                    tab2_content,
                    label="Interaction effects",
                    tab_style={"marginLeft": "auto"},
                    tab_id="tab-2",
                    id="interaction-effects-tab",
                ),
                dbc.Tab(
                    tab3_content,
                    label="Random effects",
                    tab_style={"marginLeft": "auto"},
                    tab_id="tab-3",
                    id="random-effects-tab",
                ),
                dbc.Tab(
                    tab4_content,
                    label="Family, Link functions",
                    tab_style={"marginLeft": "auto"},
                    tab_id="tab-4",
                    id="family-link-functions-tab",
                ),
            ],
            id="tabs",
        )
        return tabs

    def overview(self):
        query = self.components.getQuery()
        overview = dbc.Card(
            dbc.CardBody(
                [
                    html.H5("Variables expressed in query: "),
                    html.P("DV: {}".format(query["DV"])),
                    html.P("IVs:"),
                    html.Ul(children=[html.Li(iv) for iv in query["IVs"]]),
                    html.H5("Variables added:"),
                    html.Div(
                        [
                            html.H6("Main effects added:"),
                            html.Ul(id="added-main-effects"),
                        ]
                        + self.components.getInteractionEffectsAddedSection(),
                        id="added-variables-paragraph",
                    ),
                ]
                + self.components.getRandomEffectsAddedSection()
                + [
                    html.H5("Family: Gaussian", id="overview-family"),
                    html.H5("Link: Identity", id="overview-link")
                    # html.Div(id="test-div-output")
                ]
            ),
            color="light",
        )

        return overview
