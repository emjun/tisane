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
import pandas as pd
import scipy.stats as stats
import numpy as np
from tisane.gui.gui_strings import GUIStrings

log = logging.getLogger("")
log.setLevel(logging.ERROR)

from tisane.gui.gui_helpers import simulate_data_dist


def cardP(text):
    return html.H5(text, className="card-text")


def checklist(labelList, id):
    return dcc.Checklist(
        options=[{"label": "{}".format(g), "value": g} for g in labelList],
        labelStyle={"display": "block"},
        id=id,
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
            words.append(mystr[start : i + 1])
    return words


def getInfoBubble(id: str):
    return html.I(className="bi bi-info-circle text-info", id=id)


class GUIComponents:
    def __init__(self, input_json: str, generateCode):
        self.strings = GUIStrings()
        dir = os.path.dirname(os.path.abspath(__file__))
        defaultExplanationsPath = os.path.join(dir, "default_explanations.json")
        if os.path.exists(defaultExplanationsPath):
            with open(defaultExplanationsPath, "r") as f:
                self.defaultExplanations = json.loads(f.read())
                pass
            pass
        else:
            self.defaultExplanations = {}
        self.numGeneratedComponentIds = 0
        self.codeGenerator = generateCode
        self.generatedComponentIdToRandomEffect = {}
        self.generatedComponentIdToMainEffect = {}
        self.generatedComponentIdToInteractionEffect = {}
        self.simulatedData = {}
        self.familyLinkFunctions = {}
        familyLinkFunctionsPath = os.path.join(dir, "family_link_functions.json")
        if os.path.exists(familyLinkFunctionsPath):
            with open(familyLinkFunctionsPath, "r") as f:
                self.familyLinkFunctions = json.loads(f.read())
                pass
            pass
        self.defaultLinkForFamily = {
            "GaussianFamily": "IdentityLink",
            "BinomialFamily": "LogitLink",
            "PoissonFamily": "LogLink",
            "TweedieFamily": "LogLink",
            "GammaFamily": "InverseLink",
            "NegativeBinomialFamily": "LogLink",
            "InverseGaussianFamily": "InverseSquaredLink",
        }
        self.output = {
            "main effects": [],
            "dependent variable": "",
            "interaction effects": [],
            "random effects": {},
            "family": "",
            "link": "",
        }
        self.highestActiveTab = -1

        self.variables = {"main effects": {}, "interaction effects": {}}
        self.rowIdsByUnit = {}
        self.unitsByAddedRandomVariableId = {}
        self.measuresByAddedRandomVariableId = {}
        self.unitsByRowId = {}
        self.randomSlopes = {}
        self.generatedCorrelatedIdToRandomSlope = {}
        log.debug(input_json)
        if os.path.exists(input_json):
            with open(input_json, "r") as f:
                self.data = json.loads(f.read())
                pass
            pass
        else:
            log.error("Cannot find input json file {}".format(input_json))
            exit(1)
            pass
        # print(self.data)

        query = self.getQuery()
        self.output["dependent variable"] = query["DV"]
        self.dv = query["DV"]
        if self.hasData():
            self.dataDf = pd.DataFrame(self.getData())
        for me in self.getGeneratedMainEffects():
            self.variables["main effects"][me] = {"info-id": self.getNewComponentId()}
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
                self.output["random effects"][unit]["random intercept"] = re[
                    "random intercept"
                ]
                pass
            if "random slope" in re:
                self.output["random effects"][unit]["random slope"] = re["random slope"]
                if "correlated" in re and re["correlated"]:
                    for slope in self.output["random effects"][unit]["random slope"]:
                        slope["correlated"] = True
        self.generatedCorrelatedIdToGroupIv = {}
        self.randomIntercepts = {}
        self.randomInterceptIdToGroup = {}
        self.randomSlopeAddedIdToGroupIv = {}
        self.randomSlopeIdToGroupIv = {}
        for unit, re in randomEffects.items():
            if "random intercept" in re:
                infoId = self.getNewComponentId()
                cellId = self.getNewComponentId()
                groupId = self.getNewComponentId()
                self.randomIntercepts[unit] = {
                    "info-id": infoId,
                    "cell-id": cellId,
                    "group-id": groupId,
                }
                self.randomInterceptIdToGroup[infoId] = unit
                self.randomInterceptIdToGroup[cellId] = unit
                self.randomInterceptIdToGroup[groupId] = unit
                pass
            if "random slope" in re and "random intercept" in re:
                if unit not in self.randomSlopes:
                    self.randomSlopes[unit] = {}
                    pass
                for rs in re["random slope"]:
                    newId = self.getNewComponentId()
                    infoId = self.getNewComponentId()
                    addedId = self.getNewComponentId()
                    cellId = self.getNewComponentId()
                    self.randomSlopes[unit][rs["iv"]] = {
                        "correlated-id": newId,
                        "info-id": infoId,
                        "added-id": addedId,
                        "cell-id": cellId,
                    }
                    self.generatedCorrelatedIdToRandomSlope[newId] = rs
                    self.generatedCorrelatedIdToGroupIv[newId] = (unit, rs["iv"])
                    self.randomSlopeAddedIdToGroupIv[addedId] = (unit, rs["iv"])
                    self.randomSlopeIdToGroupIv[cellId] = (unit, rs["iv"])
                    pass
                pass
            elif "random slope" in re:
                if unit not in self.randomSlopes:
                    self.randomSlopes[unit] = {}
                    pass
                for rs in re["random slope"]:
                    infoId = self.getNewComponentId()
                    addedId = self.getNewComponentId()
                    cellId = self.getNewComponentId()
                    self.randomSlopes[unit][rs["iv"]] = {
                        "info-id": infoId,
                        "added-id": addedId,
                        "cell-id": cellId,
                    }
                    self.randomSlopeAddedIdToGroupIv[addedId] = (unit, rs["iv"])
                    self.randomSlopeIdToGroupIv[cellId] = (unit, rs["iv"])
            pass
        # print(self.randomSlopes)
        self._init_helper()
        pass

    def _init_helper(self):
        # Additional initialization code
        self.units = set()
        self.unitToMeasures = {}
        for measure, unit in self.getMeasuresToUnits().items():
            if unit not in self.units:
                self.units.add(unit)
                self.unitToMeasures[unit] = [measure]
            else:
                self.unitToMeasures[unit].append(measure)
                pass
            pass
        measures = self.getMeasures()
        if self.dv not in measures:
            self.units.add(self.dv)
            pass
        for me in self.getGeneratedMainEffects():
            if not self.hasUnitForMeasure(me):
                # this is a unit
                self.units.add(me)
                pass
            pass
        for group in self.getGeneratedRandomEffects():
            if group not in self.units:
                self.units.add(group)
                pass
            pass

        # A set containing the units that do not have measures referenced, for
        # making sure they appear in random effects if present
        self.unitsWithoutVariables = set()
        for unit in self.units:
            if (
                unit != self.dv
                and unit not in self.unitToMeasures
                and unit not in self.getGeneratedMainEffects()
            ):
                self.unitsWithoutVariables.add(unit)
                pass
            pass
        self.randomEffectsUnitToRandomSlopeIVs = {}
        self.randomEffectsUnitToRandomSlopeAddedId = {}
        randomEffects = self.getGeneratedRandomEffects()
        for group, randomEffect in randomEffects.items():
            if "random slope" in randomEffect:
                if randomEffect["random slope"]:
                    self.randomEffectsUnitToRandomSlopeAddedId[
                        group
                    ] = self.getNewComponentId()
                for rs in randomEffect["random slope"]:
                    if "iv" in rs:
                        if group not in self.randomEffectsUnitToRandomSlopeIVs:
                            self.randomEffectsUnitToRandomSlopeIVs[group] = []
                            pass
                        self.randomEffectsUnitToRandomSlopeIVs[group].append(rs["iv"])
                        pass
                    pass
                pass
            pass
        self.randomSlopeAddedIdToUnit = {}
        for key, val in self.randomEffectsUnitToRandomSlopeAddedId.items():
            self.randomSlopeAddedIdToUnit[val] = key
            pass

        pass

    def filterOutput(self):
        log.debug("Raw output: {}".format(json.dumps(self.output, indent=4)))
        newOutput = {
            "main effects": sorted(self.output["main effects"]),
            "interaction effects": sorted(self.output["interaction effects"]),
            "dependent variable": self.output["dependent variable"],
            "family": self.output["family"],
            "link": self.output["link"],
            "random effects": {},
        }
        if "random effects" in self.output:
            for group, randomEffects in self.output["random effects"].items():
                groupDict = {}
                if "random intercept" in randomEffects:
                    randIntercept = randomEffects["random intercept"]
                    if "unavailable" in randIntercept:
                        if not randIntercept["unavailable"]:
                            groupDict["random intercept"] = {
                                key: value
                                for key, value in randIntercept.items()
                                if key != "unavailable"
                            }
                            pass
                        pass
                    else:
                        groupDict["random intercept"] = randIntercept
                    pass
                if "random slope" in randomEffects:
                    randSlope = randomEffects["random slope"]
                    for rs in randSlope:
                        if "unavailable" in rs:
                            if not rs["unavailable"]:
                                if "random slope" not in groupDict:
                                    groupDict["random slope"] = []
                                    pass
                                groupDict["random slope"].append(
                                    {
                                        key: value
                                        for key, value in rs.items()
                                        if key != "unavailable"
                                    }
                                )
                                pass
                            pass
                        else:
                            groupDict["random slope"].append(rs)
                            pass
                        pass
                    pass
                if groupDict:
                    if "random slope" in groupDict:
                        groupDict["random slope"] = sorted(
                            groupDict["random slope"], key=lambda rs: rs["iv"]
                        )
                    newOutput["random effects"][group] = groupDict
                pass
            pass
        return newOutput

    def getFamilyLinkFunctions(self):
        if self.hasRandomEffects():
            return self.familyLinkFunctions["with-mixed-effects"]
        return self.familyLinkFunctions["without-mixed-effects"]

    def generateCode(self):
        if self.codeGenerator:
            newOutput = self.filterOutput()
            destinationDir = os.getcwd()
            jsonFile = "model_spec.json"
            with open(os.path.join(destinationDir, jsonFile), "w") as f:
                f.write(json.dumps(newOutput, indent=4, sort_keys=True))
                pass
            path = self.codeGenerator(
                destinationDir=destinationDir, modelSpecJson=jsonFile
            )
            return path
        return False

    def getRandomInterceptCellIds(self):
        return [ri["cell-id"] for group, ri in self.randomIntercepts.items()]

    def getRandomEffectAddedGroupingIds(self):
        return [ri["group-id"] for group, ri in self.randomIntercepts.items()]

    def getGroupFromRandomInterceptId(self, id):
        assert (
            id in self.randomInterceptIdToGroup
        ), "Id {} not found in randomInterceptIdToGroup\n{}".format(
            id, json.dumps(self.randomInterceptIdToGroup, sort_keys=True, indent=2)
        )
        return self.randomInterceptIdToGroup[id]

    def getRandomSlopesVariousIds(self, key):
        ids = []
        for unit, randomSlope in self.randomSlopes.items():
            for iv, ivIds in randomSlope.items():
                if key in ivIds:
                    ids.append(ivIds[key])
                    pass
                pass
            pass
        return ids

    def getRandomSlopesIvCellIds(self):
        return self.getRandomSlopesVariousIds("cell-id")

    def getRandomSlopesIvAddedIds(self):
        ids = []
        for unit, randomSlope in self.randomSlopes.items():
            for iv, ivIds in randomSlope.items():
                if "added-id" in ivIds:
                    ids.append(ivIds["added-id"])
                    pass
                pass
            pass
        return ids

    def hasDefaultExplanations(self):
        return self.defaultExplanations

    def hasDefaultExplanation(self, key):
        return key in self.defaultExplanations

    def getDefaultExplanation(self, key):
        return self.defaultExplanations[key]

    def getDefaultExplanationSafe(self, key):
        if self.hasDefaultExplanations() and self.hasDefaultExplanation(key):
            return self.getDefaultExplanation(key)
        return None

    def getRandomEffectsUnavailableExplanation(self):
        return self.getDefaultExplanationSafe("random-effects-not-available")

    def getNoInteractionEffectsExplanation(self):
        return self.getDefaultExplanationSafe("no-interaction-effects")
        # key = "no-interaction-effects"
        # if self.hasDefaultExplanations() and self.hasDefaultExplanation(key):
        #     return self.getDefaultExplanation(key)
        # return None

    def getNoRandomEffectsExplanation(self):
        return self.getDefaultExplanationSafe("no-random-effects")
        # if self.hasDefaultExplanations() and self.hasDefaultExplanation(key):
        #     return self.getDefaultExplanation(key)
        # return None

    def getMeasures(self):
        return sorted(list(self.getMeasuresToUnits().keys()))

    def getMeasuresToUnits(self):
        return self.data["input"]["measures to units"]

    def hasUnitForMeasure(self, measure):
        return measure in self.getMeasuresToUnits()

    def getUnitFromMeasure(self, measure):
        measuresToUnits = self.getMeasuresToUnits()
        assert (
            measure in measuresToUnits
        ), "Measure {} not in measuresToUnits {}".format(measure, measuresToUnits)
        return measuresToUnits[measure]

    def getUnitFromRowId(self, rowId):
        assert rowId in self.unitsByRowId
        return self.unitsByRowId[rowId]

    def getUnitFromRowOrAddedRandomVariableId(self, id):
        assert (
            id in self.unitsByRowId or id in self.unitsByAddedRandomVariableId
        ), "Id {} in neither {} nor {}".format(
            id, self.unitsByRowId, self.unitsByAddedRandomVariableId
        )
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

    def hasExplanations(self):
        return "input" in self.data and "explanations" in self.data["input"]

    def getData(self):
        return self.data["input"]["data"]

    def hasData(self):
        return (
            "input" in self.data
            and "data" in self.data["input"]
            and self.data["input"]["data"]
        )

    def getDefaultLinkForFamily(self, family):
        if family in self.defaultLinkForFamily:
            return self.defaultLinkForFamily[family]
        return None

    def hasEffectForComponentId(self, componentId, effectDict):
        return componentId in effectDict

    def hasMainEffectForComponentId(self, componentId):
        return self.hasEffectForComponentId(
            componentId, self.generatedComponentIdToMainEffect
        )

    def hasInteractionEffectForComponentId(self, componentId):
        return self.hasEffectForComponentId(
            componentId, self.generatedComponentIdToInteractionEffect
        )

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
        assert componentId in effectDict, "Component id {} does not exist in {}".format(
            componentId, effectDict
        )
        return effectDict[componentId]

    def getMainEffectFromComponentId(self, componentId):
        return self.getEffectFromComponentId(
            componentId, self.generatedComponentIdToMainEffect
        )

    def getInteractionEffectFromComponentId(self, componentId):
        return self.getEffectFromComponentId(
            componentId, self.generatedComponentIdToInteractionEffect
        )

    def getRandomEffectFromComponentId(self, componentId):
        assert (
            componentId in self.generatedComponentIdToRandomEffect
        ), "Component id {} does not exist in {}".format(
            componentId, self.generatedComponentIdToRandomEffect
        )
        return self.generatedComponentIdToRandomEffect[componentId]

    def getRandomSlopeFromComponentId(self, componentId):
        assert (
            componentId in self.generatedCorrelatedIdToRandomSlope
        ), "Component id {} does not exist in {}".format(
            componentId, self.generatedCorrelatedIdToRandomSlope
        )
        return self.generatedCorrelatedIdToRandomSlope[componentId]

    def markCheckedForCorrelatedId(self, correlatedId, checked: bool):
        if self.hasGroupAndIvForCorrelatedId(correlatedId):
            group, iv = self.getGroupAndIvFromCorrelatedId(correlatedId)
            assert (
                group in self.output["random effects"]
                and "random slope" in self.output["random effects"][group]
            )
            for slope in self.output["random effects"][group]["random slope"]:
                if slope["iv"] == iv and "correlated" in slope:
                    slope["correlated"] = checked
                    pass
                pass
            pass
        pass

    def markUnavailableRandomEffect(
        self, group: str, iv: str = None, unavailable: bool = False
    ):
        assert (
            group in self.output["random effects"]
        ), "Group {} not in output random effects: {}".format(
            group, self.output["random effects"]
        )
        if iv is None:
            # iv is None, so this is a random intercept
            assert (
                "random intercept" in self.output["random effects"][group]
            ), "Could not find random intercept for group {} in output: {}".format(
                group, self.output["random effects"][group]
            )
            self.output["random effects"][group]["random intercept"][
                "unavailable"
            ] = unavailable
            pass
        elif iv:
            # iv needs to not be the empty string
            assert (
                "random slope" in self.output["random effects"][group]
            ), "Could not find random slopes for group {} in output: {}".format(
                group, self.output["random effects"][group]
            )
            for slope in self.output["random effects"][group]["random slope"]:
                if slope["iv"] == iv:
                    slope["unavailable"] = unavailable
                    pass
                pass
            pass
        pass

    def hasGroupAndIvForCorrelatedId(self, componentId):
        return componentId in self.generatedCorrelatedIdToGroupIv

    def getGroupAndIvFromCorrelatedId(self, componentId):
        assert (
            componentId in self.generatedCorrelatedIdToGroupIv
        ), "Component id {} does not exist in {}".format(
            componentId, self.generatedCorrelatedIdToGroupIv
        )
        return self.generatedCorrelatedIdToGroupIv[componentId]

    def hasRandomSlopeForComponentId(self, componentId):
        return componentId in self.generatedCorrelatedIdToRandomSlope

    def hasCorrelatedIdForRandomSlope(self, group, iv):
        return (
            group in self.randomSlopes
            and iv in self.randomSlopes[group]
            and "correlated-id" in self.randomSlopes[group][iv]
        )

    def getCorrelatedIdForRandomSlope(self, group, iv):
        assert self.hasCorrelatedIdForRandomSlope(group, iv)
        return self.randomSlopes[group][iv]["correlated-id"]

    def getRandomSlopeCheckboxIds(self):
        return list(self.generatedCorrelatedIdToRandomSlope.keys())

    def getNewComponentId(self):
        self.numGeneratedComponentIds += 1
        return "gui-components-unique-id-{}".format(self.numGeneratedComponentIds)

    def hasComponentIdForEffect(self, effect: str, effectsDict):
        assert effect in effectsDict, "Group {} not found in effects: {}".format(
            effect, effectsDict
        )
        return "component-id" in effectsDict[effect]

    def hasComponentIdForMainEffect(self, mainEffect: str):
        return self.hasComponentIdForEffect(mainEffect, self.variables["main effects"])

    def hasComponentIdForInteractionEffect(self, interactionEffect: str):
        return self.hasComponentIdForEffect(
            interactionEffect, self.variables["interaciton effects"]
        )

    def setComponentIdForEffect(self, effect, effectsDict, componentIdToEffect):
        assert effect in effectsDict, "{} not found in effects dict {}".format(
            effect, effectsDict
        )
        if not self.hasComponentIdForEffect(effect, effectsDict):
            newId = self.getNewComponentId()
            componentIdToEffect[newId] = effect
            effectsDict[effect]["component-id"] = newId
            return newId
        return effectsDict[effect]["component-id"]

    def setComponentIdForMainEffect(self, mainEffect):
        return self.setComponentIdForEffect(
            mainEffect,
            self.variables["main effects"],
            self.generatedComponentIdToMainEffect,
        )

    def setComponentIdForInteractionEffect(self, interactionEffect):
        return self.setComponentIdForEffect(
            interactionEffect,
            self.variables["interaction effects"],
            self.generatedComponentIdToInteractionEffect,
        )

    def hasComponentIdForRandomEffect(self, randomEffectGroup: str):
        randomEffects = self.getGeneratedRandomEffects()
        assert (
            randomEffectGroup in self.getGeneratedRandomEffects()
        ), "Group {} not found in generated random effects: {}".format(
            randomEffectGroup, randomEffects
        )
        return "component-id" in randomEffects[randomEffectGroup]

    def setComponentIdForRandomEffect(self, randomEffectGroup: str):
        randomEffects = self.getGeneratedRandomEffects()
        assert (
            randomEffectGroup in randomEffects
        ), "Group {} not found in generated random effects: {}".format(
            randomEffectGroup, randomEffects
        )
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
                html.H6(self.strings("overview", "interaction-effects-added")),
                html.Ul(id="added-interaction-effects"),
            ]
        return [
            html.H6(
                html.I(self.strings("overview", "interaction-effects-no-add")),
                id="added-interaction-effects",
            )
        ]

    def getRandomEffectsAddedSection(self):

        if self.hasRandomEffects():
            randomEffects = self.getGeneratedRandomEffects()
            info = []
            for group, randomEffect in randomEffects.items():
                titleId = self.getNewComponentId()
                self.unitsByAddedRandomVariableId[titleId] = group
                titleElement = html.H6(
                    group
                    + (
                        " (with random intercept)"
                        if "random intercept" in randomEffect
                        else ""
                    ),
                    id=titleId,
                )

                if "random slope" in randomEffect:
                    randomSlopes = []
                    for rs in randomEffect["random slope"]:
                        iv = rs["iv"]
                        listItemId = self.randomSlopes[group][iv][
                            "added-id"
                        ]  # self.getNewComponentId()
                        self.unitsByAddedRandomVariableId[listItemId] = group
                        randomSlopes.append(
                            html.Li(
                                [iv]
                                + (
                                    [
                                        html.Span(
                                            " (correlated)",
                                            id=self.getCorrelatedIdForRandomSlope(
                                                group, iv
                                            )
                                            + "-span",
                                        )
                                    ]
                                    if "correlated" in randomEffect
                                    else []
                                ),
                                id=listItemId,
                            )
                        )
                        pass
                    if randomEffect["random slope"]:
                        info.append(
                            html.Li(
                                [
                                    titleElement,
                                    html.Span(
                                        "Random slopes",
                                        id=self.randomEffectsUnitToRandomSlopeAddedId[
                                            group
                                        ],
                                    ),
                                    html.Ul(randomSlopes),
                                ],
                                id=self.randomIntercepts[group]["group-id"],
                            )
                        )
                        pass
                    else:
                        info.append(
                            html.Li(
                                [titleElement],
                                id=self.randomIntercepts[group]["group-id"],
                            )
                        )
                    pass
                else:
                    info.append(
                        html.Li(
                            titleElement, id=self.randomIntercepts[group]["group-id"]
                        )
                    )

            return [
                html.H5(self.strings("overview", "random-effects-added")),
                html.Ul(id="added-random-effects"),
                html.Ul(info),
            ]
        return [
            html.H6(
                html.I(self.strings("overview", "random-effects-no-add")),
                id="added-random-effects",
            )
        ]

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
        continueButtonPortion = [
            html.P(""),
            dbc.Button(
                "Continue",
                color="success",
                id="continue-to-interaction-effects",
                n_clicks=0,
            ),
        ]
        if ivs:
            body = [
                cardP(self.strings.getMainEffectsPageTitle()),
                dcc.Markdown(self.defaultExplanations["overall-main-effects"]),
                self.layoutFancyChecklist(
                    {
                        me: html.Span(
                            [
                                me + " ",
                                getInfoBubble(
                                    self.variables["main effects"][me]["info-id"]
                                ),
                            ]
                        )
                        for me in self.getGeneratedMainEffects()
                    },
                    self.setComponentIdForMainEffect,
                    {me: me in ivs for me in self.getGeneratedMainEffects()},
                ),
            ]
        else:
            body = [cardP(html.I(self.strings.getMainEffectsNoPageTitle()))]
        return dbc.Card(dbc.CardBody(body + continueButtonPortion), className="mt-3")

    def getInteractionEffectsCard(self):
        interactions = self.getGeneratedInteractionEffects()
        continueButton = dbc.Button(
            "Continue", color="success", id="continue-to-random-effects", n_clicks=0
        )
        assert self.hasDefaultExplanation(
            "no-interaction-effects"
        ), "Could not find interaction effect explanation in defaults: {}".format(
            self.defaultExplanations
        )
        if not interactions:
            # interactions is empty
            return dbc.Card(
                dbc.CardBody(
                    [
                        cardP(html.I(self.strings.getInteractionEffectsNoPageTitle())),
                        dcc.Markdown(
                            self.getNoInteractionEffectsExplanation()
                            or "Placeholder text for where an explanation would go"
                        ),
                        continueButton,
                    ]
                ),
                className="mt-3",
            )
        return dbc.Card(
            dbc.CardBody(
                [
                    cardP(self.strings.getInteractionEffectsPageTitle()),
                    dcc.Markdown(
                        self.defaultExplanations["overall-interaction-effects"]
                    ),
                    self.layoutFancyChecklist(
                        {
                            me: html.Span(
                                [
                                    me + " ",
                                    html.I(
                                        className="bi bi-info-circle",
                                        id=self.variables["interaction effects"][me][
                                            "info-id"
                                        ],
                                    ),
                                ]
                            )
                            for me in self.getGeneratedInteractionEffects()
                        },
                        self.setComponentIdForInteractionEffect,
                        {ie: False for ie in interactions},
                    ),
                    html.P(""),
                    continueButton,
                ]
            ),
            className="mt-3",
        )

    def layoutFancyChecklist(self, labelDict, componentIdSetter, checkedDict):
        options = []
        for name, label in labelDict.items():
            options.append(
                dbc.FormGroup(
                    [
                        dbc.Checkbox(
                            id=componentIdSetter(name),
                            className="form-check-input",
                            checked=checkedDict[name],
                        ),
                        dbc.Label(
                            label,
                            html_for=componentIdSetter(name),
                            className="form-check-label",
                        ),
                    ],
                    check=True,
                )
            )
            pass
        return html.Div(options)

    def makeFancyCheckbox(self, checked=False, label=None, id=None):
        if label:
            return dbc.FormGroup(
                [
                    dbc.Checkbox(
                        id=id,
                        className="form-check-input",
                        checked=checked,
                    ),
                    dbc.Label(label, html_for=id, className="form-check-label"),
                ],
                check=True,
            )
        return dbc.FormGroup(
            dbc.Checkbox(
                id=id,
                checked=checked,
            )
        )

    def layoutRandomEffectsTable(self):
        randomEffects = self.getGeneratedRandomEffects()
        hasRandomSlope = any(
            "random slope" in randomEffects[group] for group in randomEffects
        )
        hasRandomIntercept = any(
            "random intercept" in randomEffects[group] for group in randomEffects
        )
        hasCorrelation = any(
            "correlated" in randomEffects[group] for group in randomEffects
        )
        centeredStyle = {"text-align": "center"}
        booleans = [True, hasRandomIntercept, hasRandomSlope, hasCorrelation]
        # These are headers that just need to be wrapped in html.Th
        plainHeaders = ["Group", "Random Intercept", "Random Slope"]
        headers = [html.Th(head) for head in plainHeaders]
        # this one's a special case, so we add it separately
        # Also, it looked weird previously when it wasn't centered
        headers += [html.Th("Correlated", style=centeredStyle)]
        assert len(booleans) == len(
            headers
        ), "Number of booleans and headers does not match!\nNumber of booleans: {}\nNumber of headers: {}".format(
            len(booleans), len(headers)
        )
        # Use the `booleans` list to filter the headers
        headersLayout = [headers[i] for i in range(len(headers)) if booleans[i]]
        tableHeader = [html.Thead(html.Tr(headersLayout))]

        tableRows = []
        for group in sorted(list(randomEffects.keys())):
            groupDict = randomEffects[group]
            rowsToSpan = (
                len(groupDict["random slope"]) if "random slope" in groupDict else 1
            )
            row = [html.Td(group, rowSpan=rowsToSpan)]
            thisGroupHasCorrelation = "correlated" in groupDict

            if hasRandomIntercept and "random intercept" in groupDict:
                row.append(
                    html.Td(
                        [
                            "Yes ",
                            getInfoBubble(self.randomIntercepts[group]["info-id"]),
                        ],
                        rowSpan=rowsToSpan,
                        id=self.randomIntercepts[group]["cell-id"],
                    )
                )

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
                    assert (
                        group in self.randomSlopes
                    ), "Random slopes does not contain {}:\n{}".format(
                        group, self.randomSlopes
                    )
                    row.append(
                        html.Td(
                            [
                                "IV: {} ".format(randomSlopes[0]["iv"]),
                                getInfoBubble(self.randomSlopes[group][iv]["info-id"]),
                            ],
                            id=self.randomSlopes[group][iv]["cell-id"],
                        )
                    )
                    if thisGroupHasCorrelation:
                        row.append(
                            html.Td(
                                self.makeFancyCheckbox(
                                    id=self.getCorrelatedIdForRandomSlope(group, iv),
                                    checked=True,
                                ),
                                style=centeredStyle,
                            )
                        )
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
                            # print("Adding row for iv {}".format(iv))
                            correlationCheckbox = (
                                [
                                    html.Td(
                                        self.getFancyCheckbox(
                                            id=self.getCorrelatedIdForRandomSlope(
                                                group, iv
                                            ),
                                            checked=True,
                                        ),
                                        style=centeredStyle,
                                    )
                                ]
                                if hasCorrelation and thisGroupHasCorrelation
                                else (
                                    [html.Td(className="bg-light")]
                                    if hasCorrelation
                                    else []
                                )
                            )
                            tableRows.append(
                                html.Tr(
                                    [
                                        html.Td(
                                            [
                                                "IV: {} ".format(r["iv"]),
                                                getInfoBubble(
                                                    self.randomSlopes[group][iv][
                                                        "info-id"
                                                    ]
                                                ),
                                            ],
                                            id=self.randomSlopes[group][iv]["cell-id"],
                                        )
                                    ]
                                    + correlationCheckbox,
                                    id=rowId,
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
        assert self.hasDefaultExplanation(
            "no-random-effects"
        ), "Could not find default explanation for no random effects: {}".format(
            self.defaultExplanations
        )
        randomeffects = self.getGeneratedRandomEffects()
        continueButton = dbc.Button(
            "Continue",
            color="success",
            id="continue-to-family-link-functions",
            n_clicks=0,
        )
        if not randomeffects:
            return dbc.Card(
                dbc.CardBody(
                    [
                        cardP(html.I(self.strings.getRangetRandomEffectsNoPageTitle())),
                        html.P(
                            self.getNoRandomEffectsExplanation()
                            or "Placeholder text for where an explanation would go"
                        ),
                        continueButton,
                    ]
                ),
                className="mt-3",
            )
        return dbc.Card(
            dbc.CardBody(
                [
                    cardP(self.strings.getRandomEffectsPageTitle()),
                    dcc.Markdown(self.defaultExplanations["overall-random-effects"]),
                    self.layoutRandomEffectsTable(),
                    dcc.Markdown(id="random-effects-not-available-explanation"),
                    continueButton,
                ]
            ),
            className="mt-3",
        )

    def make_family_link_options(self):
        family_options = list()

        fls = self.getFamilyLinkFunctions()
        # link_options =

        for f in self.getGeneratedFamilyLinkFunctions():
            label = " ".join(separateByUpperCamelCase(f)[:-1])

            family_options.append(
                {"label": label, "value": f, "disabled": f not in fls}
            )
            pass

        linkExplanation = self.getDefaultExplanation("link-functions")
        familyExplanation = self.getDefaultExplanation("distribution-families")

        controls = dbc.Card(
            [
                dbc.FormGroup(
                    [
                        dbc.Label(["Family ", getInfoBubble("family-label-info")]),
                        dcc.Dropdown(
                            id="family-options",
                            options=family_options,
                            value="",
                            optionHeight=45,
                        ),
                    ]
                ),
                dbc.FormGroup(
                    [
                        dbc.Label(
                            [
                                "Link function ",
                                getInfoBubble("link-function-label-info"),
                            ]
                        ),
                        dcc.Dropdown(
                            id="link-options",
                            options=[],
                            value="",
                            optionHeight=45,
                        ),
                    ]
                ),
                dbc.Popover(
                    [
                        dbc.PopoverHeader(linkExplanation["header"]),
                        dbc.PopoverBody(dcc.Markdown(linkExplanation["body"])),
                    ],
                    target="link-function-label-info",
                    trigger="hover",
                ),
                dbc.Popover(
                    [
                        dbc.PopoverHeader(familyExplanation["header"]),
                        dbc.PopoverBody(dcc.Markdown(familyExplanation["body"])),
                    ],
                    target="family-label-info",
                    trigger="hover",
                ),
            ],
            body=True,
            id={"type": "family_link_options", "index": "family_link_options"},
        )

        return controls

    def createFigure(self, family):
        # Generate figure
        fig = go.Figure()
        if self.hasData():
            fig.add_trace(
                go.Histogram(x=self.dataDf[self.dv], name=f"{self.dv}", showlegend=True)
            )
        if family:
            key = f"{family}_data"

            if key in self.simulatedData:
                family_data = self.simulatedData[key]
            else:
                # Do we need to generate data?
                if self.hasData():
                    # dvData = np.log(self.dataDf[self.dv])
                    dvData = self.dataDf[self.dv]
                    family_data = simulate_data_dist(
                        family,
                        dataMean=dvData.mean(),
                        dataStdDev=dvData.std(),
                        dataSize=dvData.count(),
                    )
                    pass
                else:
                    family_data = simulate_data_dist(family)
                    pass
                self.simulatedData[key] = family_data
                pass

            fig.add_trace(
                go.Histogram(
                    x=family_data,
                    name=f"Simulated {family} distribution.",
                    showlegend=True,
                )
            )
        fig.update_layout(barmode="overlay")
        fig.update_traces(opacity=0.75)
        fig.update_layout(
            legend=dict(
                orientation="h", yanchor="bottom", y=1.09, xanchor="left", x=-0.1
            )
        )
        fig.update_layout(margin=dict(b=25, l=25, r=25, t=25))
        fig.update_layout(autosize=True)
        fig.update_layout(height=400)

        return fig

    def createNormalityTestSection(self):
        normalityTestPortion = [
            html.H5(
                [
                    html.I("No Normality Tests "),
                    getInfoBubble("no-normality-tests-info"),
                ]
            ),
            dbc.Popover(
                [
                    dbc.PopoverHeader("Why?"),
                    dbc.PopoverBody("No data included to run the normality tests."),
                ],
                target="no-normality-tests-info",
                trigger="hover",
            ),
        ]
        if self.hasData():
            normalityTestExplanation = self.getDefaultExplanation("normality-tests")
            dvData = self.dataDf[self.dv]
            shapiroStat, shapiroPvalue = stats.shapiro(dvData.values)
            normaltestStat, normaltestPvalue = stats.normaltest(dvData.values)

            shapiroHeader = html.Th(
                html.A(
                    "Shapiro-Wilk Test",
                    href="https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.shapiro.html",
                ),
                colSpan=2,
            )
            dagostinoAndPearsonsHeader = html.Th(
                html.A(
                    "D'Agostino and Pearson's Test",
                    href="https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.normaltest.html",
                ),
                colSpan=2,
            )
            testHeader = [
                html.Th("Test Statistic"),
                html.Th("P-Value"),
            ]

            tableHeader = html.Thead(
                [
                    html.Tr([shapiroHeader, dagostinoAndPearsonsHeader]),
                    html.Tr(testHeader + testHeader),
                ]
            )
            tableBody = html.Tbody(
                [
                    html.Tr(
                        [
                            html.Td("{:.5e}".format(shapiroStat)),
                            html.Td(
                                "{:.5e}{}".format(shapiroPvalue, "*" if shapiroPvalue < 0.05 else "")
                            ),
                            html.Td("{:.5e}".format(normaltestStat)),
                            html.Td(
                                "{:.5e}{}".format(
                                    normaltestPvalue,
                                    "*" if normaltestPvalue < 0.05 else ""
                                )
                            ),
                        ]
                    )
                ]
            )
            normalityTestPortion = [
                html.H5(["Normality Tests"]),
                dbc.Row(
                    [
                        dbc.Col(
                            dbc.Table(
                                [
                                    tableHeader,
                                    tableBody
                                ]
                            )
                        )

                    ]
                ),
                dcc.Markdown(normalityTestExplanation["note"]),
                html.H6(normalityTestExplanation["header"]),
                dcc.Markdown(normalityTestExplanation["body"])
                # dbc.Popover(
                #     [
                #         dbc.PopoverHeader(normalityTestExplanation["header"]),
                #         dbc.PopoverBody(normalityTestExplanation["body"]),
                #     ],
                #     target="normality-tests-info",
                #     trigger="hover",
                # ),
            ]
            pass
        return normalityTestPortion

    def createGraph(self, family):
        fig = self.createFigure(family)

        # Get form groups for family link div
        family_link_chart = dcc.Graph(
            id="family-link-chart",
            figure=fig,
            config={"responsive": True},
            style={"height": "inherit"},
        )
        return family_link_chart

    def getFamilyLinkFunctionsCard(self):
        ##### Collect all elements
        # Create family and link title
        family_link_title = html.Div(
            [
                html.H5(self.strings.getFamilyLinksPageTitle()),
                dcc.Markdown(
                    self.strings(
                        "family-link-functions", "titles", "page-sub-title"
                    ).format(self.getDependentVariable())
                ),
            ]
        )

        fig = self.createFigure("GaussianFamily")

        # Get form groups for family link div
        family_link_chart = html.Div(
            dcc.Graph(
                id="family-link-chart",
                figure=fig,
                config={"responsive": True},
                style={"height": "inherit"},
            ),
            id="family-link-chart-div",
        )
        family_link_controls = self.make_family_link_options()

        normalityTestPortion = self.createNormalityTestSection()
        ##### Combine all elements
        # Create div
        family_and_link_div = dbc.Card(
            dbc.CardBody(
                [
                    family_link_title,
                    dbc.Row(
                        [
                            dbc.Col(family_link_chart, sm=6, md=7, lg=8),
                            dbc.Col(family_link_controls, sm=6, md=5, lg=4),
                        ],
                        align="center",
                        no_gutters=True,
                    ),
                ]
                + normalityTestPortion
                + [
                    html.Span(
                        dbc.Button(
                            "Generate Code",
                            color="success",
                            id="generate-code",
                            disabled=True,
                            style={"pointer-events": "none"},
                        ),
                        id="generate-code-button-div",
                        tabIndex="0",
                        className="d-inline-block",
                    ),
                    html.Div(id="generated-code-div", hidden=True),
                    dbc.Tooltip(
                        "You still need to choose family and link functions before you can generate code.",
                        target="generate-code-button-div",
                        id="generate-code-tooltip",
                    ),
                ]
            ),
            className="mt-3",
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
            if (
                me in explanations
                and me in self.variables["main effects"]
                and "info-id" in self.variables["main effects"][me]
            ):
                popovers.append(
                    dbc.Popover(
                        [
                            dbc.PopoverHeader("Main Effect: {}".format(me)),
                            dbc.PopoverBody(explanations[me]),
                        ],
                        target=self.variables["main effects"][me]["info-id"],
                        trigger="hover",
                    )
                )
                pass
            pass
        for ie in interactionEffects:
            if (
                ie in explanations
                and ie in self.variables["interaction effects"]
                and "info-id" in self.variables["interaction effects"][ie]
            ):
                popovers.append(
                    dbc.Popover(
                        [
                            dbc.PopoverHeader("Interaction Effect: {}".format(ie)),
                            dbc.PopoverBody(explanations[ie]),
                        ],
                        target=self.variables["interaction effects"][ie]["info-id"],
                        trigger="hover",
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
                            dbc.PopoverBody(
                                html.Ul([html.Li(expl) for expl in explanations[key]])
                            ),
                        ],
                        target=data["info-id"],
                        trigger="hover",
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
                                dbc.PopoverBody(
                                    html.Ul(
                                        [html.Li(expl) for expl in explanations[key]]
                                    )
                                ),
                            ],
                            target=ivData["info-id"],
                            trigger="hover",
                        )
                    )
        return popovers

    def createCodeGenerationModal(self):
        modal = dbc.Modal(
            [
                dbc.ModalHeader("Code Generated!", id="code-generated-modal-header"),
                dbc.ModalBody("Placeholder", id="code-generated-modal-body"),
                dbc.ModalFooter(
                    dbc.Button(
                        "dismiss",
                        id="close-code-generated-modal",
                        className="ml-auto",
                        n_clicks=0,
                    )
                ),
            ],
            id="code-generated-modal",
            is_open=False,
        )
        store = dcc.Store(id="modal-data-store")
        return [modal, store]
