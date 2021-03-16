from tisane.statistical_model import StatisticalModel
from tisane.design import Design 
from tisane.graph import Graph 
from tisane.variable import AbstractVariable, Nominal, Ordinal, Numeric


from z3 import *
from typing import List, Union

##### GENERAL HELPERS #####
def parse_fact(fact: z3.BoolRef) -> List[str]: 
    fact_dict = dict()
    tmp = str(fact).split('(')
    func_name = tmp[0] 
    fact_dict['function'] = func_name
    
    # Parse Interaction facts aware that the argument is a SetSort
    if func_name == 'Interaction': 
        set_arg = fact.arg(0)
        arg_str = str(set_arg).split('False), ')

        assert(len(arg_str) == 2)
        arg_str = arg_str[1].split(',')

        # This for loop should take care of n-way Interactions
        variables = list()
        for s in arg_str: 
            if 'True' not in s: 
                variables.append(s.strip())
        fact_dict['variables'] = variables
    else: 
        variables = tmp[1].split(')')[0].split(',')
    
        if len(variables) == 1: 
            fact_dict['variable_name'] = variables[0].strip()
        elif len(variables) == 2: 
            fact_dict['start'] = variables[0].strip()
            fact_dict['end'] = variables[1].strip()
        
    return fact_dict

# Elicit info to and create a new variable 
def elicit_and_create_new_variable(): 
    # TODO: Provide option to exit?
    var_name = str(input(f"What is the name of the new variable? "))
    # TODO: Provide "None of the above" option?
    var_type_options = ['Nominal', 'Ordinal', 'Numeric']
    idx = int(input(f"What is the data type of \'{var_name}\'? Pick index number: {var_type_options} "))
    
    if idx in range(len(var_type_options)):
        var_type = var_type_options[idx]
    if var_type.upper() == 'NOMINAL': 
        return Nominal(name=var_name)
    elif var_type.upper() == 'ORDINAL': 
        return Ordinal(name=var_name)
    else: 
        assert(var_type.upper() == 'NUMERIC')
        return Numeric(name=var_name)

##### FOR PREPARING FOR QUERIES #####

# Ask users for which DV to consider when infering Designs and StatisitcalModels
def elicit_dv(gr: Graph):
    # TODO: Suggest nodes with only incoming edges and no outgoing edges?
    # edges = gr.get_edges() # get list of edges

    nodes = gr.get_nodes()
    node_names = [data['variable'].name for (n, data) in nodes]
    assert(len(nodes) == len(node_names))
    # TODO: An end-user may want to do this in a loop for more complex graphs/designs?
    idx = int(input(f'Which variable is your dependent variable: {node_names}? Choose index: '))

    if idx in range(len(nodes)):
        print(f'Ok, will use {node_names[idx]} as DV!')
    else: 
        raise ValueError("Index is out of range!")
    
    return  gr.get_variable(node_names[idx])

# Ask users about nesting and other structures
def elicit_structure_facts(gr: Graph, dv: AbstractVariable, variables: List[AbstractVariable]) -> List: 
    nodes = gr.get_nodes()

    ans = str(input(f'Are there any nesting relationships? Y or N:'))
    
    if ans.upper() == 'Y':
        variables = gr.get_variables() 
        variable_names = [v.name for v in variables]
        assert(len(variables) == len(variable_names))
        
        all_done = False

        while not all_done: 
            # TODO: Do we need to consider the case where we want to create a new variable UNIT and not just GROUP?
            idx_unit = int(input(f'Which variable is nested in another: {variable_names}? Choose index: '))

            if idx_unit in range(len(variables)): 
                unit = variables[idx_unit]
                group_variables = [v for v in variables if v.name != unit.name]
                options = [v.name for v in group_variables]
                assert(len(group_variables) == len(options))
                idx_group = str(input(f"Which variable is \'{unit}\' nested under?: {options}. Choose index or E to create a new variable: "))

                if idx_group.upper() == 'E': 
                    group = elicit_and_create_new_variable()
                    # TODO: Update w Graph IR?
                    gr._add_edge(start=group, end=unit, edge_type='nest')
                elif int(idx_group) in range(len(options)): 
                    group = group_variables[int(idx_group)]
                    # TODO: Update w Graph IR?
                    gr._add_edge(start=group, end=unit, edge_type='nest')
                else: 
                    raise ValueError(f"Unrecognized option: {idx_group}")
            else: 
                raise ValueError(f"Unrecognized option: {idx_group}")

            ans = str(input(f'Any more nesting relationships to declare? Y or N: '))
            if ans.upper() == 'N': 
                all_done = True

