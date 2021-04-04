from tisane.variable import AbstractVariable, Numeric, Nominal, Ordinal
from tisane.design import Design
from tisane.statistical_model import StatisticalModel
from tisane.random_effects import *
from tisane.smt.synthesizer import Synthesizer
from tisane.smt.rules import *
from tisane.helpers import *


from z3 import *
from typing import List, Any, Tuple
import subprocess
from subprocess import DEVNULL
import os
import sys
from flask import request

import json
import pandas as pd
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
import webbrowser # For autoamtically opening the browser for the CLI
import socket # For finding next available socket

external_stylesheets = [dbc.themes.BOOTSTRAP]
__str_to_z3__ = dict() # Global map between vals and z3 facts

# Find socket info 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 0))
addr = s.getsockname()
port = addr[1]
s.close()

# port = '0' # FYI: default dash port is 8050
def open_browser():
    global port
    webbrowser.open_new("http://localhost:{}".format(port))

# Write data to a file
def write_data(data: dict): 
    with open('model_spec.json', 'w') as f: 
        f.write(json.dumps(data))

class InputInterface(object): 
    design: Design 
    statistical_model: StatisticalModel
    app: dash.Dash

    def __init__(self, main_effects: Dict[str, List[AbstractVariable]]=None, interaction_effects: Dict[str, Tuple[AbstractVariable, ...]]=None, random_effects: List[z3.BoolRef]=None, family_link: Dict[z3.BoolRef, List[z3.BoolRef]]=None, default_family_link: Dict[z3.BoolRef, z3.BoolRef]=None, design: Design=None, synthesizer: Synthesizer=None):
        global port 

        if design:
            # Save necessary data
            self.design = design
        if family_link:
            # self.synthesizer = synthesizer
            for family, links in family_link.items(): 
                key = str(family) 
                __str_to_z3__[key] = family # str to Z3 fact

                for l in links: 
                    key = str(l) 
                    __str_to_z3__[key] = l # str to Z3 fact

        self.family_link_options = family_link
        self.default_family_link = default_family_link
    
    def start_app(self, main_effects: Dict[str, List[AbstractVariable]], interaction_effects: Dict[str, Tuple[AbstractVariable, ...]], random_effects: List[z3.BoolRef], family_link: Dict[z3.BoolRef, List[z3.BoolRef]], default_family_link: Dict[z3.BoolRef, z3.BoolRef], design: Design):
        
        app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

        ##### Layout UI
        # Hidden modals
        code_gen_modal = dbc.Modal(
            [
                dbc.ModalHeader("Downloading generated script!"),
                dbc.ModalBody("Tisane is generating a script based on your input script and UI selections."),
                dbc.ModalFooter([
                    dbc.Button("Close GUI", id="close", color='danger', className="ml-auto"),
                    dbc.Button("Keep GUI open", id="keep_open", className="ml-auto")
                ]),
            ],
            id="code_gen_modal",
        )
        model_spec_issue_ivs_modal = dbc.Modal(
            [
                dbc.ModalHeader("Issue! Please specify at least one independent variable!"),
                # dbc.ModalBody("Tisane is generating a script based on your input script and UI selections."),
                dbc.ModalFooter([
                    dbc.Button("Got it!", id="got_it_ivs", className="ml-auto")                ]),
            ],
            id="model_spec_issue_ivs",
        )
        model_spec_issue_family_modal = dbc.Modal(
            [
                dbc.ModalHeader("Issue! You must select a family distribution for your data!"),
                # dbc.ModalBody("Tisane is generating a script based on your input script and UI selections."),
                dbc.ModalFooter([
                    dbc.Button("Got it!", id="got_it_family", className="ml-auto"),
                ]),
            ],
            id="model_spec_issue_family",
        )
        model_spec_issue_link_modal = dbc.Modal(
            [
                dbc.ModalHeader("Issue! You must specify a link function. Consider using the default for a family!"),
                # dbc.ModalBody("Tisane is generating a script based on your input script and UI selections."),
                dbc.ModalFooter([
                    dbc.Button("Got it!", id="got_it_link", className="ml-auto")
                ]),
            ],
            id="model_spec_issue_link",
        )



        # Main components 
        main_effects_div = self.layout_main_effects_div(main_effects)
        interaction_effects_div = self.layout_interaction_effects_div(interaction_effects)
        family_link_div = self.layout_family_link_div(family_link)
        random_effects_div = self.layout_random_effects_div(random_effects)
        script_download_button = dbc.Button("Generate code snippet and model diagnostics", id='generate_code', color="primary", block=True, disabled=True)

        # Create Dash App
        app.layout = dbc.Container([
                dcc.Store(id='session_store', storage_type='session'),
                code_gen_modal,
                model_spec_issue_ivs_modal,
                model_spec_issue_family_modal,
                model_spec_issue_link_modal,
                
                # Body
                dbc.Row([dbc.Col(main_effects_div, width=8)], justify='center'),
                dbc.Row([dbc.Col(interaction_effects_div, width=8)], justify='center'),
                # dbc.Row([dbc.Col(random_effects_card, width=8)], justify='center'),
                dbc.Row([dbc.Col(random_effects_div, width=8)], justify='center'),
                dbc.Row([dbc.Col(family_link_div, width=8)], justify='center'),
                dbc.Row([dbc.Col(script_download_button, width=8)], justify='center'),

                # Hidden div for storing intermediate state before updating session
                # store and eventually checking with synthesizer
                html.Div(id='intermediate_store', hidden=True)
            ],
            fluid=True
        )
        
        # TODO: Move outside ctor?
        ##### Add callbacks for interactions
        
        # TODO: Start here - save the values we care about into intermediate storage div; test that first
        @app.callback(
            Output({'type': 'main_effects_options', 'index': ALL}, 'options'),
            Input('main_effects_switch', 'value'),
            State({'type': 'main_effects_options', 'index': ALL}, 'options')
        )
        def save_main_effects(switch_value, main_effects_options):
            output = list()
            if switch_value: 
                facts = list()
                
                for i, options in enumerate(main_effects_options): 
                    cluster = list()        
                    for o in options:
                        facts.append(o['value'])
                        cluster.append({'label': o['label'], 'value': o['value'], 'disabled': True}) 
                    output.append(cluster)

                return output
                # TODO: Save main effects somewhere!
                # is_sat = self.synthesizer.check_constraints(facts, rule_set='effects', design=self.design)
                # if is_sat: 
                #     self.synthesizer.update_with_facts(facts, rule_set='effects', design=self.design)
                #     return output
                # else: 
                #     # TODO: Start a modal?
                #     raise ValueError(f"Error in saving main effects!")
            else: 
                for i, options in enumerate(main_effects_options): 
                    cluster = list()
                    for o in options: 
                        cluster.append({'label': o['label'], 'value': o['value'], 'disabled': False})
                    output.append(cluster)
                return output
        
        # @app.callback(
        #     Output('two-way_options', 'options'),
        #     [Input('interaction_effects_switch', 'value'),
        #     Input('two-way_options', 'value')],
        #     State('two-way_options', 'options')
        # )
        # def save_two_way_interaction_effects(switch_value, two_way_values, two_way_options): 
        #     output = list()
        #     if switch_value: 
        #         # Do we have any selected interaction effects to save? 
        #         if len(two_way_values) > 0: 
        #             facts = list()
        #             for o in two_way_options: 
        #                 facts.append(o['value'])
        #                 output.append({'label': o['label'], 'value': o['value'], 'disabled': True})
        #                 return output
                    
        #             # TODO: Save interaction effects somewhere!
        #             # is_sat = self.synthesizer.check_constraints(facts, rule_set='effects', design=self.design)
        #             # if is_sat: 
        #             #     self.synthesizer.update_with_facts(facts, rule_set='effects', design=self.design)
        #             #     return output
        #             # else: 
        #             #     # TODO: Start a modal?
        #             #     raise ValueError(f"Error in saving two-way interaction effects!")
        #         # No selected interaction effects to save
        #         else: 
        #             for o in two_way_options: 
        #                 output.append({'label': o['label'], 'value': o['value'], 'disabled': True})
        #             return output
        #     for o in two_way_options: 
        #         output.append({'label': o['label'], 'value': o['value'], 'disabled': False})
            
        #     return output
        
        @app.callback(
            Output({'type': 'interaction_effects_options', 'index': ALL}, 'options'),
            Input('interaction_effects_switch', 'value'),
            State({'type': 'interaction_effects_options', 'index': ALL}, 'options')
        )
        def save_interaction_effects(switch_value, interaction_effects_options): 
            output = list()
            if switch_value: 
                for i, options in enumerate(interaction_effects_options): 
                    cluster = list() 
                    for o in options: 
                        cluster.append({'label': o['label'], 'value': o['value'], 'disabled': True})    
                    output.append(cluster)
                return output                
            # else
            for i, options in enumerate(interaction_effects_options): 
                cluster = list() 
                for o in options: 
                    cluster.append({'label': o['label'], 'value': o['value'], 'disabled': False})    
                output.append(cluster)
            return output
            
        # @app.callback(
        #     Output('n-way_options', 'options'),
        #     [Input('interaction_effects_switch', 'value'),
        #     Input('n-way_options', 'value')],
        #     State('n-way_options', 'options')
        # )
        # def save_n_way_interaction_effects(switch_value, n_way_values, n_way_options): 
        #     output = list()
        #     if switch_value: 
        #         # Do we have any selected interaction effects to save? 
        #         if len(n_way_values) > 0: 
        #             facts = list()
        #             for o in n_way_options: 
        #                 facts.append(o['value'])
        #                 output.append({'label': o['label'], 'value': o['value'], 'disabled': True})
        #                 return output
        #             # TODO: Save and verify interaction effect facts somewhere
        #             # is_sat = self.synthesizer.check_constraints(facts, rule_set='effects', design=self.design)
        #             # if is_sat: 
        #             #     self.synthesizer.update_with_facts(facts, rule_set='effects', design=self.design)
        #             #     return output
        #             # else: 
        #             #     # TODO: Start a modal?
        #             #     raise ValueError(f"Error in saving n-way interaction effects!")
        #         # No selected interaction effects to save
        #         else: 
        #             for o in n_way_options: 
        #                 output.append({'label': o['label'], 'value': o['value'], 'disabled': True})        
        #             return output
        #     for o in n_way_options: 
        #         output.append({'label': o['label'], 'value': o['value'], 'disabled': False})
                
        #     return output
        
        @app.callback(
            Output('random_effects_table', 'children'),
            [Input('random_effects_switch', 'value'),
            # TODO: Start with what happens when main effects removed --> add _IMPLIED random
            # Input()
            Input('random_effects_table', 'children')],
        )
        def save_random_effects(switch_value, random_effects_table):
            
            ctx = dash.callback_context

            if not ctx.triggered: 
                return random_effects_table 
            #else: 
            trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

            if trigger_id == 'random_effects_switch': 
                output = list() 
                new_rows = list() 

                table_body = random_effects_table[0]
                table_rows = table_body['props']['children']

                if switch_value: 
                    for row in table_rows: 
                        # Is the row visible? 
                        if row['props']['hidden'] is False: 
                            new_row = copy.deepcopy(row)
                            # Turn off 
                            new_row['props']['style'] = {'color': '#808080'}

                            # Does this row have Correlated radio button children?
                            if len(row['props']['children']) == 2: 
                                radioItems = new_row['props']['children'][1]
                                radioItems = radioItems['props']['children']['props']['children']
                                # print(radioItems)
                                options = radioItems[0]['props']['options']
                                for o in options: 
                                    o['disabled'] = True
                            new_rows.append(new_row)
                        #
                else: 
                    for row in table_rows: 
                        # Is the row visible? 
                        if row['props']['hidden'] is False: 
                            new_row = copy.deepcopy(row)
                            # Remove "off" styling
                            new_row['props']['style'] = {}

                            # Does this row have Correlated radio button children?
                            if len(row['props']['children']) == 2: 
                                radioItems = new_row['props']['children'][1]
                                radioItems = radioItems['props']['children']['props']['children']
                                # print(radioItems)
                                options = radioItems[0]['props']['options']
                                for o in options: 
                                    o['disabled'] = False
                            new_rows.append(new_row)
                    
                output = [html.Tbody(children=new_rows)]
                return output
        
            
        # @app.callback(
        #     # Output({'type': 'random_effects_list', 'index': ALL}, 'children'),
        #     Output('random_effects_table', 'children'),
        #     Input('main_effects_switch', 'value'),
        #     Input('interaction_effects_switch', 'value'),
        #     Input({'type': 'main_effects_options', 'index': ALL}, 'value'),
        #     Input({'type': 'interaction_effects_options', 'index': ALL}, 'value'),
        #     # State({'type': 'random_effects_list', 'index': ALL}, 'children')
        #     State('random_effects_table', 'children')
        # )
        # def sync_random_effects(main_switch, interaction_switch, main_effects, interaction_effects, random_effects): 
        #     output = list() 
        #     rows = list()

        #     # Keep track of which random_effects to add as hidden afterwards 
        #     all_re = list()
        #     table_body = random_effects[0] # Tbody(rows)
        #     for row in table_body['props']['children']: 
        #         var_names = row['props']['id'].split('_random_effects')[0]
        #         all_re.append(var_names)
        #     added_re = list()

        #     if main_switch:     
        #         for m_list in main_effects: 
        #             assert(isinstance(m_list, list))
        #             # Is the main effect selected? 
        #             if len(m_list) > 0: 
        #                 for m in m_list: 
        #                     # If so, leave main effect in the random effects table
        #                     # If not, hide main effect in the random effects table 
        #                     var_name = m.split('FixedEffect(')[1]
        #                     var_name = var_name.split(',')[0]
        #                     table_body = random_effects[0] # Tbody(rows)
                            
        #                     for row in table_body['props']['children']: 
        #                         # Does this row pertain to the main effect being considered?
        #                         re_var_names = row['props']['id'].split('_random_effects')[0]
        #                         if var_name in re_var_names: 
        #                             new_row = html.Tr(children=row['props']['children'], id=row['props']['id'], hidden=False)
        #                         # else: 
        #                         #     new_row = html.Tr(children=row['props']['children'], id=row['props']['id'], hidden=False)
        #                             if new_row not in rows: 
        #                                 rows.append(new_row)
        #                                 assert(re_var_names not in added_re)
        #                                 added_re.append(re_var_names)

                        
        #                 for m in m_list: 
        #                     if m not in added_re: 
        #                         table_body = random_effects[0] # Tbody(rows)
        #                         for row in table_body['props']['children']: 
        #                             re_var_names = row['props']['id'].split('_random_effects')[0]
        #                             if m in re_var_names: 
        #                                 new_row = html.Tr(children=row['props']['children'], id=row['props']['id'], hidden=True)
        #                             if new_row not in rows: 
        #                                 rows.append(new_row)
        #                                 assert(re_var_names not in added_re)
        #                                 added_re.append(re_var_names)
                              
        #             # # If there are no main effects selected, hide all rows
        #             # else:
        #             #     table_body = random_effects[0] # Tbody(rows)
                        
        #             #     for row in table_body['props']['children']: 
        #             #         new_row = html.Tr(children=row['props']['children'], id=row['props']['id'], hidden=True)
        #             #         rows.append(new_row)
            
        #     table_body = random_effects[0] # Tbody(rows)
        #     for r in all_re: 
        #         if r not in added_re: 
        #             print(r)
        #             for row in table_body['props']['children']: 
        #                 re_var_names = row['props']['id'].split('_random_effects')[0]
        #                 if r in re_var_names: 
        #                     new_row = html.Tr(children=row['props']['children'], id=row['props']['id'], hidden=False)
        #                     rows.append(new_row)
                
        #     if interaction_switch: 
        #         pass
            
        #     if not main_switch and not interaction_switch: 
        #         raise PreventUpdate


        #     # print(rows)
        #     if len(rows) == 0: 
        #         print(main_effects)
        #         print(random_effects)
        #         print(rows)
        #     output = [html.Tbody(children=rows)]
        #     return output
    

        # @app.callback(
        #     [Output({'type': 'random_slope', 'index': MATCH}, 'value'),
        #     Output({'type': 'random_intercept', 'index': MATCH}, 'value'),
        #     Output({'type': 'correlated_random_slope_intercept', 'index': MATCH}, 'value')],
        #     [Input({'type': 'random_slope', 'index': MATCH}, 'value'),
        #     Input({'type': 'random_intercept', 'index': MATCH}, 'value'),
        #     Input({'type': 'correlated_random_slope_intercept', 'index': MATCH}, 'value')],
        #     [State({'type': 'random_slope', 'index': MATCH}, 'options'),
        #     State({'type': 'random_intercept', 'index': MATCH}, 'options'),
        #     State({'type': 'correlated_random_slope_intercept', 'index': MATCH}, 'options')]
        # )
        # def sync_correlated_random_effects(slope_value, intercept_value, old_corr_value, slope_options, intercept_options, corr_options): 
        #     # TODO: Use the cache rather than string comparisons here?
        #     ctx = dash.callback_context
        #     trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        #     trigger_val = ctx.triggered[0]['value']

        #     slope_type = '"type":"random_slope"'
        #     intercept_type = '"type":"random_intercept"'
        #     correlated_type = '"type":"correlated_random_slope_intercept"'
            
        #     # Updated the slope selection 
        #     if slope_type in trigger_id:
        #         if len(trigger_val) > 0: 
        #             if len(intercept_value) > 0: 
        #                 new_corr_value = corr_options[0]['value']
        #                 return slope_value, intercept_value, new_corr_value
        #             return slope_value, list(), None
        #         else:
        #             return slope_value, intercept_value, None
        #     elif intercept_type in trigger_id: 
        #         if len(trigger_val) > 0: 
        #             assert(intercept_value is not None)
        #             if len(slope_value) > 0: 
        #                 new_corr_value = corr_options[0]['value']
        #                 return slope_value, intercept_value, new_corr_value
        #             else: 
        #                 return list(), intercept_value, None
        #         else: 
        #             return slope_value, intercept_value, None
        #     elif correlated_type in trigger_id:
        #         new_slope_value = slope_options[0]['value']
        #         new_intercept_value = intercept_options[0]['value']
        #         return [new_slope_value], [new_intercept_value], old_corr_value

        #     # Nothing is selected
        #     raise PreventUpdate
                
        # @app.callback(
        #     [Output(f"{i}_collapse", "is_open") for i in ['two-way', 'n-way']],
        #     [Input(f"{i}_toggle", "n_clicks") for i in ['two-way', 'n-way']],
        #     [State(f"{i}_collapse", "is_open") for i in ['two-way', 'n-way']],
        # )
        # def toggle_accordion(n1, n2, is_open1, is_open2):
        #     ctx = dash.callback_context

        #     if not ctx.triggered:
        #         return False, False
        #     else:
        #         button_id = ctx.triggered[0]["prop_id"].split(".")[0]

        #     if button_id == "two-way_toggle" and n1:
        #         return not is_open1, is_open2
        #     elif button_id == "n-way_toggle" and n2:
        #         return is_open1, not is_open2
        #     return False, False

        @app.callback(
            [Output('family_options', 'options'),
            Output('link_options', 'options')],
            [Input('family_options', 'value'),
            Input('family_options', 'options'),
            Input('link_options', 'options'),
            Input('family_link_switch', 'value')]
        )
        def update_and_save_family_link_options(family, family_options, link_options, fl_switch,): 
            global __str_to_z3__
            
            ctx = dash.callback_context

            if not ctx.triggered:
                return family_options, link_options
            # else
            trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
            if trigger_id == 'family_options':
                new_options = list()

                if family is not None: 
                    # Get link options
                    assert(family in __str_to_z3__.keys())
                    family_fact = __str_to_z3__[family]
                    link_options = self.family_link_options[family_fact]
                    
                    for link in link_options: 
                        # "Prettify" link names before rendering
                        label = str(link).split('Transform')[0]
                        # label += ' link'

                        # Is the link the default for this family? 
                        assert(self.default_family_link[family_fact])
                        if link in self.default_family_link[family_fact]: 
                            label += '(default)'

                        new_options.append({'label': label, 'value': str(link)})                    
                    
                    return family_options, new_options
                else: 
                    print(trigger_id)
            elif trigger_id == 'family_link_switch': 
                trigger_val = ctx.triggered[0]['value']
                
                # Did we lock? 
                if trigger_val:
                    new_family_options = list() 
                    new_link_options = list() 

                    for f in family_options:
                        new_family_options.append({'label': f['label'], 'value': f['value'], 'disabled': True}) 
                    
                    for l in link_options:
                        new_link_options.append({'label': l['label'], 'value': l['value'], 'disabled': True}) 
                    
                    return new_family_options, new_link_options

                # Did we unlock?
                else: 
                    
                    new_family_options = list() 
                    new_link_options = list() 

                    for f in family_options:
                        new_family_options.append({'label': f['label'], 'value': f['value'], 'disabled': False}) 
                    
                    for l in link_options:
                        new_link_options.append({'label': l['label'], 'value': l['value'], 'disabled': False}) 
                    
                    return new_family_options, new_link_options
            else: 
                raise PreventUpdate

        @app.callback(
            Output('data_dist', 'figure'),
            Input('family_options', 'value'),
            State('data_dist', 'figure')
        )
        def update_chart_family(family, link): 
            global __str_to_z3__
            
            if family is not None: 
                assert(isinstance(family, str))
                family_fact = __str_to_z3__[family]

                # Get current data 
                (curr_data, curr_label) = self.get_data_dist()

                # Get data for family
                key = f'{family}_data'
                
                # Do we need to generate data?
                if key not in __str_to_z3__.keys(): 
                    family_data = generate_data_dist_from_facts(fact=family_fact, design=self.design)
                    # Store data for family in __str_to_z3__ cache
                    __str_to_z3__[key] = family_data
                # We already have the data generated in our "cache"
                else: 
                    family_data = __str_to_z3__[key]

                # if link is not None: 
                #     assert(isinstance(link, str))
                #     link_fact = __str_to_z3__[link]
                #     # Transform the data 
                #     transformed_data = transform_data_from_fact(data=family_data, link_fact=link_fact)

                # Generate figure 
                fig = go.Figure()
                fig.add_trace(go.Histogram(x=curr_data, name=f'{self.design.dv.name}',))
                fig.add_trace(go.Histogram(x=family_data, name=f'Simulated {family} distribution.'))
                fig.update_layout(barmode='overlay')
                fig.update_traces(opacity=0.75)
                fig.update_layout(legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ))

                return fig
                
            else: 
                raise PreventUpdate

        @app.callback(
            [Output('generate_code', 'disabled'),
            Output('session_store', 'data')],
            [Input('main_effects_switch', 'value'),
            Input('interaction_effects_switch', 'value'),
            Input('random_effects_switch', 'value'),
            Input('family_link_switch', 'value'),
            Input({'type': 'main_effects_options', 'index': ALL}, 'value'),
            Input({'type': 'interaction_effects_options', 'index': ALL}, 'value'),
            Input('random_effects_table', 'children'),
            Input('family_options', 'value'), 
            Input('link_options', 'value')]
        )
        def enable_code_generation(me_switch, i_switch, re_switch, fl_switch, main_effects, interaction_effects, random_effects, family, link): 
            global __str_to_z3__

            model_spec = dict()
            # If all the switches are turned on/True
            if me_switch and i_switch and re_switch and fl_switch: 
                
                # Get all the values
                main_facts = list()
                for m_list in main_effects: 
                    assert(isinstance(m_list, list))
                    for m in m_list: 
                        fact = __str_to_z3__[m]
                        main_facts.append(str(fact))
                model_spec['main_effects'] = main_facts

                ixn_facts = list()
                for i_list in interaction_effects: 
                    assert(isinstance(i_list, list))
                    for i in i_list: 
                        fact = __str_to_z3__[i]
                        ixn_facts.append(str(fact))
                model_spec['interaction_effects'] = ixn_facts

                re_facts = list() 
                random_effects_values = self.get_random_effects_values_from_table(random_effects)
                for re in random_effects_values: 
                    # Is this a joint correlated/uncorrelated example? 
                    if '_OR_' in re: 
                        # Look at the radio buttons 
                        pass

                    else: 
                        fact = __str_to_z3__[re]
                        re_facts.append(str(fact))
                model_spec['random_effects'] = re_facts

                if family is not None: 
                    model_spec['family'] = str(__str_to_z3__[family])
                else: 
                    model_spec['family'] = None
                if link is not None: 
                    model_spec['link'] = str(__str_to_z3__[link])
                else: 
                    model_spec['link'] = None
            
                # Write out all the values 
                assert(isinstance(model_spec, dict))
                json_model_spec = json.dumps(model_spec)
                return False, json_model_spec
                
            assert(isinstance(model_spec, dict))
            json_model_spec = json.dumps(model_spec)
            return True, json_model_spec # disable: True

        @app.callback(
            [Output('code_gen_modal', 'is_open'),
            Output('model_spec_issue_ivs', 'is_open'),
            Output('model_spec_issue_family', 'is_open'),
            Output('model_spec_issue_link', 'is_open')],
            [Input('generate_code', 'n_clicks'),
            Input('close', 'n_clicks'),
            Input('keep_open', 'n_clicks'),
            Input('got_it_ivs', 'n_clicks'),
            Input('got_it_family', 'n_clicks'),
            Input('got_it_link', 'n_clicks'),
            Input('session_store', 'data')],
            State('code_gen_modal', 'is_open')
        )
        def generate_code(generate_code_click, close_click, keep_open_click, got_it_ivs, got_it_family, got_it_link, model_spec, is_open): 
            if generate_code_click or close_click or keep_open_click or got_it_ivs or got_it_family or got_it_link:
                # Check that there is enough info to create a statistical model
                (is_valid_model, problem) = self.check_model_specification(model_spec)
                
                if is_valid_model: 
                    # Write out a model spec!
                    assert(isinstance(model_spec, str))
                    # model_spec = json.loads(model_spec)
                    # assert(isinstance(model_spec, dict))
                    write_data(model_spec)
                else: 
                    if problem == 'independent variables': 
                        return not is_open, not is_open, not is_open, not is_open 
                    elif problem == 'family': 
                        return not is_open, not is_open, not is_open, not is_open 
                    elif problem == 'link': 
                        return not is_open, not is_open, not is_open, not is_open 
                if close_click: 
                    self.shutdown()
                return not is_open, False, False, False
            return is_open, False, False, False
        
        ##### Start and run app on local server
        self.app = app
        open_browser()
        app.run_server(debug=False, threaded=True, port=port)
        
    def create_switch(self, switch_id: str, form_group_id: str): 
        switch = dbc.FormGroup([
                dbc.Checklist(
                    options=[
                        {"label": "🔐", "value": False}
                    ],
                    value=[],
                    id=switch_id,
                    switch=True,
                    style={'float': 'right'}
                ),
            ],
            id=form_group_id
        )

        return switch
        
    def layout_main_effects_div(self, main_effects: Dict[str, List[AbstractVariable]]): 
        ##### Collect all elements
        # Create main effects title 
        main_title = html.Div([
            dcc.Markdown('''
            ### Independent Variables
            #### Do you want to want to add or remove independent variables?
            *Based on the relationships you specified earlier, the following variables directly impact the dependent variable.*
            ''')
            
            # html.H3('Independent variables'),
            # html.H6('You already specified a few independent variables. Do you want to add any more?'),
            # dbc.Alert(
            #     '', className="mb-0",
            #     id="main_alert",
            #     dismissable=True,
            #     fade=True, 
            #     is_open=True
            # )
        ])
        
        # Get form groups for each set of main effects options
        input_fg, derived_direct_fg, derived_transitive_fg = self.populate_main_effects(main_effects)
        
        # Create main effects switch
        main_switch = self.create_switch(switch_id='main_effects_switch', form_group_id='main_effects_group')
        
        ##### Combine all elements
        # Create div 
        labels = list() 
        fg_combo = list()
        if len(input_fg.children[0].options) > 0: 
            labels.append(dbc.Col(self.create_label_tooltip('Specified', 'End-user has already specified these variables as independent variables.'), width=2))
            fg_combo.append(dbc.Col(input_fg, width=2))
        if len(derived_direct_fg.children[0].options) > 0: 
            labels.append(dbc.Col(self.create_label_tooltip('Derived directly', 'These are indepepdent variables that also cause or are associated with the dependent variable but were not specified.'), width=2))
            fg_combo.append(dbc.Col(derived_direct_fg, width=2))
        if len(derived_transitive_fg.children[0].options) > 0: 
            labels.append(dbc.Col(self.create_label_tooltip('Derived transitively', 'These are independent variables that may underlie independent variables that are already specified.'), width=2))
            fg_combo.append(dbc.Col(derived_transitive_fg, width=2))

        main_effects_div = html.Div([
                main_title,
                dbc.Row(labels),
                dbc.Row(fg_combo),
                main_switch
        ])

        ##### Return div
        return main_effects_div

    def layout_interaction_effects_div(self, interaction_effects): 
        

        ##### Collect all elements
        # Create interaction effects title 
        interaction_effects_title = html.Div([
            dcc.Markdown('''
            #### Are there any interactions between variables that you are interested in?
            *Interactions between variables mean that one variable's effect on the dependent variable impacts, or moderates, how another variable affects the dependent variable.*
            ''')
            
            # html.H3('Interaction effects'),
            
            # dbc.Alert(
            #     "TODO: Explanation of interaction effects", className="mb-0",
            #     id="interaction_alert",
            #     dismissable=True,
            #     fade=True, 
            #     is_open=True
            # )
        ])
        
        # Get accordion for the interaction effects (two-way, n-way)
        interaction_effects_acc = self.populate_interaction_effects(interaction_effects)
        
        # Get chart for visualizing interactions
        # two_way_interaction_vis = self.create_two_way_interaction_chart(('HomeWork', 'Race'), self.design.dv, self.design.dataset.dataset)
        # three_way_interaction_vis = self.create_three_way_interaction_chart(('HomeWork', 'Race', 'SES'), self.design.dv, self.design.dataset.dataset)

        # Create interaction effects switch
        interaction_switch = self.create_switch(switch_id='interaction_effects_switch', form_group_id='interaction_effects_group')
        
        
        ##### Combine all elements
        # Create div 

        # There are interaction effects
        has_interactions = False
        for k, val in interaction_effects.items():
            if len(val) > 0:
                has_interactions = True

        if has_interactions:
            interaction_effects_div = html.Div([
                interaction_effects_title, 
                interaction_effects_acc,
                interaction_switch
            ])
        else:
            interaction_switch = dbc.FormGroup([
                dbc.Checklist(
                    options=[
                        {"label": "🔐", "value": False}
                    ],
                    value=True, 
                    id='interaction_effects_switch',
                    switch=True,
                    style={'float': 'right'}
                ),
            ],
            id='interaction_effects_group'
        )
            interaction_effects_div = html.Div([
                interaction_effects_title, 
                interaction_effects_acc,
                interaction_switch
            ],
            hidden=True)

        ##### Return div
        return interaction_effects_div

    def layout_random_effects_div(self, random_effects): 
        
        ##### Collect all elements
        # Create random effects title 
        random_effects_title = html.Div([
            dcc.Markdown('''
            #### There are clusters within your data.
            *Based on the relationships you specified in your program, Tisane has identified the following random effects to account for in order to maximize your statistical power.*
            ''')
            
        ])

        # Create description 
        # random_descrip = dcc.Markdown('''
        # ##### Based on the relationships you specified in your program, Tisane has identified the following random effects.
        # *These constitute the maximal effects sturcture for your model.*
        # ''')
    
        # Create interaction effects switch
        random_switch = self.create_switch(switch_id='random_effects_switch', form_group_id='random_effects_group')

        ##### Combine all elements
        # Create table: 
        table = self.populate_random_effects(random_effects)

        # Create div 
        # There are random effects
        if random_effects is not None:
            random_effects_div = html.Div([
                random_effects_title, 
                # random_descrip, 
                table,
                random_switch
            ])
        else:
            random_switch = dbc.FormGroup([
                dbc.Checklist(
                    options=[
                        {"label": "🔐", "value": False}
                    ],
                    value=[True],
                    id='random_effects_switch',
                    switch=True,
                    style={'float': 'right'}
                ),
            ],
            id='random_effects_group'
        )
            random_effects_div = html.Div([
                random_effects_title, 
                # random_descrip, 
                table,
                random_switch
            ],
            hidden=True)

        ##### Return div
        return random_effects_div


    def layout_family_link_div(self, family_link: Dict[z3.BoolRef, List[z3.BoolRef]]): 
        ##### Collect all elements
        # Create family and link title 
        family_link_title = html.Div([
            dcc.Markdown('''
            ### Data distributions: Family and Link functions.
            #### Which distribution best matches your data?
            ''')
            
            # html.H3('Family and Link: Data distributions'),
            # dbc.Alert(
            #     "TODO: Explanation of family and link functions", className="mb-0",
            #     id='family_link_alert',
            #     dismissable=True,
            #     fade=True, 
            #     is_open=True
            # )
        ])
        
        # Get form groups for family link div
        family_link_chart = self.draw_data_dist()
        family_link_controls = self.make_family_link_options(family_link)    

        # Create main effects switch
        family_link_switch = self.create_switch(switch_id='family_link_switch', form_group_id='family_link_group')
        
        ##### Combine all elements
        # Create div
        family_and_link_div = html.Div([
            family_link_title,
            dbc.Row(
                [
                    dbc.Col(family_link_chart, md=8),
                    dbc.Col(family_link_controls, md=4),
                ],
                align="center",
            ),
            family_link_switch
        ])
        
        ##### Return div
        return family_and_link_div 

    # @param main_effects is a dictionary of pre-generated possible main effects
    def populate_main_effects(self, main_effects: Dict[str, List[AbstractVariable]]): 
        global __str_to_z3__

        dv = self.design.dv # Might want to get rid of this
        output = list()

        # TODO: We could lay them out in separate divs for query | Tisane recommended | not included.
        # Lay main_effects options out
        input_options = list()
        input_selected = list()
        derived_direct_options = list()
        derived_transitive_options = list()
        for (tag, variables) in main_effects.items(): 
            for v in variables:
                
                # Add to global map of str to z3 facts
                fact = FixedEffect(v.const, dv.const)
                __str_to_z3__[str(fact)] = fact

                if tag == 'input':
                    input_options.append({'label': str(v.name), 'value': f'{str(fact)}'})
                    input_selected.append(f'{str(fact)}')
                elif tag == 'derived_direct':
                    derived_direct_options.append({'label': str(v.name), 'value': f'{str(fact)}'})
                elif tag == 'derived_transitive':
                    derived_transitive_options.append({'label': str(v.name), 'value': f'{str(fact)}'})
                # variable_options.append({'label': str(v.name), 'value': f'{FixedEffect(v.name, dv.name)}'})
        
        input_fg = dbc.FormGroup([
            dbc.Checklist(
                options=input_options,
                value=input_selected,
                id={'type': 'main_effects_options', 'index': 'input_options'}
            ),
        ])
        derived_direct_fg = dbc.FormGroup([
            dbc.Checklist(
                options=derived_direct_options, 
                value=[],
                id={'type': 'main_effects_options', 'index': 'derived_direct_options'}
            )
        ])
        derived_transitive_fg = dbc.FormGroup([
            dbc.Checklist(
                options=derived_transitive_options, 
                value=[],
                id={'type': 'main_effects_options', 'index': 'derived_transitive_options'}
            )
        ])

        return input_fg, derived_direct_fg, derived_transitive_fg

    def populate_interaction_effects(self, interaction_effects: List[Tuple[AbstractVariable, ...]]): 
        global __str_to_z3__

        vis_charts = list()
        output = list()

        # TODO: Build Summary checklist

        # Lay them out
        for (num_interactions, options) in interaction_effects.items(): 
            interaction_options = list()
            for ixn in options:
                ixn_names = [v.name for v in ixn]
                name = '*'.join(ixn_names)
                interaction_options.append({'label': name, 'value': name}) # TODO: Update the value

                # Add to global map of str to z3 facts
                # Create set for interaction
                fact = EmptySet(Object)
                for v in ixn:
                    fact = SetAdd(fact, v.const)
                __str_to_z3__[name] = fact
            
            # output.append(self.make_interaction_card(title=num_interactions, options=interaction_options))
                
                chart = self.make_interaction_vis(title=f'{num_interactions} visualized', interaction=ixn)
                # vis_charts.append(chart)
                vis_charts.append(dbc.Col(chart, className='w-50'))
            
            # summary_card = self.make_interaction_summary_card(title=num_interactions, options=interaction_options)
            # vis_card = self.make_interaction_vis_card(title=num_interactions, vis_cards=vis_charts)
            # output.append(summary_card)
            # output.append(vis_card)
            # output.append(vis_charts)

        # Format vis_chars to so that there are only two per row
        chart_rows = list()
        i = 0 
        while i in range(len(vis_charts)): 
            if i + 1 < len(vis_charts): 
                row = dbc.Row([vis_charts[i], vis_charts[i+1]])
                i+=2
            else: 
                row = dbc.Row([vis_charts[i]])
                i+=1
            chart_rows.append(row)
            
        return html.Div(chart_rows)
    
    # @param data to make categorical 
    # @return new list with @param values that are split into 3 groups: low, medium, high 
    # Low: (,-centered std) | Medium: [-centered std, +centered std] | High: (+centered_std, )
    def get_categorical_data(self, data: pd.Series): 
        mean = data.mean()
        centered_data = data - mean 
        centered_std = centered_data.std()
        centered_mean = centered_data.mean()
        assert(int(centered_mean) == 0)

        # Divide into 3 categorical groups
        cat_data = list()
        for val in centered_data: 
            # low
            if val < (0 - centered_std): 
                cat_data.append('- 1 SD')
            # high
            elif val > (0 + centered_std):
                cat_data.append('+ 1 SD')
            # medium
            else: 
                cat_data.append('Mean')

        return cat_data

    def create_two_way_interaction_chart(self, interaction: Tuple[AbstractVariable, AbstractVariable], dv: AbstractVariable, data: pd.DataFrame):
        assert(len(interaction) == 2)
        (x1, x2) = interaction 
        if isinstance(x1, Numeric) and isinstance(x2, Nominal): 
            x = x1
            color_group = x2
        elif isinstance(x1, Numeric) and isinstance(x2, Ordinal): 
            x = x1
            color_group = x2
        elif isinstance(x1, Numeric) and isinstance(x2, Numeric): 
            x1_data = self.design.get_data(x1)
            x2_data = self.design.get_data(x2)

            if x1_data.nunique() <= x2_data.nunique(): 
                x = x2
                color_group = x1

                color_data_cat = self.get_categorical_data(x1_data)
                color_group_cat_name = f'{color_group.name}_categorized'
            else: 
                x = x1
                color_group = x2
            
                color_data_cat = self.get_categorical_data(x2_data)
                color_group_cat_name = f'{color_group.name}_categorized'

            data[color_group_cat_name] = pd.Series(color_data_cat, index=data.index)
            fig = px.scatter(data, x=x.name, y=dv.name, color=color_group_cat_name, trendline='ols')
            fig_elt = dcc.Graph(id=f'two_way_interaction_chart_{x.name}_{color_group.name}', figure=fig)        
    
            return fig_elt

        elif isinstance(x1, Nominal) and isinstance(x2, Numeric):
            x = x2
            color_group = x1
        elif isinstance(x1, Nominal) and isinstance(x2, Ordinal): 
            x = x2
            color_group = x1
        elif isinstance(x1, Ordinal) and isinstance(x2, Numeric): 
            x = x1
            color_group = x2
        elif isinstance(x1, Ordinal) and isinstance(x2, Ordinal): 
            x = x1
            color_group = x2
        else: 
            x = x1
            color_group = x2
        
        fig = px.scatter(data, x=x.name, y=dv.name, color=color_group.name, trendline='ols')
        fig_elt = dcc.Graph(id=f'two_way_interaction_chart_{x.name}_{color_group.name}', figure=fig)        
        
        return fig_elt

    def create_three_way_interaction_chart(self, interaction: Tuple[AbstractVariable, AbstractVariable, AbstractVariable], dv: AbstractVariable, data: pd.DataFrame):
        assert(len(interaction) == 3)

        (x1, x2, x3) = interaction 

        categorical_count = 0
        categorical_variables = list()

        if isinstance(x1, Nominal) or isinstance(x1, Ordinal): 
            categorical_count += 1
            categorical_variables.append(x1)
        if isinstance(x2, Nominal) or isinstance(x2, Ordinal): 
            categorical_count += 1
            categorical_variables.append(x2)
        if isinstance(x3, Nominal) or isinstance(x3, Ordinal): 
            categorical_count += 1
            categorical_variables.append(x3)

        # Are there at least two variables that are categorical?
        if categorical_count == 0: 
            # Order variables based on cardinality 
            cardinality = list()
            cardinality_to_variable = dict() 
            for i in interaction: 
                i_card = self.design.get_data(i).nunique()
                cardinality.append(i_card)
                cardinality_to_variable[i_card] = i
                
            cardinality.sort()
            x = cardinality_to_variable[cardinality[2]]
            
            facet_var = cardinality_to_variable[cardinality[1]]
            facet_data = self.design.get_data(facet_var)
            facet_data_cat = self.get_categorical_data(facet_data)
            facet_data_cat_name = f'{facet_var.name}_categorized'
            data[facet_data_cat_name] = pd.Series(facet_data_cat, index=data.index)

            color_group_var = cardinality_to_variable[cardinality[0]]
            color_group_data = self.design.get_data(color_group_var)
            color_group_data_cat = self.get_categorical_data(color_group_data)
            color_group_data_cat_name = f'{color_group_var.name}_categorized'
            data[color_group_data_cat_name] = pd.Series(color_group_data_cat, index=data.index)

            fig = px.scatter(data, x=x.name, y=dv.name, color=color_group_data_cat_name, facet_col=facet_data_cat_name, trendline='ols')
            fig_elt = dcc.Graph(id=f'three_way_interaction_chart_{x.name}_{color_group_data_cat_name}_{facet_data_cat_name}', figure=fig)        

        elif categorical_count == 1: 
            cat_var = categorical_variables[0]
            lower_cardinality_var = None 
            higher_cardinality_var = None

            for i in interaction: 
                if i not in categorical_variables: 
                    i_data = self.design.get_data(i)
                    if higher_cardinality_var is None: 
                        higher_cardinality_var = i
                    else: 
                        if i_data.nunique() > self.design.get_data(higher_cardinality_var).nunique(): 
                            lower_cardinality_var = higher_cardinality_var 
                            higher_cardinality_var = i
                        else: 
                            lower_cardinality_var = i

            lower_data = self.design.get_data(lower_cardinality_var)
            lower_data_cat = self.get_categorical_data(lower_data)
            lower_data_cat_name = f'{lower_cardinality_var.name}_categorized'
            data[lower_data_cat_name] = pd.Series(lower_data_cat, index=data.index)

            x = higher_cardinality_var 
            color_group = cat_var
            facet_name = lower_data_cat_name
            fig = px.scatter(data, x=x.name, y=dv.name, color=color_group.name, facet_col=facet_name, trendline='ols')
            fig_elt = dcc.Graph(id=f'three_way_interaction_chart_{x.name}_{color_group.name}_{facet_name}', figure=fig)        
            
        elif categorical_count == 2:
            for i in interaction: 
                if i not in categorical_variables: 
                    x = i
                    break 
            color_group = categorical_variables[0]
            facet = categorical_variables[1]
            fig = px.scatter(data, x=x.name, y=dv.name, color=color_group.name, facet_col=facet.name, trendline='ols')
            fig_elt = dcc.Graph(id=f'three_way_interaction_chart_{x.name}_{color_group.name}_{facet.name}', figure=fig)        

        elif categorical_count == 3: 
            x = interaction[0]
            color_group = interaction[1]
            facet = interaction[2]
            fig = px.scatter(data, x=x.name, y=dv.name, color=color_group.name, facet_col=facet.name, trendline='ols')
            fig_elt = dcc.Graph(id=f'three_way_interaction_chart_{x.name}_{color_group.name}_{facet.name}', figure=fig)        
    

        # fig_elt = dcc.Graph(id=f'three_way_interaction_chart_{x.name}_{color_group.name}_{facet.name}', figure=fig)        
        
        return fig_elt

    def populate_random_effects(self, random_effects: List): 
        global __str_to_z3__

        rows = list()
        
        # There are no random effects
        if random_effects is None:
            table_body = [html.Tbody(children=rows)]
            table = dbc.Table(children=table_body, striped=False, bordered=False, id='random_effects_table')

            # return output
            return html.Div(id='random_effects_div', children=table)
    

        re_dict = self.reorganize_random_effects(random_effects)
        
        # Create table rows with the information
        for var_name, data in re_dict.items(): 
            
            # There is exactly one possible value
            if len(data) == 1: 
                d = data[0]
                fact = d['fact']
                re = d['effect']
                assert(isinstance(re, RandomIntercept))

                # Add random effect fact to global map
                __str_to_z3__[str(fact)] = fact
                

                name = html.P(var_name)
                badges = list()
                ri_badge = dbc.Badge("Random intercept", pill=True, color="info", className="mr-1", id=f'{fact}')
                badges.append(ri_badge)

                content = [name] + badges
                if '_IMPLIED_' in var_name: 
                    row = html.Tr(
                        children=[html.Td(children=content)],
                        hidden=True,
                        id=f'{var_name}_random_effects',
                    )
                else: 
                    row = html.Tr(
                        children=[html.Td(children=content)],
                        hidden=False,
                        id=f'{var_name}_random_effects'
                    )

            elif len(data) > 1: 
                facts = dict()
                for d in data: 
                    fact = d['fact']
                    re = d['effect']

                    # Add random effect fact to global map
                    __str_to_z3__[str(fact)] = fact
                    
                    
                    import pdb; pdb.set_trace()
                    assert(isinstance(re, CorrelatedRandomSlopeAndIntercept) or isinstance(re, UncorrelatedRandomSlopeAndIntercept))
                    if isinstance(re, CorrelatedRandomSlopeAndIntercept): 
                        facts['Correlated'] = fact
                    if isinstance(re, UncorrelatedRandomSlopeAndIntercept): 
                        facts['Uncorrelated'] = fact
                
                assert(len(var_name) > 1)
                v_names = [v for v in var_name]
                name_str = ' within '.join(v_names)
                name = html.P(name_str)
                badges = list() 
                
                facts_str = [str(v) for (k, v) in facts.items()]
                val = '_OR_'.join(facts_str)
                ri_badge = dbc.Badge("Random intercept", pill=True, color="info", className="mr-1", id=f'{val}_intercept')
                rs_badge = dbc.Badge("Random slope", pill=True, color="primary", className="mr-1", id=f'{val}_slope')
                badges.append(ri_badge)
                badges.append(rs_badge)
                
                correlated_radio_items = self.create_correlated_radio_items(facts)
                
                content = [name] + badges
                
                row = html.Tr(
                    children=[html.Td(children=content), html.Td(children=correlated_radio_items)],
                    hidden=False,
                    id=f'{name_str}_random_effects'
                )
            
            rows.append(row)

        table_body = [html.Tbody(children=rows)]
        table = dbc.Table(children=table_body, striped=False, bordered=False, id='random_effects_table')

        # return output
        return html.Div(id='random_effects_div', children=table)
    
    def create_correlated_radio_items(self, facts: Dict[str, z3.BoolRef]): 
        correlated_fact = facts['Correlated']
        uncorrelated_fact = facts['Uncorrelated']

        corr_radioitems = dbc.FormGroup(
            [
                dbc.RadioItems(
                    options=[
                        {"label": "Correlated", "value": f'{str(correlated_fact)}', 'disabled': False},
                        {"label": "Uncorrelated", "value": f'{str(uncorrelated_fact)}', 'disabled': False},
                    ],
                    value=f'{str(correlated_fact)}',
                    id=f"{'_OR'.join(facts)}_choice",
                    inline=True,
                ),
            ]
        )

        return corr_radioitems
    
    def reorganize_random_effects(self, random_effects: List): 
        re_dict = dict() 

        # Add all facts to dict
        for (re_fact, re) in random_effects: 
            if isinstance(re, RandomIntercept):
                group = re.groups 

                key = group.name
                val = {'fact': re_fact, 'effect': re}
                if key not in re_dict.keys(): 
                    re_dict[key] = list() 
                re_dict[key].append(val)
            elif isinstance(re, RandomSlope):
                iv = re.iv
                group = re.groups
                
                key = (iv.name, group.name)
                val = {'fact': re_fact, 'effect': re}
                if key not in re_dict.keys(): 
                    re_dict[key] = list() 
                re_dict[key].append(val)
            elif isinstance(re, CorrelatedRandomSlopeAndIntercept): 
                iv = re.iv
                group = re.groups
                
                key = (iv.name, group.name)
                val = {'fact': re_fact, 'effect': re}
                if key not in re_dict.keys(): 
                    re_dict[key] = list() 
                re_dict[key].append(val)
            elif isinstance(re, UncorrelatedRandomSlopeAndIntercept): 
                iv = re.iv
                group = re.groups
                
                key = (iv.name, group.name)
                val = {'fact': re_fact, 'effect': re}
                if key not in re_dict.keys(): 
                    re_dict[key] = list() 
                re_dict[key].append(val)
        
        # Update dict in case there are repeated groups
        to_delete = list()
        new_entries = dict() 
        for var_name, val in re_dict.items(): 
            # This variable is part of another random effect
            existing_keys = re_dict.keys()
            
            for ek in existing_keys: 
                if isinstance(ek, str): 
                    pass
                elif isinstance(ek, tuple): 
                    if var_name in ek: 
                        new_key = var_name + '_IMPLIED_'

                        # Keep track of entries to add
                        new_entries[new_key] = re_dict[var_name]
                        # Keep track of entries to delete
                        to_delete.append(var_name)
        
        # Add entries
        for k, v in new_entries.items():
            re_dict[k] = v
        # Delete entries
        for d in to_delete: 
            del re_dict[d]

        return re_dict

    def get_random_effects_values_from_table(self, random_effects_table): 
        re_values = list() 

        table_body = random_effects_table[0]
        
        table_rows = table_body['props']['children']

        for row in table_rows: 
            # Is the row visible? 
            if row['props']['hidden'] is False: 
                row_c = row['props']['children']
                row_c = row_c[0] # Get the html.Td wrapping around the label and badges
                content = row_c['props']['children'] # Get to the content

                if len(content) == 2:
                    badges = content[1]
                    # Get id, which contains fact for random effect
                    fact = badges['props']['id']
                    re_values.append(fact)
                elif len(content) == 3:
                    badges = [content[1], content[2]] # Random Slope and Random Intercept
                    # Get radio buttons
                    radio_wrapper = row['props']['children'][1]
                    radio_wrapper = radio_wrapper['props']['children']
                    radio_wrapper = radio_wrapper['props']['children']
                    radio_val = radio_wrapper[0]['props']['value']
                    re_values.append(radio_val)
        
        return re_values 

    def get_data_dist(self): 
        hist_data = None 
        labels = None 

        dv = self.design.dv
        
        data = self.design.get_data(variable=dv)
        
        if data is not None: 
            hist_data = data
            labels = dv.name
        
        return (hist_data, labels)

    def draw_dist(self, hist_data, label): 
        # Make sure that there is data to draw
        # Hist_data is not None and labels is not None
        if hist_data is not None and label is not None: 
            data = pd.DataFrame(hist_data, columns=[label])

            fig = px.histogram(data, x=label)
            fig.update_layout(legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ))

            fig_elt = dcc.Graph(id='data_dist', figure=fig)
        else: 
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=[-1, 3, 5, 10, 12],
                y=[10, 8, 5, 4, 0],
                mode="markers+text",
                # name="Markers and Text",
                text=['', 'No data supplied!', 'Imagine how your data will look when you collect it...', '...by looking at possible distributions  -->. :]',''],
                textposition="bottom center"
            ))

            fig_elt = dcc.Graph(id='data_dist', figure=fig)
            
        return fig_elt
        
    def draw_data_dist(self): 
        (hist_data, labels) = self.get_data_dist()
        
        return self.draw_dist(hist_data, labels)

    def populate_data_distributions(self): 
        output = list() 

        (data, labels) = self.get_possible_family_distributions()

        # fig = px.histogram(family_data, x=f"{Value of self.design.dv.name}", y="frequency", color="dist", marginal="rug",
        #                 hover_data=df.columns)

        fig = ff.create_distplot(data, labels, showlegend=False)
        output.append(html.Div([
            html.H3(str(dist)),  
            dcc.Graph(figure=fig)
            ]))

        return html.Div(output)
    
    def get_possible_family_distributions(self): 
        dist_names = self.synthesizer.generate_family_distributions(design=self.design)

        data = list()
        labels = list()
        for dist in dist_names: 
            data.append(generate_data_dist_from_facts(fact=dist, design=self.design))
            labels.append(f'{self.design.dv.name} with {dist}')

        return (data, labels)    

    def get_data_for_family_distribution(self, family_fact: z3.BoolRef): 
        global __str_to_z3__

        key = f'{str(family_fact)}_data'
        if key in __str_to_z3__.keys(): 
            return __str_to_z3__[key]
        else: 
            val = generate_data_dist_from_facts(fact=family_fact, design=self.design)
            __str_to_z3__[key] = val
            return val

    def populate_compound_family_div(self): 

        (curr_data_dist, curr_data_label) = self.get_data_dist()

        (possible_family_dists, possible_family_labels) = self.get_possible_family_distributions()

        # Combine data
        data = curr_data_dist + possible_family_dists
        labels = curr_data_label + possible_family_labels 

        fig = ff.create_distplot(data, labels)
        fig_div = html.Div([
            # html.H3(str(dist)),  
            dcc.Graph(figure=fig)
            ])

        return fig_div

    # TODO: Need to add callbacks to this...
    def populate_link_div(self): 
        output = list()

        # Get Family: Link functions
        dist_link_dict = dict()
        dist_names = self.synthesizer.generate_family_distributions(design=self.design)
        for dist in dist_names: 
            dist_link_dict[dist] = self.get_link_options(dist)

        for family, links in dist_link_dict.items(): 
            options = list() 
            for l in links: 
                default = None # TODO: Start at default (Identity usually)
                options.append({'label': f'{str(l)}', 'value': str(l)})

            # Create HTML div
            output.append(dbc.FormGroup(
                [
                    dbc.Label(f'{str(family)}', 
                        # style={'visibility': 'hidden'}
                    ),
                    dbc.RadioItems(
                        id=f'{str(family)}_link_options',
                        options=options,
                        value=None, # TODO: Start at default (Identity usually)
                        inline=True,
                        # style={'visibility': 'hidden'}
                    ),
                ]
            ))
        return html.Div(output)

    def create_label_tooltip(self, label: str, description: str): 
        name = label.replace(' ', '_')
        tooltip = html.Div(
            [
                html.P(
                    [
                        html.Span(
                            label,
                            id=f'{name}_tooltip_target',
                            style={"textDecoration": "underline", "cursor": "pointer"},
                        )
                    ]
                ),
                dbc.Tooltip(
                    description,
                    target=f'{name}_tooltip_target',
                )
            ]
        )   

        return tooltip

    def create_main_effects_div(self, input_fg, derived_direct_fg, derived_transitive_fg, main_title, main_switch): 
        labels = list() 
        fg_combo = list()
        if len(input_fg.children[0].options) > 0: 
            # TODO: Start here: Add tooltips to all 
            labels.append(dbc.Col(self.create_label_tooltip('Specified', 'End-user has already specified these variables as independent variables.'), width=2))
            fg_combo.append(dbc.Col(input_fg, width=2))
        if len(derived_direct_fg.children[0].options) > 0: 
            labels.append(dbc.Col(self.create_label_tooltip('Derived directly', 'These are indepepdent variables that also cause or are associated with the dependent variable but were not specified.'), width=2))
            fg_combo.append(dbc.Col(derived_direct_fg, width=2))
        if len(derived_transitive_fg.children[0].options) > 0: 
            labels.append(dbc.Col(self.create_label_tooltip('Derived transitively', 'These are independent variables that may underlie independent variables that are already specified.'), width=2))
            fg_combo.append(dbc.Col(derived_transitive_fg, width=2))

        main_effects_div = html.Div([
                main_title,
                dbc.Row(labels),
                dbc.Row(fg_combo),
                main_switch
        ])

        return main_effects_div

    def get_link_options(self, family_fact: z3.BoolRef): 
         
        link_functions = self.synthesizer.generate_link_functions(design=self.design, family_fact=family_fact)

        return link_functions
    
    # def make_family_options(self): 
    #     global __str_to_z3__ 

    #     options = list()

    #     dist_names = self.synthesizer.generate_family_distributions(design=self.design)

    #     for d in dist_names: 
    #         __str_to_z3__[str(d)] = d
    #         options.append({'label': str(d), 'value': str(d)})
        
    #     return options

    def make_family_link_options(self, family_link_options): 
        global __str_to_z3__

        family_options = list()
        
        for f in family_link_options.keys(): 
            label = str(f)
            label = str(f).split('Family')[0]
            if label == 'InverseGaussian': 
                label = 'Inverse Gaussian' # add a space

            family_options.append({'label': label, 'value': str(f)})

        controls = dbc.Card(
            [
                dbc.FormGroup(
                    [
                        dbc.Label('Family'),
                        dcc.Dropdown(
                            # id={'type': 'family_link_options', 'index': 'family_options'},
                            id='family_options',
                            options=family_options,
                            value=None,
                        ),
                    ]
                ),
                dbc.FormGroup(
                    [
                        dbc.Label('Link function'),
                        dcc.Dropdown(
                            # id={'type': 'family_link_options', 'index': 'link_options'},
                            id='link_options',
                            options=[],
                            value=None,
                        ),
                    ]
                )
            ],
            body=True,
            id={'type': 'family_link_options', 'index': 'family_link_options'},
        )

        return controls

    def make_interaction_vis_card(self, title: str, vis_cards: List[dbc.Card]): 
        card = dbc.Card([
            dbc.CardHeader(
                html.H2(
                    dbc.Button(
                        f"{title}",
                        color="link",
                        id=f"{title}_vis_toggle",
                    )
                )
            ),
            dbc.Collapse(
                vis_cards,
                id=f'{title}_vis_collapse'
            )
        ])
        return card

    def make_interaction_summary_card(self, title: str, options: List): 
        card = dbc.Card([
            dbc.CardHeader(
                html.H2(
                    dbc.Button(
                        f"{title}",
                        color="link",
                        id=f"{title}_toggle",
                    )
                )
            ),
            dbc.Collapse(
                dbc.FormGroup([
                    dbc.Checklist(
                        options=options,
                        value=[],
                        id=f"{title}_options",
                        labelStyle={'disabled': True}
                    ),
                ]),
                id=f'{title}_collapse'
            )
        ])
        return card

    def make_interaction_vis(self, title: str, interaction: Tuple[AbstractVariable, ...]): 
        # Create vis 
        fig = None
        if len(interaction) == 2: 
            fig = self.create_two_way_interaction_chart(interaction, self.design.dv, self.design.dataset.dataset)
        elif len(interaction) == 3: 
            fig = self.create_three_way_interaction_chart(interaction, self.design.dv, self.design.dataset.dataset)
        else: 
            pass
            # fig = None

        # Add it to cards 
        names = [v.name for v in interaction]
        interaction_name = '*'.join(names)
        card = dbc.Card([
            dbc.CardHeader([dbc.Checklist(options=[{'label': f'{interaction_name}', 'value': f'{interaction_name}'}], id={'type': 'interaction_effects_options', 'index': f'{interaction_name}'}, value=[])]),
            dbc.CardBody([
                fig
            ])
        ])

        return card

    def make_random_slope_card(self, variables: str, value: str):
        var_names = variables.split(',')
        base = var_names[0]
        group = var_names[1]
        card = dbc.Card([
            dbc.CardHeader([dbc.Checklist(options=[{'label': 'Random slope', 'value': f'{value}'}], id={'type': 'random_slope', 'index': f'{variables}'}, value=[])]),
            dbc.CardBody([
                html.P(f'Does each {base} within {group} differ in their impact on the dependent variable?'),
                # dbc.Checklist(options=[{'label': 'Include', 'value': f'{value}'}], id=f'{value}_slope')
            ])
        ])

        return card
    
    def make_random_intercept_card(self, variables: str, value: str):
        var_names = variables.split(',')
        base = var_names[0]
        group = var_names[1]
        card = dbc.Card([
            dbc.CardHeader([dbc.Checklist(options=[{'label': 'Random intercept', 'value': f'{value}'}], id={'type': 'random_intercept', 'index': f'{variables}'}, value=[])]),
            dbc.CardBody([
                html.P(f'Does each {base} within {group} differ on average on the dependent variable?')
            ])
        ])

        return card

    def make_random_checklist(self, label: str, options: List): 
        checklist = dbc.FormGroup([
            dbc.Label(label),
            dbc.Checklist(
                options=[
                    {'label': 'Random slope', 'value': f'{options[0]}'},
                    {'label': 'Random intercept', 'value': f'{options[1]}'},
                    {'label': 'Correlated random slope & intercept', 'value': f'{options[2]}'}
                ],
                value=[],
                labelStyle={'display': 'inline-block'}
            )  
        ])
        return checklist
            # TODO: correlate should only be an option if both are selected

    # @returns True if this specification is for a valid model
    # otherwise returns string indicating which aspect is not specified
    # @param spec is a JSON object specifying a statistical model
    def check_model_specification(self, spec: str): 
        spec = json.loads(spec) # JSON -> dict
        
        ivs = list() 
        if 'main_effects' in spec: 
            ivs = spec['main_effects']
        if 'interaction_effects' in spec: 
            ivs += spec['interaction_effects']
        family = None
        if 'family' in spec: 
            family = spec['family']
        link = None
        if 'link' in spec: 
            link = spec['link'] 

        if len(ivs) > 0: 
            if family: 
                if link: 
                    return (True, None)
                else: 
                    return (False, 'link')
            else: 
                return (False, 'family')
        else: 
            return (False, 'independent variables')

    def shutdown(self):
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError('Not running with the Werkzeug Server')
        func()

    
    # @classmethod
    # def ask_inclusion_prompt(cls, subject: str) -> bool: 

    #     prompt = f'Would you like to include {subject}?'
    #     choices = f' Y or N: '

    #     while True: 
    #         ans = add_inclusion_prompt(prompt=prompt, choices=choices)
    #         if ans.upper() == 'Y': 
    #             return ans.upper()
    #         elif ans.upper() == 'N': 
    #             return ans.upper()
    #         else: 
    #             pass
    
    # @classmethod
    # def ask_inclusion(cls, subject: str) -> bool: 
    
    #     ans = cls.ask_inclusion_prompt(subject)

    #     if ans.upper() == 'Y':
    #         # TODO: write to a file here 
    #         return True
    #     elif ans.upper() == 'N': 
    #         return False
    #     else: 
    #         pass
    
    # # TODO: Format the interactions to be more readable
    # @classmethod 
    # def format_options(cls, options: List) -> List: 
    #     return options

    # @classmethod
    # def ask_multiple_choice_prompt(cls, options: List) -> Any: 
    #     prompt = f'These cannot be true simultaneously.'
    #     formatted_options = cls.format_options(options)
    #     choices = f' Pick index (starting at 0) to select option in: {formatted_options}: '
    #     while True: 
    #         idx = int(input(prompt + choices))
    #         # st.write()

    #         if idx in range(len(options)): 
    #             # only keep the constraint that is selected. 
    #             constraint = options[idx] 
    #             print(f'Ok, going to add {constraint} and remove the others.')
    #             return idx
    #         else:
    #             print(f'Pick a value in range')
    #             pass
    
    # @classmethod
    # def resolve_unsat(cls, facts: List, unsat_core: List) -> List: 
    #     idx = cls.ask_multiple_choice_prompt(options=unsat_core)
    
    #     return unsat_core[idx]

    # # TODO: Format options for specifying family of a distribution
    # @classmethod
    # def format_family(cls, options: List): 
    #     return options
    
    # @classmethod
    # def ask_family_prompt(cls, options: List, dv: AbstractVariable): 
    #     prompt = f'Which distribution best approximates your dependent variable {dv}?'
    #     formatted_options = cls.format_options(options)
    #     choices = f' Pick index (starting at 0) to select option in: {formatted_options}: '

    #     while True: 
    #         idx = int(input(prompt + choices))

    #         if idx in range(len(options)): 
    #             # only keep the constraint that is selected. 
    #             constraint = options[idx] 
    #             print(f'Ok, going to add {constraint} and remove the others.')
    #             return idx
    #         else:
    #             print(f'Pick a value in range')
    #             pass
    
    # @classmethod
    # def ask_family(cls, options: List, dv: AbstractVariable): 
    #     idx = cls.ask_family_prompt(options=options, dv=dv)

    #     return options[idx]

    # @classmethod
    # def ask_link_prompt(cls, options: List, dv: AbstractVariable): 
    #     prompt = f'W'


    # @classmethod
    # def ask_link(cls, options: List, dv: AbstractVariable): 
    #     idx = cls.ask_link_prompt(options=options, dv=dv)

    #     return options[idx]

    # # @classmethod
    # # def ask_change_default_prompt(cls, subject: str, default: str, options: List): 
    # #     prompt = f'The default {subject} is {default}. Would you like to change it to one of {options}?'

    # # @classmethod
    # # def ask_change_default(cls, subject: str, default: str, options: List): 
    # #     idx = cls.ask_change_default_prompt(subject=subject, default=default, options=options)
    # #     pass
    