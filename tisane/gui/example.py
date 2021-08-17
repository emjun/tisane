from tisane.gui.gui import TisaneGUI

# @param input is a json file that has all the data to read in
def start_gui(input: str):
    gui = TisaneGUI()
    
    gui.start_app()

class ExampleData: 
    main_only_input="./example_inputs/main_only.json"
    # TODO: Add more input sources and json files here

start_gui()