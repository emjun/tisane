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

from tisane.gui.gui_helpers import simulate_data_dist

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

def getInfoBubble(id: str):
    return html.I(className="bi bi-info-circle", id=id)

class GUIComponents():
    def __init__(self, input_json: str):
        self.numGeneratedComponentIds = 0
        self.generatedComponentIdToRandomEffect = {}
        self.generatedComponentIdToMainEffect = {}
        self.generatedComponentIdToInteractionEffect = {}
        self.simulatedData = {}
        self.defaultLinkForFamily = {
            "GaussianFamily": "IdentityLink",
            "BinomialFamily": "LogitLink",
            "PoissonFamily": "LogLink",
            "TweedieFamily": "LogLink",
            "GammaFamily": "InverseLink",
            "NegativeBinomialFamily": "LogLink",
            "InverseGaussianFamily": "InverseSquaredLink"
        }
        self.output = {
            "main effects": [],
            "dependent variable": "",
            "interaction effects": [],
            "random effects": {},
            "family": "GaussianFamily",
            "link": "IdentityLink"
        }
        self.variables = {
            "main effects": {},
            "interaction effects": {}
        }
        self.rowIdsByUnit = {}
        self.unitsByAddedRandomVariableId = {}
        self.unitsByRowId = {}
        self.randomSlopes = {}
        self.generatedCorrelatedIdToRandomSlope = {}
        if os.path.exists(input_json):
            with open(input_json, "r") as f:
                self.data = json.loads(f.read())
                pass
            pass
        else:
            log.error("Cannot find input json file {}".format(input_json))
            exit(1)
            pass
        query = self.getQuery()
        self.output["dependent variable"] = query["DV"]
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
        randomEffects = self.getGeneratedRandomEffects()
        for unit, re in randomEffects.items():
            self.output["random effects"][unit] = {}
            if "random intercept" in re:
                self.output["random effects"][unit]["random intercept"] = re["random intercept"]
                pass
            if "random slope" in re:
                self.output["random effects"][unit]["random slope"] = re["random slope"]
                if "correlated" in re and re["correlated"]:
                    for slope in self.output["random effects"][unit]["random slope"]:
                        slope["correlated"] = True
        self.generatedCorrelatedIdToGroupIv = {}
        self.randomIntercepts = {}
        for unit, re in randomEffects.items():
            if "random intercept" in re:
                infoId = self.getNewComponentId()
                self.randomIntercepts[unit] = {
                    "info-id": infoId
                }
                pass
            if "random slope" in re and "random intercept" in re:
                if unit not in self.randomSlopes:
                    self.randomSlopes[unit] = {}
                    pass
                for rs in re["random slope"]:
                    newId = self.getNewComponentId()
                    infoId = self.getNewComponentId()
                    self.randomSlopes[unit][rs["iv"]] = {
                        "correlated-id": newId,
                        "info-id": infoId,
                    }
                    self.generatedCorrelatedIdToRandomSlope[newId] = rs
                    self.generatedCorrelatedIdToGroupIv[newId] = (unit, rs["iv"])
                    pass
                pass
            elif "random slope" in re:
                if unit not in self.randomSlopes:
                    self.randomSlopes[unit] = {}
                    pass
                for rs in re["random slope"]:
                    infoId = self.getNewComponentId()
                    self.randomSlopes[unit][rs["iv"]] = {
                        "info-id": infoId
                    }
            pass
        print(self.randomSlopes)
        pass

    def getMeasuresToUnits(self):
        return self.data["input"]["measures to units"]

    def hasUnitForMeasure(self, measure):
        return measure in self.getMeasuresToUnits()

    def getUnitFromMeasure(self, measure):
        measuresToUnits = self.getMeasuresToUnits()
        assert measure in measuresToUnits, "Measure {} not in measuresToUnits {}".format(measure, measuresToUnits)
        return measuresToUnits[measure]

    def getUnitFromRowId(self, rowId):
        assert rowId in self.unitsByRowId
        return self.unitsByRowId[rowId]

    def getUnitFromRowOrAddedRandomVariableId(self, id):
        assert id in self.unitsByRowId or id in self.unitsByAddedRandomVariableId, "Id {} in neither {} nor {}".format(id, self.unitsByRowId, self.unitsByAddedRandomVariableId)
        if id in self.unitsByRowId:
            return self.getUnitFromRowId(id)
        return self.getUnitFromAddedRandomVariableId(id)

    def getUnitFromAddedRandomVariableId(self, addedRandomVariableId):
        return self.unitsByAddedRandomVariableId[addedRandomVariableId]

    def getAddedRandomVariableIds(self):
        return sorted(list(self.unitsByAddedRandomVariableId.keys()))

    def getRandomEffectsRowIds(self):
        return sorted(list(self.unitsByRowId.keys()))

    def getExplanations(self):
        return self.data["input"]["explanations"]

    def getDefaultLinkForFamily(self, family):
        if family in self.defaultLinkForFamily:
            return self.defaultLinkForFamily[family]
        return None

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

    def getGroupFromMeasure(self, measure):
        if measure in self.data["input"]["measures to units"]:
            return self.data["input"]["measures to units"][measure]
        return ""

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

    def getRandomSlopeFromComponentId(self, componentId):
        assert componentId in self.generatedCorrelatedIdToRandomSlope, "Component id {} does not exist in {}".format(componentId, self.generatedCorrelatedIdToRandomSlope)
        return self.generatedCorrelatedIdToRandomSlope[componentId]

    def markCheckedForCorrelatedId(self, correlatedId, checked: bool):
        if self.hasGroupAndIvForCorrelatedId(correlatedId):
            group, iv = self.getGroupAndIvFromCorrelatedId(correlatedId)
            assert group in self.output["random effects"] and "random slope" in self.output["random effects"][group]
            for slope in self.output["random effects"][group]["random slope"]:
                if slope["iv"] == iv and "correlated" in slope:
                    slope["correlated"] = checked
                    pass
                pass
            pass
        pass


    def hasGroupAndIvForCorrelatedId(self, componentId):
        return componentId in self.generatedCorrelatedIdToGroupIv
    def getGroupAndIvFromCorrelatedId(self, componentId):
        assert componentId in self.generatedCorrelatedIdToGroupIv, "Component id {} does not exist in {}".format(componentId, self.generatedCorrelatedIdToGroupIv)
        return self.generatedCorrelatedIdToGroupIv[componentId]
    def hasRandomSlopeForComponentId(self, componentId):
        return componentId in self.generatedCorrelatedIdToRandomSlope

    def hasCorrelatedIdForRandomSlope(self, group, iv):
        return group in self.randomSlopes and iv in self.randomSlopes[group] and "correlated-id" in self.randomSlopes[group][iv]
    def getCorrelatedIdForRandomSlope(self, group, iv):
        assert self.hasCorrelatedIdForRandomSlope(group, iv)
        return self.randomSlopes[group][iv]["correlated-id"]

    def getRandomSlopeCheckboxIds(self):
        return list(self.generatedCorrelatedIdToRandomSlope.keys())

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
    def getIndependentVariables(self):
        return self.getQuery()["IVs"]

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
            randomEffects = self.getGeneratedRandomEffects()
            info = []
            for group, randomEffect in randomEffects.items():
                titleId = self.getNewComponentId()
                info.append(html.H6(group + (" (with random intercept)" if "random intercept" in randomEffect else ""), id=titleId))
                self.unitsByAddedRandomVariableId[titleId] = group
                if "random slope" in randomEffect:
                    randomSlopes = []
                    for rs in randomEffect["random slope"]:
                        iv = rs["iv"]
                        listItemId = self.getNewComponentId()
                        self.unitsByAddedRandomVariableId[listItemId] = group
                        randomSlopes.append(
                            html.Li([
                                iv
                            ] + (
                                [
                                    html.Span(" (correlated)", id=self.getCorrelatedIdForRandomSlope(group, iv) + "-span")
                                ] if "correlated" in randomEffect else []
                            ),
                            id=listItemId
                        ))
                        pass
                    if randomEffect["random slope"]:
                        info.append(html.Span("Random slopes:"))
                        info.append(html.Ul(randomSlopes))

            return [
                html.H5("Random effects:"),
                html.Ul(id="added-random-effects"),
                html.Div(info)
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
        ivs = self.getIndependentVariables()
        return dbc.Card(
            dbc.CardBody(
                [
                    cardP("Generated Main Effects"),
                    self.layoutFancyChecklist({me: html.Span([me + " ", getInfoBubble(self.variables["main effects"][me]["info-id"])]) for me in self.getGeneratedMainEffects()}, self.setComponentIdForMainEffect,
                                              {me: me in ivs for me in self.getGeneratedMainEffects()}),
                    html.P(""),
                    dbc.Button("Continue", color="success", id="continue-to-interaction-effects", n_clicks=0),
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
                        html.P("Placeholder text for where an explanation would go"),
                        continueButton
                    ]
                ),
                className="mt-3"
            )
        return dbc.Card(
            dbc.CardBody(
                [
                    cardP("Interactions"),
                    self.layoutFancyChecklist({me: html.Span([me + " ", html.I(className="bi bi-info-circle", id=self.variables["interaction effects"][me]["info-id"])]) for me in self.getGeneratedInteractionEffects()}, self.setComponentIdForInteractionEffect, {ie: False for ie in interactions}),
                    html.P(""),
                    continueButton
                ]
            ),
            className="mt-3"
        )

    def layoutFancyChecklist(self, labelDict, componentIdSetter, checkedDict):
        options = []
        for name, label in labelDict.items():
            options.append(dbc.FormGroup(
                [
                    dbc.Checkbox(id=componentIdSetter(name),
                                 className="form-check-input",
                                 checked=checkedDict[name]),
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
                return html.Li(elt)
            randomInterceptPortion = [dbc.Badge("Random Intercept", color="danger", className="mr-1")] if ri in randomEffectDict else []
            randomSlopePortion = []
            if rs in randomEffectDict:
                for randomSlope in randomEffectDict[rs]:
                    iv = randomSlope["iv"]
                    checker = []
                    if cor in randomEffectDict:
                        print("Adding checkbox")
                        checker = [html.Ul(html.Li(dbc.Checklist(options=[{"label": "correlated", "value": "correlated"}], value=["correlated"], id=self.getCorrelatedIdForRandomSlope(group, iv))))]
                        pass
                    randomSlopePortion.append([html.Span(iv), dbc.Badge("Random Slope", color="info", className="mr-1")
                    ] + checker)
            contents = randomInterceptPortion + randomSlopePortion #+ corPortion
            contents = [wrapper(c) for c in contents]
            return html.Div([html.H6(group), html.Ul(contents)])
        randomEffects = self.getGeneratedRandomEffects()
        options = [layoutRandomEffect(group, randomEffectDict) for group, randomEffectDict in randomEffects.items()]
        return html.Div(options)

    def layoutRandomEffectsTable(self):
        randomEffects = self.getGeneratedRandomEffects()
        hasRandomSlope = any("random slope" in randomEffects[group] for group in randomEffects)
        hasRandomIntercept = any("random intercept" in randomEffects[group] for group in randomEffects)
        hasCorrelation = any("correlated" in randomEffects[group] for group in randomEffects)
        tableHeader = [
            html.Thead(html.Tr(
                [html.Th("Group")] +
                ([html.Th("Random Intercept")] if hasRandomIntercept else []) +
                ([html.Th("Random Slope")] if hasRandomSlope else [])
                + ([html.Th("Correlated", style={"text-align": "center"})] if hasCorrelation else [])
            ))
        ]
        tableRows = []
        for group in sorted(list(randomEffects.keys())):
            groupDict = randomEffects[group]
            rowsToSpan = len(groupDict["random slope"]) if "random slope" in groupDict else 1
            row = [html.Td(group, rowSpan=rowsToSpan)]
            thisGroupHasCorrelation = "correlated" in groupDict

            if hasRandomIntercept and "random intercept" in groupDict:
                row.append(html.Td(["Yes ", getInfoBubble(self.randomIntercepts[group]["info-id"])], rowSpan=rowsToSpan))

            elif hasRandomIntercept:
                row.append(html.Td(rowSpan=rowsToSpan, className="bg-light"))
                pass
            if not hasRandomSlope:
                newId = self.getNewComponentId()
                if group not in self.rowIdsByUnit:
                    self.rowIdsByUnit[group] = []
                tableRows.append(html.Tr(row, id=newId))
                self.rowIdsByUnit[group].append(newId)
                self.unitsByRowId[newId] = group
                pass

            if hasRandomSlope and "random slope" in groupDict:
                randomSlopes = groupDict["random slope"]
                if len(randomSlopes) >= 1:
                    iv = randomSlopes[0]["iv"]
                    assert group in self.randomSlopes, "Random slopes does not contain {}:\n{}".format(group, self.randomSlopes)
                    row.append(html.Td(["IV: {} ".format(randomSlopes[0]["iv"]), getInfoBubble(self.randomSlopes[group][iv]["info-id"])]))
                    if thisGroupHasCorrelation:
                        row.append(html.Td(
                            dbc.FormGroup(
                                dbc.Checkbox(
                                    id=self.getCorrelatedIdForRandomSlope(group, iv),
                                    checked=True
                                )
                            ),
                            style={"text-align": "center"}
                        ))
                        pass
                    elif hasCorrelation:
                        row.append(html.Td(className="bg-light"))
                        pass
                    if group not in self.rowIdsByUnit:
                        self.rowIdsByUnit[group] = []
                        pass
                    newId = self.getNewComponentId()
                    tableRows.append(html.Tr(row, id=newId))
                    self.rowIdsByUnit[group].append(newId)
                    self.unitsByRowId[newId] = group

                    if len(randomSlopes) >= 2:
                        for r in randomSlopes[1:]:
                            iv = r["iv"]
                            rowId = self.getNewComponentId()
                            print("Adding row for iv {}".format(iv))
                            tableRows.append(
                                html.Tr(
                                    [
                                        html.Td(["IV: {} ".format(r["iv"]), getInfoBubble(self.randomSlopes[group][iv]["info-id"])])
                                    ] +
                                    ([
                                        html.Td(
                                            dbc.FormGroup(
                                                [
                                                dbc.Checkbox(
                                                    id=self.getCorrelatedIdForRandomSlope(group, iv),
                                                    checked=True
                                                )
                                            ]
                                            ),
                                            style={"text-align": "center"}
                                        )
                                    ] if hasCorrelation and thisGroupHasCorrelation else ([html.Td(className="bg-light")] if hasCorrelation else [])),
                                    id=rowId
                                )
                            )
                            self.rowIdsByUnit[group].append(rowId)
                            self.unitsByRowId[rowId] = group
                            pass
                        pass
                    pass
                pass
            elif hasRandomSlope:
                row.append(html.Td(rowSpan=rowsToSpan, className="bg-light"))
                if hasCorrelation:
                    row.append(html.Td(className="bg-light"))
                    pass
                newId = self.getNewComponentId()
                if group not in self.rowIdsByUnit:
                    self.rowIdsByUnit[group] = []
                tableRows.append(html.Tr(row, id=newId))
                self.rowIdsByUnit[group].append(newId)
                self.unitsByRowId[newId] = group
            pass
        return dbc.Table(tableHeader + [html.Tbody(tableRows)])





    def getRandomEffectsCard(self):
        randomeffects = self.getGeneratedRandomEffects()
        continueButton = dbc.Button("Continue", color="success", id="continue-to-family-link-functions", n_clicks=0)
        if not randomeffects:
            return dbc.Card(
                dbc.CardBody([
                    cardP(html.I("No random effects")),
                    html.P("Placeholder text for where an explanation would go"),
                    continueButton
                ])
            )
        return dbc.Card(
            dbc.CardBody(
                [
                    cardP("Random Effects"),
                    # self.layoutGeneratedRandomEffects(),
                    # html.P(""),
                    self.layoutRandomEffectsTable(),
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

            family_options.append({"label": label, "value": f})
            pass

        controls = dbc.Card(
            [
                dbc.FormGroup(
                    [
                        dbc.Label(["Family ", getInfoBubble("family-label-info")]),
                        dcc.Dropdown(
                            # id={'type': 'family_link_options', 'index': 'family_options'},
                            id="family-options",
                            options=family_options,
                            value="GaussianFamily",
                        ),
                    ]
                ),
                dbc.FormGroup(
                    [
                        dbc.Label(["Link function ", getInfoBubble("link-function-label-info")]),
                        dcc.Dropdown(
                            # id={'type': 'family_link_options', 'index': 'link_options'},
                            id="link-options",
                            options=[],
                            value="IdentityLink",
                        ),
                    ]
                ),
                dbc.Popover(
                    [
                        dbc.PopoverHeader("More on Link Functions"),
                        dbc.PopoverBody("* indicates the default/canonical link for the family"),

                    ],
                    target="link-function-label-info",
                    trigger="hover",
                    ),
                dbc.Popover(
                    [
                        dbc.PopoverHeader("More on Families of Distributions"),
                        dbc.PopoverBody("Some text"),
                    ],
                    target="family-label-info",
                    trigger="hover",
                )
            ],
            body=True,
            id={"type": "family_link_options", "index": "family_link_options"},
        )

        return controls

    def createFigure(self, family):
        key = f"{family}_data"
        if key in self.simulatedData:
            family_data = self.simulatedData[key]
        else:
            # Do we need to generate data?
            family_data = simulate_data_dist(
                    family)
            # Store data for family in __str_to_z3__ cache
        # We already have the data generated in our "cache"

        # if link is not None:
        #     assert(isinstance(link, str))
        #     link_fact = __str_to_z3__[link]
        #     # Transform the data
        #     transformed_data = transform_data_from_fact(data=family_data, link_fact=link_fact)

        # Generate figure
        fig = go.Figure()
        # fig.add_trace(
        #     go.Histogram(
        #         x=curr_data,
        #         name=f"{self.design.dv.name}",
        #     )
        # )
        fig.add_trace(
            go.Histogram(
                x=family_data, name=f"Simulated {family} distribution.",
                showlegend=True,
            )
        )
        fig.update_layout(barmode="overlay")
        fig.update_traces(opacity=0.75)
        fig.update_layout(
            legend=dict(
                orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
            )
        )
        return fig

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

        fig = self.createFigure("GaussianFamily")


        # Get form groups for family link div
        family_link_chart = dcc.Graph(id="family-link-chart", figure=fig) #self.draw_data_dist()
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
                dbc.Row(
                    [
                        dbc.Col(html.Div("Placeholder for normality tests"), md=12)
                    ],
                    align="center"
                ),
                # family_link_switch,
                dbc.Button("Generate Code", color="success", id="generate-code"),
                html.Div(id="generated-code-div")
            ]),
            className="mt-3"
        )

        ##### Return div
        return family_and_link_div

    def createEffectPopovers(self):
        mainEffects = self.getGeneratedMainEffects()
        interactionEffects = self.getGeneratedInteractionEffects()
        # randomEffects = self.getGeneratedRandomEffects()
        explanations = self.getExplanations()
        popovers = []
        for me in mainEffects:
            if me in explanations and me in self.variables["main effects"] and "info-id" in self.variables["main effects"][me]:
                popovers.append(
                    dbc.Popover(
                        [
                            dbc.PopoverHeader("Main Effect: {}".format(me)),
                            dbc.PopoverBody(explanations[me])
                        ],
                        target=self.variables["main effects"][me]["info-id"],
                        trigger="hover"
                    )
                )
                pass
            pass
        for ie in interactionEffects:
            if ie in explanations and ie in self.variables["interaction effects"] and "info-id" in self.variables["interaction effects"][ie]:
                popovers.append(
                    dbc.Popover(
                        [
                            dbc.PopoverHeader("Interaction Effect: {}".format(ie)),
                            dbc.PopoverBody(explanations[ie])
                        ],
                        target=self.variables["interaction effects"][ie]["info-id"],
                        trigger="hover"
                    )
                )
                pass
            pass
        for group, data in self.randomIntercepts.items():
            key = "{},RandomIntercept".format(group)
            if key in explanations and "info-id" in data:
                popovers.append(
                    dbc.Popover(
                        [
                            dbc.PopoverHeader("Random Intercept: {}".format(group)),
                            dbc.PopoverBody(html.Ul([html.Li(expl) for expl in explanations[key]]))
                        ],
                        target=data["info-id"],
                        trigger="hover"
                    )
                )
                pass
            pass
        for group, rsData in self.randomSlopes.items():
            for iv, ivData in rsData.items():
                key = "{}, {}, RandomSlope".format(group, iv)
                if key in explanations and "info-id" in ivData:
                    popovers.append(
                        dbc.Popover(
                            [
                                dbc.PopoverHeader("Random Slope: {}".format(iv)),
                                dbc.PopoverBody(html.Ul([html.Li(expl) for expl in explanations[key]]))
                            ],
                            target=ivData["info-id"],
                            trigger="hover"
                        )
                    )
        return popovers
