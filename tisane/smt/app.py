import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import webbrowser # For autoamtically opening the browser for the CLI

# Import other Python libraries for updating the app
from typing import List

app = dash.Dash(__name__)

# TODO: Get all elements on page
# TODO: Add logic for showing and hiding

app.layout = html.Div(
    id='main_effects', 
    children=[
    # All elements from the top of the page
    html.Div([
        html.H1(children='Main Effects'),

        html.Div(children='''
            Dash: A web application framework for Python.
        '''),

        # dcc.Graph(
        #     id='graph1',
        #     figure=fig
        # ),  
        html.Button(id='inclusion', include=False, style = dict(display='none'))
    ]),
    # New Div for all elements in the new 'row' of the page
    html.Div([
        html.H1(children='Interaction Effects'),

        html.Div(children='''
            Dash: A web application framework for Python.
        '''),

        # dcc.Graph(
        #     id='graph2',
        #     figure=fig
        # ),  
    ]),
    # New Div for all elements in the new 'row' of the page
    html.Div([
        html.H1(children='Family Distribution'),

        html.Div(children='''
            Dash: A web application framework for Python.
        '''),

        # dcc.Graph(
        #     id='graph2',
        #     figure=fig
        # ),  
    ]),
    # New Div for all elements in the new 'row' of the page
    html.Div([
        html.H1(children='Link functions'),

        html.Div(children='''
            Dash: A web application framework for Python.
        '''),

        # dcc.Graph(
        #     id='graph2',
        # ),  
    ]),
])

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
    Output('main_effects','children'),
    [Input('inclusion','include')],
    [State('main_effects','children')])
def more_output(include,old_output):
    if not include: 
        raise PreventUpdate
    return old_output + [html.Div('Thing {}'.format(n_clicks))]

port = '8050' # default dash port
def open_browser():
	webbrowser.open_new("http://localhost:{}".format(port))

open_browser()
app.run_server(debug=False, threaded=True)


def update_include():
    include = True