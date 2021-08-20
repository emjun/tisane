import json
import os
import logging
from typing import Dict, List
from tisane.variable import AbstractVariable
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import plotly.express as px
import plotly.graph_objects as go

log = logging.getLogger("")
log.setLevel(logging.ERROR)

def cardP(text):
    return html.H5(text, className="card-text")
def checklist(labelList, id):
    return dcc.Checklist(
        options=[{"label": "{}".format(g), "value": g} for g in labelList],
        labelStyle={'display': 'block'},
        id=id
    )
def separateByUpperCamelCase(mystr):
    start = -1
    words = []
    for i in range(len(mystr)):
        part = mystr[i]
        if part.lower() != part:
            # upper case
            if start >= 0:
                words.append(mystr[start:i])
                pass
            start = i
        elif i == len(mystr) - 1 and start != i:
            # we're at the end
            words.append(mystr[start:i + 1])
    return words

class GUIComponents():
    def __init__(self, input_json: str):
        self.numGeneratedComponentIds = 0
        self.generatedComponentIdToRandomEffect = {}
        self.generatedComponentIdToMainEffect = {}
        self.generatedComponentIdToInteractionEffect = {}
        self.variables = {
            "main effects": {},
            "interaction effects": {}
        }
        if os.path.exists(input_json):
            with open(input_json, "r") as f:
                self.data = json.loads(f.read())
                pass
            pass
        else:
            log.error("Cannot find input json file {}".format(input_json))
            exit(1)
            pass
        for me in self.getGeneratedMainEffects():
            self.variables["main effects"][me] = {
                "info-id": self.getNewComponentId()
            }
            pass
        for ie in self.getGeneratedInteractionEffects():
            self.variables["interaction effects"][ie] = {
                "info-id": self.getNewComponentId()
            }
            pass
        pass

    def hasEffectForComponentId(self, componentId, effectDict):
        return componentId in effectDict

    def hasMainEffectForComponentId(self, componentId):
        return self.hasEffectForComponentId(componentId, self.generatedComponentIdToMainEffect)

    def hasInteractionEffectForComponentId(self, componentId):
        return self.hasEffectForComponentId(componentId, self.generatedComponentIdToInteractionEffect)

    def getRandomEffectCheckboxIds(self):
        return list(self.generatedComponentIdToRandomEffect.keys())

    def getMainEffectCheckboxIds(self):
        return list(self.generatedComponentIdToMainEffect.keys())

    def getInteractionEffectCheckboxIds(self):
        return list(self.generatedComponentIdToInteractionEffect.keys())

    def hasRandomEffectForComponentId(self, componentId):
        return componentId in self.generatedComponentIdToRandomEffect

    def getEffectFromComponentId(self, componentId, effectDict):
        assert componentId in effectDict, "Component id {} does not exist in {}".format(componentId, effectDict)
        return effectDict[componentId]

    def getMainEffectFromComponentId(self, componentId):
        return self.getEffectFromComponentId(componentId, self.generatedComponentIdToMainEffect)

    def getInteractionEffectFromComponentId(self, componentId):
        return self.getEffectFromComponentId(componentId, self.generatedComponentIdToInteractionEffect)

    def getRandomEffectFromComponentId(self, componentId):
        assert componentId in self.generatedComponentIdToRandomEffect, "Component id {} does not exist in {}".format(componentId, self.generatedComponentIdToRandomEffect)
        return self.generatedComponentIdToRandomEffect[componentId]

    def getNewComponentId(self):
        self.numGeneratedComponentIds += 1
        return "gui-components-unique-id-{}".format(self.numGeneratedComponentIds)

    def hasComponentIdForEffect(self, effect: str, effectsDict):
        assert effect in effectsDict, "Group {} not found in effects: {}".format(effect, effectsDict)
        return "component-id" in effectsDict[effect]

    def hasComponentIdForMainEffect(self, mainEffect: str):
        return self.hasComponentIdForEffect(mainEffect, self.variables["main effects"])

    def hasComponentIdForInteractionEffect(self, interactionEffect: str):
        return self.hasComponentIdForEffect(interactionEffect, self.variables["interaciton effects"])

    def setComponentIdForEffect(self, effect, effectsDict, componentIdToEffect):
        assert effect in effectsDict, "{} not found in effects dict {}".format(effect, effectsDict)
        if not self.hasComponentIdForEffect(effect, effectsDict):
            newId = self.getNewComponentId()
            componentIdToEffect[newId] = effect
            effectsDict[effect]["component-id"] = newId
            return newId
        return effectsDict[effect]["component-id"]

    def setComponentIdForMainEffect(self, mainEffect):
        return self.setComponentIdForEffect(mainEffect, self.variables["main effects"], self.generatedComponentIdToMainEffect)

    def setComponentIdForInteractionEffect(self, interactionEffect):
        return self.setComponentIdForEffect(interactionEffect, self.variables["interaction effects"], self.generatedComponentIdToInteractionEffect)

    def hasComponentIdForRandomEffect(self, randomEffectGroup: str):
        randomEffects = self.getGeneratedRandomEffects()
        assert randomEffectGroup in self.getGeneratedRandomEffects(), "Group {} not found in generated random effects: {}".format(randomEffectGroup, randomEffects)
        return "component-id" in randomEffects[randomEffectGroup]

    def setComponentIdForRandomEffect(self, randomEffectGroup: str):
        randomEffects = self.getGeneratedRandomEffects()
        assert randomEffectGroup in randomEffects, "Group {} not found in generated random effects: {}".format(randomEffectGroup, randomEffects)
        if not self.hasComponentIdForRandomEffect(randomEffectGroup):
            newId = self.getNewComponentId()
            self.generatedComponentIdToRandomEffect[newId] = randomEffectGroup
            randomEffects[randomEffectGroup]["component-id"] = newId
            return newId
        return randomEffects[randomEffectGroup]["component-id"]


    def getQuery(self):
        return self.data["input"]["query"]

    def getDependentVariable(self):
        return self.getQuery()["DV"]

    def getGeneratedMainEffects(self):
        return self.data["input"]["generated main effects"]
    def getGeneratedInteractionEffects(self):
        return self.data["input"]["generated interaction effects"]
    def getGeneratedRandomEffects(self):
        return self.data["input"]["generated random effects"]
    def getGeneratedFamilyLinkFunctions(self):
        return self.data["input"]["generated family, link functions"]

    def getInteractionEffectsAddedSection(self):
        if self.hasInteractionEffects():
            return [
                html.H6("Interaction effects added:"),
                html.Ul(id="added-interaction-effects"),
            ]
        return [
            html.H6(html.I("No interaction effects to add"), id="added-interaction-effects")
        ]
    def getRandomEffectsAddedSection(self):
        if self.hasRandomEffects():
            return [
                html.H6("Random effects added:"),
                html.Ul(id="added-random-effects"),
            ]
        return [html.H6(html.I("No random effects to add"), id="added-random-effects")]

    def hasRandomEffects(self):
        if self.getGeneratedRandomEffects():
            return True
        return False

    def hasInteractionEffects(self):
        if self.getGeneratedInteractionEffects():
            return True
        return False
    def getMainEffectsCard(self):
        return dbc.Card(
            dbc.CardBody(
                [
                    cardP("Generated Main Effects"),
                    # checklist(self.getGeneratedMainEffects(), "main-effects-checklist"),
                    self.layoutFancyChecklist({me: html.Span([me + " ", html.I(className="bi bi-info-circle", id=self.variables["main effects"][me]["info-id"])]) for me in self.getGeneratedMainEffects()}, self.setComponentIdForMainEffect),
                    html.P(""),
                    dbc.Button("Continue", color="success", id="continue-to-interaction-effects", n_clicks=0),
                    # html.Div( [dbc.FormGroup(
                    #     [
                    #         dbc.Checkbox(
                    #             id="standalone-checkbox", className="form-check-input"
                    #         ),
                    #         dbc.Label(
                    #             "This is a checkbox",
                    #             html_for="standalone-checkbox",
                    #             className="form-check-label",
                    #         ),
                    #     ],
                    #     check=True,
                    # ),
                    # dbc.FormGroup(
                    #     [
                    #         dbc.Checkbox(
                    #             id="standalone-checkbox-1", className="form-check-input"
                    #         ),
                    #         dbc.Label(
                    #             "This is a checkbox",
                    #             html_for="standalone-checkbox-1",
                    #             className="form-check-label",
                    #         ),
                    #     ],
                    #     check=True,
                    # ),],
                    #          id="test-div"),
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
                    # checklist(self.getGeneratedInteractionEffects(), "interaction-effects-checklist"),
                    self.layoutFancyChecklist({me: html.Span([me + " ", html.I(className="bi bi-info-circle", id=self.variables["interaction effects"][me]["info-id"])]) for me in self.getGeneratedInteractionEffects()}, self.setComponentIdForInteractionEffect),
                    html.P(""),
                    continueButton
                ]
            ),
            className="mt-3"
        )

    def layoutFancyChecklist(self, labelDict, componentIdSetter):
        options = []
        for name, label in labelDict.items():
            options.append(dbc.FormGroup(
                [
                    dbc.Checkbox(id=componentIdSetter(name),
                                 className="form-check-input"),
                    dbc.Label(label,
                              html_for=componentIdSetter(name),
                              className="form-check-label"),
                ],
                check=True,
            ))
            pass
        return html.Div(options)
    def layoutGeneratedRandomEffects(self):
        def layoutRandomEffect(group, randomEffectDict):
            ri = "random intercept"
            rs = "random slope"
            cor = "correlated"



            def wrapper(elt):
                return dbc.Row(dbc.Col(elt))
            randomInterceptPortion = [dbc.Badge("Random Intercept", color="danger", className="mr-1")] if ri in randomEffectDict else []
            randomSlopePortion = [html.Span([html.Span(randomEffectDict[rs]["iv"]), dbc.Badge("Random Slope", color="info", className="mr-1")])] if rs in randomEffectDict else []
            corPortion = [dbc.Checklist(options=[{"label": "correlated", "value":"correlated"}], value=["correlated"])] if cor in randomEffectDict else []
            contents = randomInterceptPortion + randomSlopePortion + corPortion
            contents = [wrapper(c) for c in contents]
            return html.Div([wrapper(group)] + contents)
        randomEffects = self.getGeneratedRandomEffects()
        options = [dbc.FormGroup([
            dbc.Checkbox(id=self.setComponentIdForRandomEffect(group), className="form-check-input"),
            dbc.Label(layoutRandomEffect(group, randomEffectDict), html_for=self.setComponentIdForRandomEffect(group), className="form-check-label")
        ], check=True
        ) for group, randomEffectDict in randomEffects.items()]
        return html.Div(options)

    def getRandomEffectsCard(self):
        randomeffects = self.getGeneratedRandomEffects()
        continueButton = dbc.Button("Continue", color="success", id="continue-to-family-link-functions", n_clicks=0)
        if not randomeffects:
            return dbc.Card(
                dbc.CardBody([
                    cardP(html.I("No random effects")),
                    continueButton
                ])
            )
        return dbc.Card(
            dbc.CardBody(
                [
                    cardP("Random Effects"),
                    self.layoutGeneratedRandomEffects(),
                    html.P(""),
                    continueButton
                ]
            ),
            className="mt-3",)
    def get_data_dist(self):
        hist_data = None
        labels = None

        dv = self.getDependentVariable()

        data = self.design.get_data(variable=dv)

        if data is not None:
            hist_data = data
            labels = dv.name

        return (hist_data, labels)

    def make_family_link_options(self):
        global __str_to_z3__

        family_options = list()
        # link_options =

        for f in self.getGeneratedFamilyLinkFunctions():
            label = " ".join(separateByUpperCamelCase(f)[:-1])
            # if label == "InverseGaussian":
            #     label = "Inverse Gaussian"  # add a space

            family_options.append({"label": label, "value": f})
            pass

        controls = dbc.Card(
            [
                dbc.FormGroup(
                    [
                        dbc.Label("Family"),
                        dcc.Dropdown(
                            # id={'type': 'family_link_options', 'index': 'family_options'},
                            id="family-options",
                            options=family_options,
                            value=None,
                        ),
                    ]
                ),
                dbc.FormGroup(
                    [
                        dbc.Label("Link function"),
                        dcc.Dropdown(
                            # id={'type': 'family_link_options', 'index': 'link_options'},
                            id="link-options",
                            options=[],
                            value=None,
                        ),
                    ]
                ),
            ],
            body=True,
            id={"type": "family_link_options", "index": "family_link_options"},
        )

        return controls

    def draw_dist(self, hist_data, label):
        # Make sure that there is data to draw
        # Hist_data is not None and labels is not None
        if hist_data is not None and label is not None:
            data = pd.DataFrame(hist_data, columns=[label])

            fig = px.histogram(data, x=label)
            fig.update_layout(
                legend=dict(
                    orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
                )
            )

            fig_elt = dcc.Graph(id="data_dist", figure=fig)
        else:
            fig = go.Figure()
            fig.add_trace(
                go.Scatter(
                    x=[-1, 3, 5, 10, 12],
                    y=[10, 8, 5, 4, 0],
                    mode="markers+text",
                    # name="Markers and Text",
                    text=[
                        "",
                        "No data supplied!",
                        "Imagine how your data will look when you collect it...",
                        "...by looking at possible distributions  -->. :]",
                        "",
                    ],
                    textposition="bottom center",
                )
            )

            fig_elt = dcc.Graph(id="data_dist", figure=fig)

        return fig_elt

    def draw_data_dist(self):
        (hist_data, labels) = self.get_data_dist()

        return self.draw_dist(hist_data, labels)
    def getFamilyLinkFunctionsCard(self):
        ##### Collect all elements
        # Create family and link title
        family_link_title = html.Div(
            [
                dcc.Markdown(
                    """
            ### Data distributions: Family and Link functions.
            #### Which distribution best matches your data?
            """
                )
                # html.H3('Family and Link: Data distributions'),
                # dbc.Alert(
                #     "TODO: Explanation of family and link functions", className="mb-0",
                #     id='family_link_alert',
                #     dismissable=True,
                #     fade=True,
                #     is_open=True
                # )
            ]
        )

        # Get form groups for family link div
        family_link_chart = html.Div("Chart goes here") #self.draw_data_dist()
        family_link_controls = self.make_family_link_options()

        # Create main effects switch
        # family_link_switch = self.create_switch(
        #     switch_id="family_link_switch", form_group_id="family_link_group"
        # )

        ##### Combine all elements
        # Create div
        family_and_link_div = dbc.Card(
            dbc.CardBody(
            [
                family_link_title,
                dbc.Row(
                    [
                        dbc.Col(family_link_chart, md=7),
                        dbc.Col(family_link_controls, md=5),
                    ],
                    align="center",
                ),
                # family_link_switch,
                dbc.Button("Generate Code", color="success", id="generate-code"),
            ]),
            className="mt-3"
        )

        ##### Return div
        return family_and_link_div
