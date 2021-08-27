# Tisane GUI
Purpose: Asking disambiguation questions, offering interactions for helping analysts answer those questions, and saving answers to use when inferring a statistical model from a Tisane specification.

The motivating principle behind the interaction model behind Tisane, which includes the GUI and disambiguation questions, is to derive statistical models based on conceptual and data measurement relationships analysts express.

## Key challenge
The primary challenge we are trying to address through the Tisane GUI is to (1) suggest potential oversights in initial model specification at the query level based on the variable relationships the analyst expressed and (2) elicit runtime data-specific information (i.e., family and link functions). Both these tasks are necessary in order to generate a final statistical model and ensure that it has statistical conclusion and external validity.

A secondary challenge is to discourage analysts from p-hacking their statistical models. This challenge is already baked into our approach in designing Tisane because analysts author programs that describe variables and variable relationships, not statistical models directly in Tisane.

In order to address these challenges, we have specific design goals, below.

## Design goals
1. Provide an overiew of the query and interactively added variables to keep "local context" that expresses/represents analyst goals.  
2. Require analysts to consider omissions/alternatives that further their analysis goals.
3. Guide users through rationale for why Tisane makes specific suggestsions. Imagine users who may not know what a "main effect" or "random effect" is.
- This means that we should define terms wherever possible.
- This also means that we should indicate implications of decisions. (?)
> FEEDBACK REQUESTED: Do you think we should have any additional design goals/requirements?


## Features to add
> Feel free to update this list/keep track of them based on the design goals!
- If a set of effects (e.g., interaction effects) is not necessary, maybe have an explanation of why that tab isn't necessary/applicable and suggestion for how to update program in order to specify interactions?  [Design goal 3]

## Data flow overview
1. Once an analyst runs a Tisane program, the Tisane compiler will generate candidate main, interaction, and random effects and candidate family/link functions.
2. The Tisane compiler will ouptut a JSON file with all these candidates/options.
3. The Tisane GUI reads in this output JSON file and should keep track of/populate the app data according to the rules outlined in ``INFERENCE.md``. For example, only interaction effects with two or more main effects (including the variables included in the query) should be shown as options even though the Tisane compiler passes all possible interactions to the GUI.
4. When the analyst generates code, the Tisane GUI outputs a JSON file that the code generator reads in to generate the Python script.
> We might need to update/tweak this data flow design

## Sketches
[Here are the sketches we went over August 17](https://drive.google.com/file/d/1IPP6tfCSAZF2ogX4PJFo-d_d1OcLbRjK/view?usp=sharing)

## Previous code
From UIST 2021 submission: https://github.com/emjun/tisane/blob/main/tisane/smt/input_interface.py
- For generating family functions, see [LOC](https://github.com/emjun/tisane/blob/ed845debe44e5f1bf22b7ecabc1989c4df89a2f1/tisane/smt/input_interface.py#L670). It calls a helper function ``generate_data_dist_from_facts``, see [function definition](https://github.com/emjun/tisane/blob/ed845debe44e5f1bf22b7ecabc1989c4df89a2f1/tisane/helpers.py#L15). This functionality is now found in the Family instances themselves, see ``family.py`` [here](tisane/family.py). Each family has a ``simulate_data`` function that needs to be updated so that the appropriate parameters are passed. It might also make sense to make these ``simulate_data`` functions class functions rather that instance functions.

## Development notes
### Files
- `gui.py`: Main file for controlling GUI
- `example_inputs/`: Example JSON files for candidate statistical models
- `example.py`: Script to run GUI with data, edit to change the JSON file from `example_inputs` used to populate the GUI
- `generate_examples.py`: Script for creating the JSON files in example_inputs, calls functions in `tisane/main.py` to generate Python dictionary that is cast and output as JSON.
- `gui_components.py`: Stores code for layout of several components and provides an interface to the JSON input file
- `callbacks.py`: Main file for callbacks
- `family_link_function_callbacks.py`: Contains callbacks for the family and link functions tab
- `random_effects_callbacks.py`: Contains callbacks for the random effects tab
- `gui_helpers.py`: Functions that are generally helpful for multiple parts of the GUI
- `default_explanations.json`: Static text to be used. In certain situations, some of this text may only be displayed if, for example, no interaction effects were generated. For others, such as "link-functions", this text is always displayed as a popover. To include it as a popover, use the keys `"header"` and `"body"` to specify the popover.

### Functions
The main function for generating JSON from Tisane programs is `collect_model_candidates` in `tisane/main.py`. The output of this function is a JSON object that can be written out to a local file by calling `write_to_json` in `tisane/main.py`. The JSON object/file has the following general structure:
```
# Example taken from gui/example_inputs/main_interaction_random_intercept_slope_correlated.json
{
    "input": {
        "query": {
            "DV": "Time",
            "IVs": [
                "Word_type"
            ]
        },
        "generated main effects": [
            "Word_type"
        ],
        "generated interaction effects": [],
        "generated random effects": {
            "Subject": [
                {
                    "random intercept": {
                        "groups": "Subject"
                    }
                },
                {
                    "random slope": {
                        "iv": "Word_type",
                        "groups": "Subject"
                    }
                },
                {
                    "correlated": true
                }
            ],
            "Word": [
                {
                    "random intercept": {
                        "groups": "Word"
                    }
                }
            ]
        },
        "generated family, link functions": {
            "GaussianFamily": [
                "LogitLink",
                "LogLogLink",
                "ProbitLink",
                "CLogLogLink",
                "PowerLink",
                "IdentityLink",
                "OPowerLink",
                "LogLink",
                "NegativeBinomialLink"
            ],
            "InverseGaussianFamily": [
                "LogLink",
                "IdentityLink",
                "PowerLink"
            ],
            "PoissonFamily": [
                "PowerLink",
                "LogLink",
                "IdentityLink"
            ],
            "TweedieFamily": [
                "PowerLink",
                "LogLink",
                "IdentityLink"
            ],
            "GammaFamily": [
                "IdentityLink",
                "PowerLink",
                "LogLink"
            ]
        },
        "measures to units": {
            "Time": "Subject",
            "Word_type": "Subject"
        }
    }
}
```

### Example Plotly Dash apps
- Example gallery: https://dash-gallery.plotly.host/Portal/
- Code for example gallery, including the ones below: https://github.com/plotly/dash-sample-apps/tree/main/apps

- Overall layout with specific regions designated to specific tasks: https://dash-gallery.plotly.host/dash-daq-tektronix350/
- Overall layout, breadcrumbs at top (might use something like this for tracking progress): https://dash-gallery.plotly.host/ddk-oil-and-gas-demo/
- Overall layout, nice clean: https://dash-gallery.plotly.host/dash-aix360-heart/
- [For the tabbed section on the left (could use for Main, Interaction, Random Effects, and Family/Link)](https://dash-gallery.plotly.host/dash-alignment-chart/)

### Testing
- Make sure the app is running in debug mode (See line that reads something like``app.run_server(debug=True, threaded=True, port=port)``). This will update the app for you as you change the code. [More info on dev tools](https://dash.plotly.com/devtools).
- Run the app during development: ``run tisane/gui/example.py`` (I use poetry as my python virutal environment and package manager, so I run from the command line: ``poetry run python3 gui/example.py``)

### Styling
Dash Bootstrap documentation: https://dash-bootstrap-components.opensource.faculty.ai/docs/
