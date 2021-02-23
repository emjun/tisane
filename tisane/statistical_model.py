from tisane.concept import Concept
from tisane.variable import AbstractVariable, Nominal, Ordinal, Numeric
from tisane.effect_set import EffectSet, MainEffect, InteractionEffect, MixedEffect
from tisane.graph import Graph
from tisane.smt.knowledge_base import KB
# from tisane.smt.rules import Cause, Correlate, MainEffect, NoMainEffect, Interaction, NoInteraction, NominalDataType, OrdinalDataType, NumericDataType, Transformation, NoTransformation, NumericTransformation, CategoricalTransformation, LogTransform, SquarerootTransform, LogLogTransform, ProbitTransform, LogitTransform
from tisane.smt.rules import *
# from tisane.smt.query_manager import QM

from abc import abstractmethod
import pandas as pd
from typing import List, Any, Tuple
from itertools import chain, combinations

from z3 import *

##### HELPER ##### 
def powerset(iterable):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))

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


# TODO: Make this an abstract class, at least in name?
class StatisticalModel(object): 
    # residuals: AbstractVariable
    # TODO: May not need properties since not sure what the properties would be if not the indivdiual variables or the residuals
    properties: list # list of properties that this model exhibits

    main_effects: List[AbstractVariable]
    interaction_effects: List[Tuple[AbstractVariable, ...]]
    mixed_effects: List[AbstractVariable]
    link_function: str # maybe, not sure?
    variance_function: str # maybe, not sure?

    graph : Graph # IR

    consts: dict # Z3 consts representing the model and its DV, main_effects, etc. 


    def __init__(self, dv: AbstractVariable, main_effects: List[AbstractVariable]=None, interaction_effects: List[Tuple[AbstractVariable, ...]]=None, mixed_effects: List[AbstractVariable]=None, link_func: str=None, variance_func: str=None): 
        self.dv = dv

        self.graph = Graph()
        self.graph._add_variable(self.dv)
        
        if main_effects is not None: 
            self.set_main_effects(main_effects=main_effects)
        else: 
            self.main_effects = list()
        
        if interaction_effects is not None: 
            self.set_interaction_effects(interaction_effects=interaction_effects)
        else: 
            self.interaction_effects = list()
        
        if mixed_effects is not None: 
            self.set_mixed_effects(mixed_effects=mixed_effects)
        else: 
            self.mixed_effects = list()

        self.link_func = link_func
        self.variance_func = variance_func

        self.consts = dict()
        # self.generate_consts()

    # TODO: Should be class method? 
    def create_from(graph: Graph): 
        raise NotImplementedError

    def __str__(self): 
        dv = f"DV: {self.dv}\n"
        main_effects = f"Main effects: {self.main_effects}\n" 
        interaction_effects = f"Interaction effects: {self.interaction_effects}\n"
        mixed_effects = f"Mixed effects: {self.mixed_effects}"
        
        return dv + main_effects + interaction_effects + mixed_effects

    # @return string of mathematical version of the statistical model    
    # TODO: @param setting might tell us something about how to format the categorical variables...
    def mathematize(self, setting=None): 
        
        def transform_var(var: AbstractVariable): 
            if var.transform != 'NoTransformation': 
               return var.transform + '('  + var.name + ')'
            
            return var.name
            
        y = transform_var(self.dv)
        xs = list()
        
        for m in self.main_effects: 
            xs.append(transform_var(m))
        
        for i in self.interaction_effects: 
            x = '('
            # Iterate through variables involved in interaction
            for idx in range(len(i)): 
                x += transform_var(i[idx])
                if idx+1 < len(i): 
                    x += '*'
            x += ')'
            xs.append(x)
        
        for mi in self.mixed_effects: 
            # TODO: Implement, may want to do something special about slope vs. intercept vs. both....
            pass
        
        equation = y + ' = ' + '+'.join(xs)
        return equation

    # Sets main effects to @param main_effects
    def set_main_effects(self, main_effects: List[AbstractVariable]): 
        self.main_effects = main_effects

        # Update the Graph IR
        for m in self.main_effects: 
            self.graph.unknown(lhs=m, rhs=self.dv)

    # Sets interaction effects to @param main_effects
    def set_interaction_effects(self, interaction_effects: List[AbstractVariable]): 
        self.interaction_effects = interaction_effects

        # There may be 2+-way interactions
        for ixn in self.interaction_effects: 
            # For each interaction, add edges between the variables involved in the interaction
            # Get powerset of ixn 
            pset = list(powerset(ixn))
            # Only keep sets that are of size 2 
            pset_len_2 = [p for p in pset if len(p) == 2]
            
            # Update the Graph IR
            for p in pset_len_2: 
                assert(len(p)==2)
                lhs = p[0]
                rhs = p[1]
                self.graph.unknown(lhs=lhs, rhs=rhs)

    # Sets mixed effects to @param mixed_effects
    def set_mixed_effects(self, mixed_effects: List[AbstractVariable]): 
        self.mixed_effects = mixed_effects

        for mi in self.mixed_effects: 
            self.graph.unknown(lhs=mi, rhs=self.dv)
    
    # @return all variables (DV, IVs)
    def get_variables(self) -> List[AbstractVariable]: 
        variables = [self.dv] + self.main_effects
        
        for ixn in self.interaction_effects: 
            for i in ixn: 
                # Check that we haven't already added the variable (as a main effect)
                if i not in variables: 
                    variables.append(i)
        
        # TODO for mixed effects!
        for mi in self.mixed_effects: 
            pass

        return variables

    # @return a list containing all the IVs
    def get_all_ivs(self):     
        return self.main_effects + self.interaction_effects + self.mixed_effects

    def add_main_effect(self, new_main_effect: AbstractVariable, **kwargs): 
        if 'edge_type' in kwargs: 
            edge_type = kwargs['edge_type']
        else: 
            edge_type = 'unknown'

        updated_main_effects = self.main_effects + [new_main_effect]
        # TODO: Update when move to Graph IR -- add a treat Graph function?
        self.graph._add_edge(start=new_main_effect, end=self.dv, edge_type=edge_type)

    # @return Z3 consts for variables in model
    def generate_consts(self): 
        # Declare data type
        Object = DeclareSort('Object')
        
        # Create and add Z3 consts for all main effects
        main_effects = self.main_effects
        
        main_seq = None
        if len(self.main_effects) > 0: 
            for me in main_effects: 
                # Have we created a sequence of IVs yet?
                # If not, create one
                if main_seq is None: 
                    # set first Unit of sequence
                    main_seq = Unit(me.const)
                # We already created a sequence of IVs
                else: 
                    # Concatenate
                    main_seq = Concat(Unit(me.const), main_seq)
        # There are no main effects
        else: 
            main_seq = Empty(SeqSort(Object))
        
        self.consts['main_effects'] = main_seq

        # Create and add Z3 consts for Interaction effects
        interactions_seq = None
        if len(self.interaction_effects) > 0: 
            for ixn in self.interaction_effects: 
                tmp = EmptySet(Object) 
                
                # For each variable in the interaction tuple
                for v in ixn: 
                    tmp = SetAdd(tmp, v.const)

                # Do we already have a sequence we're building onto?
                # If not, create one
                assert(tmp is not None)
                if interactions_seq is None: 
                    # Create a sequence
                    interactions_seq = Unit(tmp)
                # We already have a sequence of interactions
                else: 
                    # Concatenate
                    interactions_seq = Concat(Unit(tmp), interactions_seq)
        # There are no interaction effects
        else: 
            interactions_seq = Unit(EmptySet(Object))

        self.consts['interactions'] = interactions_seq
    
        
    # @returns the set of logical facts that this StatisticalModel "embodies"
    def compile_to_facts(self) -> List: 
        facts = list()

        # Declare data type
        Object = DeclareSort('Object')

        # Add interaction effects 
        if self.interaction_effects is not None: 
            # i_set is a Tuple of AbstractVariables
            for i_set in self.interaction_effects: 
                # Create set object
                tmp = EmptySet(Object) 
                # Add each variable in the interaction set
                for v in i_set: 
                    tmp = SetAdd(tmp, v.const)

                facts.append(Interaction(tmp))
        
        # Add link function 
        if self.link_func is not None: 
            if self.link_func == 'Log': 
                facts.append(LogTransform(self.dv.const))
            elif self.link_func == 'Squareroot': 
                facts.append(SquarerootTransform(self.dv.const))
            elif self.link_func == 'LogLog': 
                facts.append(LogLogTransform(self.dv.const))
            elif self.link_func == 'Probit': 
                facts.append(ProbitTransform(self.dv.const))
            elif self.link_func == 'Logit': 
                facts.append(LogitTransform(self.dv.const))
            else: 
                raise ValueError (f"Link function not supproted: {self.link_func}")

        # Add variance function 
        if self.variance_func is not None: 
            if self.variance_func == 'Gaussian': 
                facts.append(Gaussian(self.dv.const))
            elif self.variance_func == 'InverseGaussian': 
                facts.append(InverseGaussian(self.dv.const))
            elif self.variance_func == 'Binomial': 
                facts.append(Binomial(self.dv.const))
            elif self.variance_func == 'Multinomial': 
                facts.append(Multinomial(self.dv.const))
            else: 
                raise ValueError (f"Variance function not supported: {self.variance_func}")

        # Add variable data types
        variables = self.get_variables()
        for v in variables: 
            if isinstance(v, Nominal): 
                facts.append(NominalDataType(v.const))
            elif isinstance(v, Ordinal): 
                facts.append(OrdinalDataType(v.const))
            elif isinstance(v, Numeric):
                facts.append(NumericDataType(v.const))
            elif isinstance(v, AbstractVariable): 
                pass
            else: 
                raise ValueError

        # Add structure facts
        edges = self.graph._graph.edges(data=True)
        for (n0, n1, edge_data) in edges: 
            edge_type = edge_data['edge_type']
            n0_var = self.graph._graph.nodes[n0]['variable']
            n1_var = self.graph._graph.nodes[n1]['variable']

            if edge_type == 'treat': 
                pass
                # # n0_var is unit
                # facts.append()
                # # n1_var is treatment
                # facts.append()

            elif edge_type == 'nest': 
                pass
                # TODO: Useful for mixed effects
            else: 
                pass

            # What is the unit
            # What is the nesting 
    
        return facts

    def elicit_structure_facts(self) -> List: 
        edges = list(self.graph._graph.edges(data=True)) # get list of edges

        for (n0, n1, edge_data) in edges:        
            edge_type = edge_data['edge_type']
            n0_var = self.graph._graph.nodes[n0]['variable']
            n1_var = self.graph._graph.nodes[n1]['variable']


            if n1_var is self.dv: 
                # Ask about Nesting 
                # TODO: START HERE: Test elicit_treatment_facts end-to-end before add this method?
                # TODO: probably very similar to elicit_treatment_facts. 
                idx = int(input(f'These cannot be true at the same time. Which is true? If neither, enter -1. {unsat_core}:'))
                if idx == -1: 
                    pass
                    # TODO: Remove both?
                elif idx in range(len(unsat_core)): 
                    # only keep the constraint that is selected. 
                    constraint = unsat_core[idx] 
                    keep.append(constraint)
                    print(f"Ok, going to add {constraint} and remove the others.")
                    break
                else:
                    raise ValueError

                
                # If so, which variable does it treat: existing or new 
                # TODO: What happens if treats more than one variable? 

                # Create New Variable

                # Add treatment, unknown edges

            else: 
                # TODO: This might happen for a mixed effect? 
                import pdb; pdb.set_trace()



    def elicit_treatment_facts(self) -> List: 
        # nodes = list(self.graph._graph.nodes(data=True)) # get all nodes
        edges = list(self.graph._graph.edges(data=True)) # get list of edges

        for (n0, n1, edge_data) in edges:        
            edge_type = edge_data['edge_type']
            n0_var = self.graph._graph.nodes[n0]['variable']
            n1_var = self.graph._graph.nodes[n1]['variable']
            
            if n1_var is self.dv: 
                # Ask if treatment
                treatment_var_str = f"\'{n0_var.name}\'"
                ans = str(input(f'Is {treatment_var_str} a treatment? Y or N:')).upper()
                if ans == 'Y': 
                    prompt = f'Which other variables does {treatment_var_str} treat?'
                    
                    variables = self.get_variables()
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
                        self.add_main_effect(var)

                    else:  
                        if int(opt): 
                            idx = int(opt)
                            if idx in range(len(variable_options)): 
                                var_unit = variable_options[idx]
                                # TODO: Update this when create Graph IR!
                                import pdb; pdb.set_trace()
                                self.graph._add_edge(start=n0_var, end=var_unit, edge_type='treat')
                            else: 
                                raise ValueError (f"Picked an index out of bounds!")
                    
                elif ans == 'N': 
                    pass
                else: 
                    raise ValueError
            else: 
                # TODO: This might happen for a mixed effect? 
                import pdb; pdb.set_trace()

    # @return additional set of logical facts that needs disambiguation depending on @param desired output_obj
    def collect_ambiguous_facts(self, output: str) -> List: 
        facts = list()
        edges = list(self.graph._graph.edges(data=True)) # get list of edges

        if output.upper() == 'VARIABLE RELATIONSHIP GRAPH': 
            # Iterate over all edges
            # This covers all the interactions, too. 
            for (n0, n1, edge_data) in edges:         
                edge_type = edge_data['edge_type']
                n0_var = self.graph._graph.nodes[n0]['variable']
                n1_var = self.graph._graph.nodes[n1]['variable']
                if edge_type == 'unknown':
                    if output.upper() == 'VARIABLE RELATIONSHIP GRAPH': 
                        # Induce UNSAT in order to get end-user clarification
                        facts.append(Cause(n0_var.const, n1_var.const))
                        facts.append(Correlate(n0_var.const, n1_var.const))
                else: 
                    raise NotImplementedError
        elif output.upper() == 'STUDY DESIGN': 
            # Data schema
            nodes = list(self.graph._graph.nodes(data=True))
            for (n, data)  in nodes: 
                n_var = data['variable']
                facts.append(NumericDataType(n_var.const))
                facts.append(CategoricalDataType(n_var.const)) 
                # TODO: Start here: Find data type info during prep_query? 
                # Doing so seems to defeat purpose of interactive synth procedure...
                # Maybe I don't need to add these ambiguous facts since I have a link and variance functions? 
                # Think through (1) have link and variance functions, (2) do not have (this seems like a separate pre-step...?)
                # Map out diagrammatically what looking for, etc.

                # facts.append(NominalDataType(n_var.const))
                # facts.append(OrdinalDataType(n_var.const))

            # Data collection procedure    
            for (n0, n1, edge_data) in edges: 
                edge_type = edge_data['edge_type']
                n0_var = self.graph._graph.nodes[n0]['variable'] # treatment
                n1_var = self.graph._graph.nodes[n1]['variable'] # unit
                if edge_type == 'treat':
                    facts.append(Between(n1_var.const, n0_var.const))
                    facts.append(Within(n1_var.const, n0_var.const))
                
        return facts

    def query(self, outcome: str) -> Any: 
        # Ground some rules to make the quantification simpler
        dv_const = self.consts['dv']
        main_effects = self.consts['main_effects']
        interactions = self.consts['interactions']
        KB.ground_rules(dv_const=dv_const, main_effects=main_effects, interactions=interactions)
        
        # Collect facts based on @param outcome
        facts = self.collect_facts(outcome=outcome)
        # Collect rules based on @param outcome
        result = QM.query(outcome=outcome, facts=facts)
        
        if outcome.upper() == 'VARIABLE RELATIONSHIP GRAPH': 
            graph = Graph()
            # TODO: update graph based on result (Z3 model)
            return graph


    def collect_facts(self, outcome: str): 
        desired_outcome = outcome.upper()

        facts = list()
        if desired_outcome == 'STATISTICAL MODEL': 
            raise NotImplementedError
        elif desired_outcome == 'VARIABLE RELATIONSHIP GRAPH': 
            all_vars = self.consts['variables']
            dv_const = self.consts['dv']
            main_effects = self.consts['main_effects']
            interactions = self.consts['interactions']

            for v in all_vars: 
                # Is the variable a main effect?
                if is_true(BoolVal(Contains(main_effects, Unit(v)))):
                    if v is not dv_const: 
                        facts.append(Cause(v, dv_const))
                        facts.append(Correlate(v, dv_const))
                    # Is the variable involved in an interaction?
                    # for i in interactions: 
                    #     if is_true(BoolVal(IsMember(v, i))): 

            if self.interaction_effects: 
                # TODO: Generalize this to more than 2 vars involved in an interaction
                for v0, v1 in self.interaction_effects: 
                    v0_const = None 
                    v1_const = None 
                    for v in all_vars: 
                        if v0.name == str(v): 
                            v0_const = v
                        if v1.name == str(v): 
                            v1_const = v
                    # if v0_const and v1_const: 
                    #     assert(is_true(BoolVal(IsMember(v0, ))))
                    
                    # Have found both variables involved in the interaction
                    assert(v0_const is not None)
                    assert(v1_const is not None)
                    facts.append(Cause(v0_const, v1_const))
                    facts.append(Correlate(v0_const, v1_const))

        elif desired_outcome == 'DATA SCHEMA': 
            pass
        elif desired_outcome == 'DATA COLLECTION PROCEDURE': 
            raise NotImplementedError
        else: 
            raise ValueError(f"Query is not supported: {outcome}. Try the following: 'STATISTICAL MODEL', 'VARIABLE RELATIONSHIP GRAPH', 'DATA SCHEMA', 'DATA COLLECTION PROCEDURE'")

        # import pdb; pdb.set_trace()
        return facts

    # #TODO: @return a DataSet object with data schema info only 
    # def query_data_schema(self): 
    #     ivs = self.get_all_ivs()
    #     model_facts = self.to_logical_facts()
    #     KB.query_data_schema(facts=model_facts, ivs=ivs, dv=[self.dv])


    # @property
    # def residuals(self): 
    #     raise NotImplementedError
    

    @classmethod
    def create(cls, **kwargs):
        """
        Creates a StatisticalModel according to type
        """

        global supported_model_types

        if "model_type" in kwargs.keys(): 
            mtype = kwargs["model_type"].upper()
            effect_set = kwargs['effect_set']
            assert(isinstance(effect_set, EffectSet))

            if mtype == 'LINEAR_REGRESSION':     
                return LinearRegression(effect_set)
            elif mtype == 'LOGISTIC_REGRESSION': 
                return LogisticRegression(effect_set)
            else: 
                raise ValueError(f"Model type {mtype} not supported! Try {','.join(supported_model_types)} ")
                
        else: 
            raise ValueError(f"Please specify a model type! Try {','.join(supported_model_types)} ")
    

    # TODO: May not need this (see note next to properties PIV)
    def assert_property(self, prop: str, val: Any) -> None:
        key = prop.upper()
        self.properties[key] = val


# if only main effects and numeric dv --> LinearRegression

# Should we have more tiered Model -> Regression -> LinearRegression?
        
# if main effects and interaction effects -> Regression