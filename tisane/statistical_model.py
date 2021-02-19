from tisane.concept import Concept
from tisane.variable import AbstractVariable, Nominal, Ordinal, Numeric
from tisane.effect_set import EffectSet, MainEffect, InteractionEffect, MixedEffect
from tisane.graph import Graph
from tisane.smt.knowledge_base import KB
from tisane.smt.rules import Cause, Correlate, MainEffect, NoMainEffect, Interaction, NoInteraction, NominalDataType, OrdinalDataType, NumericDataType, Transformation, NoTransformation, NumericTransformation, CategoricalTransformation, LogTransform, SquarerootTransform, LogLogTransform, ProbitTransform, LogitTransform
# from tisane.smt.query_manager import QM

from abc import abstractmethod
import pandas as pd
from typing import List, Any, Tuple

from z3 import *

# TODO: Make this an abstract class, at least in name?
class StatisticalModel(object): 
    # dv: AbstractVariable
    # main: MainEffect
    # interaction: InteractionEffect
    # mixed: MixedEffect
    # residuals: AbstractVariable
    # TODO: May not need properties since not sure what the properties would be if not the indivdiual variables or the residuals
    properties: list # list of properties that this model exhibits

    main_effects: List[AbstractVariable]
    interaction_effects: List[Tuple[AbstractVariable, ...]]
    mixed_effects: List[AbstractVariable]
    link_function: str # maybe, not sure?
    variance_function: str # maybe, not sure?

    consts: dict # Z3 consts representing the model and its DV, main_effects, etc. 

    graph : Graph # IR

    """ temp override
    @abstractmethod
    def __init__(self, effect_set: EffectSet): 
        self.dv = effect_set.get_dv()
        self.main = effect_set.get_main_effects()
        self.interaction = effect_set.get_interaction_effects()
        self.mixed = effect_set.get_mixed_effects()
    """ 

    def __init__(self, dv: AbstractVariable, main_effects: List[AbstractVariable]=None, interaction_effects: List[Tuple[AbstractVariable, ...]]=None, mixed_effects: List[AbstractVariable]=None, link_func: str=None, variance_func: str=None): 
        self.dv = dv
        
        if main_effects is not None: 
            self.main_effects = main_effects
        else: 
            self.main_effects = list()
        
        if interaction_effects is not None: 
            self.interaction_effects = interaction_effects
        else: 
            self.interaction_effects = list()
        
        if mixed_effects is not None: 
            self.mixed_effects = mixed_effects
        else: 
            self.mixed_effects = list()

        self.link_func = link_func
        self.variance_func = variance_func

        self.consts = dict()
        # self.generate_consts()

    def __str__(self): 
        dv = f"DV: {self.dv}\n"
        main_effects = f"Main effects: {self.main_effects}\n" 
        interaction_effects = f"Interaction effects: {self.interaction_effects}\n"
        mixed_effects = f"Mixed effects: {self.mixed_effects}"
        
        return dv + main_effects + interaction_effects + mixed_effects
    
    # TODO: Output mathematical version of the statistical model    
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

    # Sets interaction effects to @param main_effects
    def set_interaction_effects(self, interaction_effects: List[AbstractVariable]): 
        self.interaction_effects = interaction_effects

    # Sets mixed effects to @param mixed_effects
    def set_mixed_effects(self, mixed_effects: List[AbstractVariable]): 
        self.mixed_effects = mixed_effects
    
    # @return all variables (DV, IVs)
    def get_all_variables(self): 
        return [self.dv] + self.main_effects + self.interaction_effects + self.mixed_effects

    # @return a list containing all the IVs
    def get_all_ivs(self): 
        
        return self.main_effects + self.interaction_effects + self.mixed_effects

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
                assert(is_false(BoolVal(is_empty(tmp))))
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
        
        # Add link function 
        if self.link_func is not None: 
            raise NotImplementedError # Translate str of link function to logical fact

        # Add variance function 
        if self.variance_func is not None: 
            raise NotImplementedError

        # TODO: Add facts about variables
        variables = self.get_all_variables()
        for v in variables: 
            if isinstance(v, Nominal): 
                facts.append(NominalDataType(v.const))
            elif isinstance(v, Ordinal): 
                facts.append(OrdinalDataType(v.const))
            else: 
                assert (isinstance(v, Numeric)) 
                facts.append(NumericDataType(v.const))

        return facts
    
    # @return additional set of logical facts that needs disambiguation depending on @param desired output_obj
    def collect_ambiguous_facts(self, output: str) -> List: 
        # TODO: START HERE!
        raise NotImplementedError
    
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