# @param gr is Graph from which to elicit treatment facts
def elicit_treatment_facts(gr: Graph, dv: AbstractVariable, variables: List[AbstractVariable], **kwargs) -> List: 
    # nodes = list(gr.nodes(data=True)) # get all nodes
    edges = gr.get_edges() # get list of edges

    for (n0, n1, edge_data) in edges:     
        edge_type = edge_data['edge_type']
        n0_var = gr.get_variable(n0)
        n1_var = gr.get_variable(n1)
        
        if n1_var is dv: 
            # Ask if treatment
            treatment_var_str = f"\'{n0_var.name}\'"
            ans = str(input(f'Is {treatment_var_str} a treatment? Y or N:')).upper()
            if ans == 'Y': 
                prompt = f'Which other variables does {treatment_var_str} treat?'
                
                # Filter out DV (n1_var) and n0_var
                variable_options = [v for v in variables if (v is not n0_var) and (v is not n1_var)]
                variable_options_names = [v.name for v in variable_options]
                assert(len(variable_options_names) == len(variable_options))
                if len(variable_options) > 0: 
                    options = f'Pick index of {variable_options_names} OR E to create a new variable.'
                    opt = input(prompt + ' ' + options)
                else: 
                    print(f'Looks like {treatment_var_str} is the only IV currently. What (new) variable does it treat?')
                    opt = 'E'
            
                if opt == 'E': 
                    # TODO: What happens if treats more than one variable? 
                    assert(opt.upper() == 'E')
                    var = elicit_and_create_new_variable()
                    # TODO: Update this when create Graph IR!
                    # TODO: This is a workaround, an observer pattern or something else might be better!
                    # REPLACE ivs and other objects in StatisticalModel, Design with calls to graph?
                    if 'input_obj' in kwargs: 
                        input_obj = kwargs['input_obj']
                        if isinstance(input_obj, Statistical): 
                            input_obj.add_main_effect(var) 
                        else:
                            raise NotImplementedError
                    else: 
                        # TODO: Replace with Treat when create Graph IR!
                        gr._add_edge(start=var, end=n1_var, edge_type='treat')
                else:  
                    if int(opt): 
                        idx = int(opt)
                        if idx in range(len(variable_options)): 
                            var_unit = variable_options[idx]
                            # TODO: Update this when create Graph IR!
                            import pdb; pdb.set_trace()
                            gr._add_edge(start=n0_var, end=var_unit, edge_type='treat')
                        else: 
                            raise ValueError (f"Picked an index out of bounds!")
                
            elif ans == 'N': 
                pass
            else: 
                raise ValueError
        else: 
            # TODO: This might happen for a mixed effect? 
            import pdb; pdb.set_trace()


##### FOR POSTPROCESSING QUERY RESULTS #####
def get_var_names_to_variables(input_obj: Union[Design]): 
    var_names_to_variables = dict()

    if isinstance(input_obj, Design) or isinstance(input_obj, StatisticalModel): 
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

def postprocess_to_statistical_model(model: z3.ModelRef, facts: List, graph: Graph, statistical_model: StatisticalModel) -> StatisticalModel: 
    fixed_ivs = list()
    interaction_ivs = list()
    random_slopes = list() 
    random_intercepts = list()
    
    for f in facts: 
        fact_dict = parse_fact(f)
        function = fact_dict['function']
        
        # Is this fact about Fixed effects?
        if function == 'FixedEffect': 
            # Get variable names
            iv = fact_dict['start']
            dv = fact_dict['end']
            # Get variables 
            iv_var = graph.get_variable(start_name)
            dv_var = graph.get_variable(end_name)
            
            assert(dv_var, dv)
            fixed_ivs.append(iv_var)

        # elif function == 'Interaction': 
        #     # TODO: This is where we would expand/change to allow for n-way interactions!
        #     # Get variable names
        #     start_name = fact_dict['start']
        #     end_name = fact_dict['end']
        #     # Get variables 
        #     start_var = graph.get_variable(start_name)
        #     end_var = graph.get_variable(end_name)

        #     interaction_effects.append((start_var, end_var))
            
        # elif ('Transform' in function) and (function != 'Transformation'): 
        #     assert('variable_name' in fact_dict)
        #     var_name = fact_dict['variable_name']

        #     # Apply transformation to variable, everywhere it exists in output_obj (StatisticalModel)
        #     var = graph.get_variable(var_name)
        #     var.transform(transformation=function)
            
    
    sm.set_fixed_ivs(fixed_ivs)
    # output_obj.set_interaction_effects(interaction_effects)    
    # output_obj.set_mixed_effects(mixed_effects)

    return sm

def statistical_model_to_graph(model: z3.ModelRef, updated_facts: List, input_obj: StatisticalModel, output_obj: Graph):
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