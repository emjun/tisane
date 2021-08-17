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
        app.layout = html.Div([
            html.H1('Hello world')
        ])

        ### Start and run app on local server
        self.app = app
        open_browser()
        app.run_server(debug=False, threaded=True, port=port)
    
    def progress_bar(self):
        # Card components
        cards = [
            dbc.Card(
                [
                    html.H2(f"{train_acc*100:.2f}%", className="card-title"),
                    html.P("Model Training Accuracy", className="card-text"),
                ],
                body=True,
                color="light",
            ),
            dbc.Card(
                [
                    html.H2(f"{test_acc*100:.2f}%", className="card-title"),
                    html.P("Model Test Accuracy", className="card-text"),
                ],
                body=True,
                color="dark",
                inverse=True,
            ),
            dbc.Card(
                [
                    html.H2(f"{dfTrain.shape[0]} / {dfTest.shape[0]}", className="card-title"),
                    html.P("Train / Test Split", className="card-text"),
                ],
                body=True,
                color="primary",
                inverse=True,
            ),
        ]
