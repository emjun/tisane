from tisane.variable import AbstractVariable
from tisane.design import Design
from tisane.statistical_model import StatisticalModel
from tisane.smt.synthesizer import Synthesizer
# from tisane.smt.app import add_inclusion_prompt

from typing import List, Any
import subprocess
from subprocess import DEVNULL
import os
import sys

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import webbrowser # For autoamtically opening the browser for the CLI

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
port = '8050' # default dash port
def open_browser():
	webbrowser.open_new("http://localhost:{}".format(port))

        
class InputInterface(object): 
    design: Design 
    statistical_model: StatisticalModel
    app: dash.Dash

    def __init__(self, design: Design, synthesizer: Synthesizer):
        self.design = design
        # self.statistical_model = statistical_model
        self.synthesizer = synthesizer
        
        app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
        
        # Create Dash App
        app.layout = html.Div(
            id='main_effects', 
            children=[
            # All elements from the top of the page
            html.Div([
                html.H1(children='Main Effects'),

                html.Div( 
                id='include_main_effects',
                children=[            
                    html.H3(children='Do you want to include main effects?'),

                    dcc.RadioItems(
                        id='include_main_effects_radio',
                        options=[
                            {'label': 'Yes', 'value': 'yes'},
                            {'label': 'No', 'value': 'no'}
                        ],
                        value=None,
                        labelStyle={'display': 'inline-block'}
                    )  
                ],
                daq.ToggleSwitch(
                    id='main_done',
                    value=True,
                    label='Editing main effects',
                    labelPosition='bottom'
                )
                ),

                html.Div(
                    id='main_expand',
                    children=[
                        html.H1(children='add more here')
                    ]
                )
            ]),
            # New Div for all elements in the new 'row' of the page
            html.Div([
                html.H1(children='Interaction Effects'),

                # html.Div(children='''
                #     Dash: A web application framework for Python.
                # '''),

                # dcc.Graph(
                #     id='graph2',
                #     figure=fig
                # ),  
            ]),
            # New Div for all elements in the new 'row' of the page
            html.Div([
                html.H1(children='Family Distribution'),

                # html.Div(children='''
                #     Dash: A web application framework for Python.
                # '''),

                # dcc.Graph(
                #     id='graph2',
                #     figure=fig
                # ),  
            ]),
            # New Div for all elements in the new 'row' of the page
            html.Div([
                html.H1(children='Link functions'),

                # html.Div(children='''
                #     Dash: A web application framework for Python.
                # '''),

                # dcc.Graph(
                #     id='graph2',
                # ),  
            ]),
        ])
        
        @app.callback(  Output('main_expand', 'children'),
                [Input('include_main_effects_radio', 'value')],
                [State('main_expand','children')])
        def expand_main_effects(radio_val, old_output):
            if radio_val == 'yes':
                output = list()
                # Get possible main effects from synthesizer
                possible_main_effects = self.synthesizer.generate_main_effects(design=design)

                # Present them 
                html.Div(str("Main effects to include: "))
                for (variable, facts) in possible_main_effects.items(): 
                    output.append(html.Div([
                        str(variable), 
                        dcc.RadioItems(
                            id=f'{variable}_inclusion',
                            options=[
                                {'label': 'Include', 'value': f'{facts[0]}'},
                                {'label': 'Do not include', 'value': f'{facts[1]}'}
                            ],
                            value=f'{facts[0]}', # TODO: Replace with Tisane recommendations
                            labelStyle={'display': 'inline-block'}
                        )]))  
                return output
            if radio_val == 'no':
                pass
        
        # When finished editing the main effects, validate the selections with synthesizer
        @app.callback(Output('main_done', 'label'),
                    Input('main_done', 'value'))
        def save_main_effects(toggle): 
            return 'Saved'
            
        def check_and_update_main_effects(): 
            pass
            rules = list()

            solve()


        # # Get rules 
                # rules_dict = QM.collect_rules(output='effects', dv_const=dv.const)

                # # Solve constraints + rules
                # (res_model_fixed, res_facts_fixed) = QM.solve(facts=fixed_facts, rules=rules_dict)
                
                # # Update result StatisticalModel based on user selection 
                # sm = QM.postprocess_to_statistical_model(model=res_model_fixed, facts=res_facts_fixed, graph=design.graph, statistical_model=sm)

                # # Design 1
                # # main_effects = from synth
                # # conflicts = from synth
                # # update div based on conflict 
                # # Callback where div selection "resolves conflict"
                # # Then lock the choice.

                # # Design 2
                # # better design -> temporary storage with user selected choices. Then at the end update/check for SAT
                # # Suggestions just get "*based on your conceptual model, ...." recommendation tag?
                
                # # App contains all the relationships...(visually show the conceptual relationships? under: show the measurement relationships)
        
        open_browser()
        app.run_server(debug=False, threaded=True)
        
        self.app = app
    
    def get_input(self): 
        pass
    
    @classmethod
    def ask_inclusion_prompt(cls, subject: str) -> bool: 

        prompt = f'Would you like to include {subject}?'
        choices = f' Y or N: '

        while True: 
            ans = add_inclusion_prompt(prompt=prompt, choices=choices)
            if ans.upper() == 'Y': 
                return ans.upper()
            elif ans.upper() == 'N': 
                return ans.upper()
            else: 
                pass
    
    @classmethod
    def ask_inclusion(cls, subject: str) -> bool: 
    
        ans = cls.ask_inclusion_prompt(subject)

        if ans.upper() == 'Y':
            # TODO: write to a file here 
            return True
        elif ans.upper() == 'N': 
            return False
        else: 
            pass
    
    # TODO: Format the interactions to be more readable
    @classmethod 
    def format_options(cls, options: List) -> List: 
        return options

    @classmethod
    def ask_multiple_choice_prompt(cls, options: List) -> Any: 
        prompt = f'These cannot be true simultaneously.'
        formatted_options = cls.format_options(options)
        choices = f' Pick index (starting at 0) to select option in: {formatted_options}: '
        while True: 
            idx = int(input(prompt + choices))
            # st.write()

            if idx in range(len(options)): 
                # only keep the constraint that is selected. 
                constraint = options[idx] 
                print(f'Ok, going to add {constraint} and remove the others.')
                return idx
            else:
                print(f'Pick a value in range')
                pass
    
    @classmethod
    def resolve_unsat(cls, facts: List, unsat_core: List) -> List: 
        idx = cls.ask_multiple_choice_prompt(options=unsat_core)
    
        return unsat_core[idx]

    # TODO: Format options for specifying family of a distribution
    @classmethod
    def format_family(cls, options: List): 
        return options
    
    @classmethod
    def ask_family_prompt(cls, options: List, dv: AbstractVariable): 
        prompt = f'Which distribution best approximates your dependent variable {dv}?'
        formatted_options = cls.format_options(options)
        choices = f' Pick index (starting at 0) to select option in: {formatted_options}: '

        while True: 
            idx = int(input(prompt + choices))

            if idx in range(len(options)): 
                # only keep the constraint that is selected. 
                constraint = options[idx] 
                print(f'Ok, going to add {constraint} and remove the others.')
                return idx
            else:
                print(f'Pick a value in range')
                pass
    
    @classmethod
    def ask_family(cls, options: List, dv: AbstractVariable): 
        idx = cls.ask_family_prompt(options=options, dv=dv)

        return options[idx]

    @classmethod
    def ask_link_prompt(cls, options: List, dv: AbstractVariable): 
        prompt = f'W'


    @classmethod
    def ask_link(cls, options: List, dv: AbstractVariable): 
        idx = cls.ask_link_prompt(options=options, dv=dv)

        return options[idx]

    # @classmethod
    # def ask_change_default_prompt(cls, subject: str, default: str, options: List): 
    #     prompt = f'The default {subject} is {default}. Would you like to change it to one of {options}?'

    # @classmethod
    # def ask_change_default(cls, subject: str, default: str, options: List): 
    #     idx = cls.ask_change_default_prompt(subject=subject, default=default, options=options)
    #     pass