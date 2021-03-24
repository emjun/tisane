from tisane.variable import AbstractVariable
from tisane.design import Design
from tisane.statistical_model import StatisticalModel
from tisane.smt.synthesizer import Synthesizer
from tisane.helpers import *

from typing import List, Any
import subprocess
from subprocess import DEVNULL
import os
import sys

import pandas as pd
import plotly.figure_factory as ff
import plotly.express as px
import dash
import dash_daq as daq
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go
import webbrowser # For autoamtically opening the browser for the CLI

external_stylesheets = [dbc.themes.BOOTSTRAP]
port = '8050' # default dash port
def open_browser():
	webbrowser.open_new("http://localhost:{}".format(port))

__value_to_z3__ = dict() # Global map between vals and z3 facts
        
class InputInterface(object): 
    design: Design 
    statistical_model: StatisticalModel
    app: dash.Dash

    def __init__(self, design: Design, synthesizer: Synthesizer):
        self.design = design
        self.synthesizer = synthesizer
        
        app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

        main_heading = html.H1(children='Main Effects')
        main_effects = self.populate_main_effects()
        main_switch = dbc.FormGroup([
                dbc.Checklist(
                    options=[
                        {"label": "Save and lock main effects", "value": False}
                    ],
                    value=[],
                    id='main_effects_switch',
                    switch=True,
                ),
            ],
            id='main_effects_group'
        )

        interaction_heading = html.H1(children='Interaction Effects')
        interaction_effects = self.populate_interaction_effects()
        interaction_switch = dbc.FormGroup([
                dbc.Checklist(
                    options=[
                        {"label": "Save and lock interaction effects", "value": False}
                    ],
                    value=[],
                    id='interaction_effects_switch',
                    switch=True,
                ),
            ],
            id='interaction_effects_group'
        )

        random_heading = html.H1(children='Random Effects')
        random_effects = self.populate_random_effects()
        random_switch = dbc.FormGroup([
                dbc.Checklist(
                    options=[
                        {"label": "Save and lock random effects", "value": False}
                    ],
                    value=[],
                    id='random_effects_switch',
                    switch=True,
                ),
            ],
            id='random_effects_group'
        )

        family_heading = html.H1(children='Family Distribution')
        family_link_controls = self.make_family_link_options()
        link_chart = self.draw_data_dist()
        link_div = self.populate_link_div()

        
        # TODO: Layout Main | Interaction in a visually appealing way
        
        # Create Dash App
        app.layout = dbc.Container([
            # html.Div([main_heading, main_switch]),
            main_heading, 
            main_switch,
            main_effects,
            # html.Div([interaction_heading, interaction_switch]),
            interaction_heading,
            interaction_switch,
            interaction_effects,
            random_heading,
            random_switch,
            random_effects,
            family_heading, 
            link_chart,
            family_link_controls
        ])
        
        @app.callback(
            Output('main_effects_options', 'options'),
            [Input('main_effects_switch', 'value'),
            State('main_effects_options', 'options')],
            # State('main_effects_options', 'options')
        )
        def save_main_effects(switch_value, main_effects_options):
            output = list()
            if switch_value: 
                facts = list()
                for o in main_effects_options: 
                    facts.append(o['value'])
                    output.append({'label': o['label'], 'value': o['value'], 'disabled': True})
                    
                is_sat = self.synthesizer.check_constraints(facts, rule_set='effects', design=self.design)
                if is_sat: 
                    self.synthesizer.update_with_facts(facts, rule_set='effects', design=self.design)
                    return output
                else: 
                    # TODO: Start a modal?
                    raise ValueError(f"Error in saving main effects!")
            else: 
                for o in main_effects_options: 
                    output.append({'label': o['label'], 'value': o['value'], 'disabled': False})
                
                return output
        
        @app.callback(
            Output('two-way_options', 'labelStyle'),
            Output('n-way_options', 'labelStyle'),
            [Input('interaction_effects_switch', 'value'),
            Input('two-way_options', 'options'),
            Input('n-way_options', 'options')]
        )
        def save_interaction_effects(two_way_options, n_way_options, switch_val):
            if switch_val == 'save': 
                facts = list()

                for o in two_way_options: 
                    facts.append(two_way_options['value'])
                
                for o in n_way_options: 
                    facts.append(two_way_options['value'])
                
                is_sat = self.synthesizer.check_constraints(facts, rule_set='effects', design=self.design)
                # return html.Div(f"{is_sat}")
                if is_sat: 
                    self.synthesizer.update_with_facts(facts, rule_set='effects', design=self.design)
                    # TODO: Lock the interaction effects options
                    return {'disabled': True}
                else: 
                    # TODO: Start a modal?
                    raise ValueError(f"Error in saving main effects!")
            else: 
                raise PreventUpdate
                
        @app.callback(
            [Output(f"{i}_collapse", "is_open") for i in ['two-way', 'n-way']],
            [Input(f"{i}_toggle", "n_clicks") for i in ['two-way', 'n-way']],
            [State(f"{i}_collapse", "is_open") for i in ['two-way', 'n-way']],
        )
        def toggle_accordion(n1, n2, is_open1, is_open2):
            ctx = dash.callback_context

            if not ctx.triggered:
                return False, False
            else:
                button_id = ctx.triggered[0]["prop_id"].split(".")[0]

            if button_id == "two-way_toggle" and n1:
                return not is_open1, False
            elif button_id == "n-way_toggle" and n2:
                return False, not is_open2
            return False, False

        @app.callback(
            Output('link_choice', 'options'),
            [
                Input('family_choice', 'value'),
                Input('link_choice', 'options'),
            ],
        )
        def update_link_options(family, old_options): 
            global __value_to_z3__
            
            new_options = list()

            if family is not None: 
                # Get link options
                family_name = str(family)
                assert(family_name in __value_to_z3__.keys())
                family_fact = __value_to_z3__[family_name]
                link_options = self.get_link_options(family_fact)

                for link in link_options: 
                    __value_to_z3__[str(link)] = link
                    new_options.append({'label': str(link), 'value': str(link)})                    

                return new_options
            else: 
                raise PreventUpdate
            
        @app.callback(
            Output('data_dist', 'figure'),
            [
                Input('family_choice', 'value'),
                Input('link_choice', 'value')
            ],
            State('data_dist', 'figure')
        )
        def update_chart_family(family, link, old_data): 
            global __value_to_z3__
            
            if family is not None: 
                assert(isinstance(family, str))
                family_fact = __value_to_z3__[family]

                # Get current data 
                (curr_data, curr_label) = self.get_data_dist()

                # Get data for family
                key = f'{family}_data'
                
                # Do we need to generate data?
                if key not in __value_to_z3__.keys(): 
                    family_data = generate_data_dist_from_facts(fact=family_fact, design=self.design)
                    # Store data for family in __value_to_z3__ cache
                    __value_to_z3__[key] = family_data
                # We already have the data generated in our "cache"
                else: 
                    family_data = __value_to_z3__[key]

                if link is not None: 
                    assert(isinstance(link, str))
                    link_fact = __value_to_z3__[link]
                    # Transform the data 
                    transformed_data = transform_data_from_fact(data=family_data, link_fact=link_fact)

                    # Create a new dataframe
                    # Generate figure 
                    fig = go.Figure()
                    fig.add_trace(go.Histogram(x=curr_data, name=f'{self.design.dv.name}',))
                    fig.add_trace(go.Histogram(x=transformed_data, name=f'Simulated {family} distribution, {link} transformation.'))
                    fig.update_layout(barmode='overlay')
                    fig.update_traces(opacity=0.75)

                    return fig
                else: 
                    raise PreventUpdate
            else: 
                raise PreventUpdate
            
        open_browser()
        app.run_server(debug=False, threaded=True)
        
        self.app = app
    
    def populate_main_effects(self): 
        output = list()
        # Get possible main effects from synthesizer
        possible_main_effects = self.synthesizer.generate_main_effects(design=self.design)

        # TODO: We could lay them out in separate divs for query | Tisane recommended | not included.
        # Lay them out
        variable_options = list()
        for (variable, facts) in possible_main_effects.items(): 
            variable_options.append({'label': str(variable), 'value': f'{facts[0]}'})
        output = dbc.FormGroup([
            dbc.Checklist(
                options=variable_options,
                value=[],
                id="main_effects_options",
            ),
        ])

        return output

    def populate_interaction_effects(self): 
        global __value_to_z3__

        output = list()
        # Get possible main effects from synthesizer
        possible_interaction_effects = self.synthesizer.generate_interaction_effects(design=self.design)

        # TODO: We could lay them out in separate divs for query | Tisane recommended | not included.
        # Lay them out
        for (num_interactions, options) in possible_interaction_effects.items(): 
            interaction_options = list()
            for (name, fact) in options.items():
                __value_to_z3__[str(fact)] = fact
                interaction_options.append({'label': name, 'value': str(fact)})
            
            output.append(self.make_interaction_card(title=num_interactions, options=interaction_options))
            
        return html.Div(output, className='accordion')
    
    def populate_random_effects(self): 
        # Could be random slope OR random interaction 
        output = list()
        # Get possible main effects from synthesizer
        possible_random_effects = self.synthesizer.generate_random_effects(design=self.design)

        # TODO: We could lay them out in separate divs for query | Tisane recommended | not included.
        # Lay them out
        for (key, facts) in possible_random_effects.items(): 
            output.append(self.make_random_checklist(label=key, options=facts))
            
            # TODO: correlate should only be an option if both are selected

        # return output
        return html.Div(output)
    
    def get_data_dist(self): 
        dv = self.design.dv
        
        data = self.design.get_data(variable=dv)
        
        if data is not None: 
            hist_data = data
            labels = dv.name
        else: 
            raise NotImplementedError
        
        return (hist_data, labels)

    def draw_dist(self, hist_data, label): 
        data = pd.DataFrame(hist_data, columns=[label])

        fig = px.histogram(data, x=label)
        # fig = ff.create_distplot(hist_data, labels)

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
        global __value_to_z3__

        key = f'{str(family_fact)}_data'
        if key in __value_to_z3__.keys(): 
            return __value_to_z3__[key]
        else: 
            val = generate_data_dist_from_facts(fact=family_fact, design=self.design)
            __value_to_z3__[key] = val
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

    def update_data_with_link(self): 
        pass

    def get_link_options(self, family_fact: z3.BoolRef): 
         
        link_functions = self.synthesizer.generate_link_functions(design=self.design, family_fact=family_fact)

        return link_functions
    
    def make_family_options(self): 
        global __value_to_z3__ 

        options = list()

        dist_names = self.synthesizer.generate_family_distributions(design=self.design)

        for d in dist_names: 
            __value_to_z3__[str(d)] = d
            options.append({'label': str(d), 'value': str(d)})
        
        return options

    def make_family_link_options(self): 
        family_options = self.make_family_options()

        controls = dbc.Card(
            [
                dbc.FormGroup(
                    [
                        dbc.Label('Family'),
                        dcc.Dropdown(
                            id='family_choice',
                            options=family_options,
                            value=None,
                        ),
                    ]
                ),
                dbc.FormGroup(
                    [
                        dbc.Label('Link function'),
                        dcc.Dropdown(
                            id='link_choice',
                            options=[],
                            value=None,
                        ),
                    ]
                )
            ],
            body=True,
        )

        return controls

    def make_interaction_card(self, title: str, options: List): 
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