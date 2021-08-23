from tisane.gui.gui import TisaneGUI
import os


# @param input is a json file that has all the data to read in
def start_gui(input: str):
    gui = TisaneGUI()

    gui.start_app(input)


def createPath(fileName):
    exampleInputsDir = os.path.join(os.path.dirname(__file__), "example_inputs")
    return os.path.join(exampleInputsDir, fileName)


class ExampleData:
    main_only_input = os.path.join(
        os.path.dirname(__file__), "example_inputs/main_only.json"
    )
    main_interaction = os.path.join(
        os.path.dirname(__file__), "example_inputs/main_interaction.json"
    )
    main_interaction_random_intercepts = os.path.join(
        os.path.dirname(__file__),
        "example_inputs/main_interaction_random_intercepts.json",
    )
    main_interaction_random_intercept_slope_correlated = createPath(
        "main_interaction_random_intercept_slope_correlated.json"
    )
    main_interaction_multiple_random_slopes = createPath(
        "main_interaction_multiple_random_slopes.json"
    )
    # TODO: Add more input sources and json files here


start_gui(ExampleData.main_interaction_multiple_random_slopes)
