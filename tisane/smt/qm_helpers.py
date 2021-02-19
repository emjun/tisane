from tisane.statistical_model import StatisticalModel
from tisane.design import Design 
from tisane.graph import Graph 

from z3 import *
from typing import List, Union

##### GENERAL HELPERS #####
def parse_fact(fact: z3.BoolRef) -> List[str]: 
    fact_dict = dict()
    tmp = str(fact).split('(')
    func_name = tmp[0] 
    fact_dict['function'] = func_name
    variables = tmp[1].split(')')[0].split(',')
    
    # TODO: What if 3+-way interaction? 
    if len(variables) == 1: 
        fact_dict['variable_name'] = variables[0].strip()
    elif len(variables) == 2: 
        fact_dict['start'] = variables[0].strip()
        fact_dict['end'] = variables[1].strip()
    
    return fact_dict

##### FOR POSTPROCESSING QUERY RESULTS #####
def get_var_names_to_variables(input_obj: Union[Design]): 
    var_names_to_variables = dict()

    if isinstance(input_obj, Design): 
        for v in input_obj.get_variables(): 
            var_names_to_variables[v.name] = v

    return var_names_to_variables
    
def design_to_graph(model: z3.ModelRef, updated_facts: List, input_obj: Design, output_obj: Graph):

    var_names_to_variables = get_var_names_to_variables(input_obj=input_obj)

    for f in updated_facts: 
        fact_dict = parse_fact(f)

        if 'start' in fact_dict and 'end' in fact_dict:
            # Get variable names
            start_name = fact_dict['start']
            end_name = fact_dict['end']
            # Get variables
            start_var = var_names_to_variables[start_name]
            end_var = var_names_to_variables[end_name]

            if fact_dict['function'] == 'Cause': 
                output_obj.cause(start_var, end_var)
            elif fact_dict['function'] == 'Correlate': 
                output_obj.correlate(start_var, end_var)
            if fact_dict['function'] == 'Interaction': 
                # TODO: Should we add Interaction-specific edge??
                output_obj.correlate(start_var, end_var)
    
    return output_obj

def design_to_statistical_model(model: z3.ModelRef, updated_facts: List, input_obj: Design, output_obj: StatisticalModel):
    
    var_names_to_variables = get_var_names_to_variables(input_obj=input_obj)

    main_effects = list()
    interaction_effects = list()
    mixed_effects = list() 

    for f in updated_facts: 
        fact_dict = parse_fact(f)
        function = fact_dict['function']
        
        # Is this fact about the effects structure? (MAIN, INTERACTION)
        if function == 'MainEffect': 
            # Get variable names
            start_name = fact_dict['start']
            end_name = fact_dict['end']
            # Get variables 
            start_var = var_names_to_variables[start_name]
            end_var = var_names_to_variables[end_name]
            
            assert(end_var, input_obj.dv)
            main_effects.append(start_var)

        elif function == 'Interaction': 
            # TODO: This is where we would expand/change to allow for n-way interactions!
            # Get variable names
            start_name = fact_dict['start']
            end_name = fact_dict['end']
            # Get variables 
            start_var = var_names_to_variables[start_name]
            end_var = var_names_to_variables[end_name]

            interaction_effects.append((start_var, end_var))
            
        elif function == 'Transformation': 
            assert('variable_name' in fact_dict)
            var_name = fact_dict['variable_name']

            # TODO: Apply transformation to variable, everywhere it exists in output_obj (StatisticalModel)
            import pdb; pdb.set_trace()
            
    
    output_obj.set_main_effects(main_effects)    
    output_obj.set_interaction_effects(interaction_effects)    
    output_obj.set_mixed_effects(mixed_effects)

    return output_obj       