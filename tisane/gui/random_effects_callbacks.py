from dash.dependencies import Output, Input, State, ALL, MATCH
import dash
from dash.exceptions import PreventUpdate
import dash_html_components as html
from tisane.gui.gui_components import GUIComponents, separateByUpperCamelCase
import json


def createRandomEffectsCallbacks(app, comp: GUIComponents = None):
    # createRandomEffectsAddedCallbacks(app, comp)
    createRandomEffectsCorrelationCallbacks(app, comp)
    createRandomEffectsVisibleCallbacks(app, comp)
    pass


def createRandomEffectsAddedCallbacks(app, comp: GUIComponents = None):
    inputs = [Input(id, "checked") for id in comp.getRandomEffectCheckboxIds()]
    states = [State(id, "id") for id in comp.getRandomEffectCheckboxIds()]

    @app.callback(Output("added-random-effects", "children"), inputs, states)
    def addRandomEffects(*args):
        assert len(args) % 2 == 0, "Length of args is weird: {}".format(args)
        if not comp:
            print("Cannot update added random effects")
            raise PreventUpdate
        if args:
            print("Adding random effects")
            half = int(len(args) / 2)
            inputs = args[:half]
            states = args[half:]
            print(inputs)
            checked = []
            for i in range(len(inputs)):
                id = states[i]
                input = inputs[i]
                if input and comp.hasRandomEffectForComponentId(id):
                    randomEffect = comp.getRandomEffectFromComponentId(id)
                    checked.append(randomEffect)
                    pass
                pass
            return [html.Li(str(c)) for c in checked]
        print("Could not add random effects")
        raise PreventUpdate


def createRandomEffectsCorrelationCallbacks(app, comp: GUIComponents = None):
    if comp:
        checkboxIds = comp.getRandomSlopeCheckboxIds()
        if checkboxIds:
            inputs = [Input(id, "checked") for id in checkboxIds]
            states = [State(id, "id") for id in checkboxIds]
            outputs = [Output(id + "-span", "children") for id in checkboxIds]

            @app.callback(outputs, inputs, states)
            def changeCorrelation(*args):
                assert len(args) % 2 == 0, "Weird number of arguments: {}".format(
                    len(args)
                )

                if not comp:
                    print("Cannot update correlations")
                    raise PreventUpdate

                if args:
                    half = int(len(args) / 2)
                    inputs = args[:half]
                    states = args[half:]
                    # dict of id to checked
                    idToChecked = {states[i]: inputs[i] for i in range(half)}
                    idToCorrelated = {}
                    for id, checked in idToChecked.items():
                        idToCorrelated[id] = (
                            " (correlated)" if checked else " (not correlated)"
                        )
                        comp.markCheckedForCorrelatedId(id, checked)
                    return tuple([idToCorrelated[id] for id in checkboxIds])
                raise PreventUpdate


def createRandomEffectsVisibleCallbacks(app, comp: GUIComponents = None):
    if comp:
        rowIds = comp.getRandomEffectsRowIds()
        # addedRandomVariableIds = comp.getAddedRandomVariableIds()
        # allIds = rowIds + addedRandomVariableIds
        allIds = rowIds
        if allIds:
            print("allIds: {}".format(allIds))
            rowOutputs = [Output(id, "hidden") for id in allIds]
            rowOutputs = rowOutputs + [Output("random-effects-check-store", "data")]

            @app.callback(rowOutputs, Input("added-main-effects-store", "data"), Input("added-interaction-effects-store", "data"))
            def changeVisibility(outputFromMainEffectsString, outputFromInteractionEffectsString):
                outputFromMainEffects = json.loads(outputFromMainEffectsString) if outputFromMainEffectsString else {"main effects": [], "dependent variable": ""}
                outputFromInteractionEffects = json.loads(outputFromInteractionEffectsString) if outputFromInteractionEffectsString else {"interaction effects": []}
                if (
                    "main effects" in outputFromMainEffects
                    and "dependent variable" in outputFromMainEffects and "interaction effects" in outputFromInteractionEffects
                ):
                    dv = outputFromMainEffects["dependent variable"]
                    visibleMainEffects = outputFromMainEffects["main effects"]
                    visibleInteractionEffects = outputFromInteractionEffects["interaction effects"]
                    allVisible = [dv] + visibleMainEffects + visibleInteractionEffects
                    allVisibleUnits = set(
                        [
                            comp.getUnitFromMeasure(vis)
                            if comp.hasUnitForMeasure(vis)
                            else vis
                            for vis in allVisible
                        ]
                    )

                    units = [
                        comp.getUnitFromRowOrAddedRandomVariableId(id) for id in allIds
                    ]
                    allVisibleObject = {
                        "allVisible": allVisible
                    }
                    return tuple([u not in allVisibleUnits and u not in comp.unitsWithoutVariables for u in units] + [json.dumps(allVisibleObject)])
                raise PreventUpdate

            randomSlopeAddedIds = sorted(list(comp.randomSlopeAddedIdToUnit.keys()))
            individualIds = comp.getRandomSlopesIvAddedIds()
            cellIds = comp.getRandomSlopesIvCellIds()
            correlatedIds = comp.getRandomSlopeCheckboxIds()
            randomSlopeAddedOutputs = [Output(id, "hidden") for id in (randomSlopeAddedIds + individualIds) ]
            cellOutputs = [Output(id, "style") for id in cellIds]
            correlatedOutputs = [Output(id, "disabled") for id in correlatedIds]
            print("randomSlopeAddedIds: {}, {}".format(randomSlopeAddedIds, individualIds))
            @app.callback(
                randomSlopeAddedOutputs + cellOutputs + correlatedOutputs,
                Input("random-effects-check-store", "data")
            )
            def changeRandomSlopeSpanVisibility(allVisibleJsonString):
                if allVisibleJsonString:
                    allVisibleObject = json.loads(allVisibleJsonString)
                    allVisible = allVisibleObject["allVisible"]

                    result = []
                    for id in randomSlopeAddedIds:
                        unit = comp.randomSlopeAddedIdToUnit[id]
                        result.append(not any(iv in allVisible for iv in comp.randomEffectsUnitToRandomSlopeIVs[unit]))
                        pass
                    for id in individualIds:
                        unit, iv = comp.randomSlopeAddedIdToGroupIv[id]
                        result.append(iv not in allVisible)
                        pass
                    for id in cellIds:
                        unit, iv = comp.randomSlopeIdToGroupIv[id]
                        if iv not in allVisible:
                            result.append({
                                "opacity": 0.5
                            })
                            pass
                        else:
                            result.append({
                                "opacity": 1.0
                            })
                        # result.append(iv not in allVisible)

                        # result.append("bg-light" if iv not in allVisible else "")
                        pass
                    for id in correlatedIds:
                        unit, iv = comp.getGroupAndIvFromCorrelatedId(id)
                        result.append(iv not in allVisible)
                    return tuple(result)
                raise PreventUpdate
