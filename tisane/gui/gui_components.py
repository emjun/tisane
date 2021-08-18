import json
import os
import logging
from typing import Dict, List
from tisane.variable import AbstractVariable
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_core_components as dcc

log = logging.getLogger("")
log.setLevel(logging.ERROR)

def cardP(text):
    return html.H5(text, className="card-text")
def checklist(labelList):
    return dcc.Checklist(
        options=[{"label": g, "value": g} for g in labelList],
        labelStyle={'display': 'block'}
    )

class GUIComponents():
    def __init__(self, input_json: str):
        if os.path.exists(input_json):
            with open(input_json, "r") as f:
                self.data = json.loads(f.read())
                pass
            pass
        else:
            log.error("Cannot find input json file {}".format(input_json))
            exit(1)
        pass

    def getQuery(self):
        return self.data["input"]["query"]

    def getGeneratedMainEffects(self):
        return self.data["input"]["generated main effects"]
    def getGeneratedInteractionEffects(self):
        return self.data["input"]["generated interaction effects"]


    def getMainEffectsCard(self):
        return dbc.Card(
            dbc.CardBody(
                [
                    cardP("Generated Main Effects"),
                    checklist(self.getGeneratedMainEffects()),
                    dbc.Button("Continue", color="success", id="continue-to-interaction-effects", n_clicks=0)
                ]
            ),
            className="mt-3"
        )

    def getInteractionEffectsCard(self):
        interactions = self.getGeneratedInteractionEffects()
        continueButton = dbc.Button("Continue", color="success", id="continue-to-random-effects", n_clicks=0)
        if not interactions:
            # interactions is empty
            return dbc.Card(
                dbc.CardBody(
                    [
                        cardP(html.I("No interaction effects")),
                        continueButton
                    ]
                ),
                className="mt-3"
            )
        return dbc.Card(
            dbc.CardBody(
                [
                    cardP("Interactions"),
                    checklist(self.getGeneratedInteractionEffects()),
                    continueButton
                ]
            ),
            className="mt-3"
        )

    def layout_main_effects_div(self, main_effects: Dict[str, List[AbstractVariable]]):
        ##### Collect all elements
        # Create main effects title
        main_title = html.Div(
            [
                dcc.Markdown(
                    """
            ### Independent Variables
            #### Do you want to want to add or remove independent variables?
            *Based on the relationships you specified earlier, the following variables directly impact the dependent variable.*
            """
                )
                # html.H3('Independent variables'),
                # html.H6('You already specified a few independent variables. Do you want to add any more?'),
                # dbc.Alert(
                #     '', className="mb-0",
                #     id="main_alert",
                #     dismissable=True,
                #     fade=True,
                #     is_open=True
                # )
            ]
        )

        # Get form groups for each set of main effects options
        input_fg, derived_direct_fg, derived_transitive_fg = self.populate_main_effects(
            main_effects
        )

        # Create main effects switch
        main_switch = self.create_switch(
            switch_id="main_effects_switch", form_group_id="main_effects_group"
        )

        ##### Combine all elements
        # Create div
        labels = list()
        fg_combo = list()
        if len(input_fg.children[0].options) > 0:
            labels.append(
                dbc.Col(
                    self.create_label_tooltip(
                        "Specified",
                        "End-user has already specified these variables as independent variables.",
                    ),
                    width=2,
                )
            )
            fg_combo.append(dbc.Col(input_fg, width=2))
        if len(derived_direct_fg.children[0].options) > 0:
            labels.append(
                dbc.Col(
                    self.create_label_tooltip(
                        "Derived directly",
                        "These are indepepdent variables that also cause or are associated with the dependent variable but were not specified.",
                    ),
                    width=2,
                )
            )
            fg_combo.append(dbc.Col(derived_direct_fg, width=2))
        if len(derived_transitive_fg.children[0].options) > 0:
            labels.append(
                dbc.Col(
                    self.create_label_tooltip(
                        "Derived transitively",
                        "These are independent variables that may underlie independent variables that are already specified.",
                    ),
                    width=2,
                )
            )
            fg_combo.append(dbc.Col(derived_transitive_fg, width=2))

        main_effects_div = html.Div(
            [main_title, dbc.Row(labels), dbc.Row(fg_combo), main_switch]
        )

        ##### Return div
        return main_effects_div
