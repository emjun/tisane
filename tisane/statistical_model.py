from tisane.concept import Concept
from tisane.variable import AbstractVariable
from tisane.effect_set import EffectSet, MainEffect, InteractionEffect, MixedEffect
from tisane.graph import Graph
from tisane.smt.knowledge_base import KB
from tisane.smt.rules import Models, Dependent, Cause, Correlate
from tisane.smt.query_manager import QM

from abc import abstractmethod
import pandas as pd
from typing import List, Any, Tuple

from z3 import *

# TODO: Make this an abstract class?
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


    """ temp override
    @abstractmethod
    def __init__(self, effect_set: EffectSet): 
        self.dv = effect_set.get_dv()
        self.main = effect_set.get_main_effects()
        self.interaction = effect_set.get_interaction_effects()
        self.mixed = effect_set.get_mixed_effects()
    """ 

    def __init__(self, dv: str, main_effects: List[str], interaction_effects: List[Tuple[str, ...]], mixed_effects: List[str], link: str, variance: str): 
        self.dv = AbstractVariable(name=dv)
        
        self.main_effects = list()
        for m in main_effects: 
            self.main_effects.append(AbstractVariable(name=m.upper()))
        
        self.interaction_effects = list()
        for i in interaction_effects: 
            var_list = list()
            # i is a Tuple of variable names
            for v in i: 
                # import pdb; pdb.set_trace()
                var_list.append(AbstractVariable(name=v.upper())) 
            self.interaction_effects.append(tuple(var_list))
        
        self.mixed_effects = list()
        for mi in mixed_effects: 
            self.mixed_effects.append(AbstractVariable(name=mi.upper()))

        self.link = link 
        self.variance = variance

        self.consts = dict()
        self.generate_consts()

    # @return a list containing all the IVs
    def get_all_ivs(self): 
        
        return self.main_effects + self.interaction_effects + self.mixed_effects

    # @return Z3 consts for variables in model
    def generate_consts(self): 
        # Declare data type
        Object = DeclareSort('Object')

        # Create Z3 const objects for DV, Main effects
        var_consts = list()
        dv_name = self.dv.name
        dv_const = Const(dv_name, Object)
        var_consts.append(dv_const) # create and add Z3 const object for DV
        self.consts['dv'] = dv_const
        
        # Create and add Z3 consts for all main effects
        main_effects = self.main_effects
        main_seq = None
        if len(self.main_effects) > 0: 
            for me in main_effects: 
                name = me.name
                me_const = Const(name, Object) # create a Z3 object
                var_consts.append(me_const) # add each object 
                # Have we created a sequence of IVs yet?
                # If not, create one
                if main_seq is None: # Cannot use idiom with Z3 Exprs: if not ivs_seq
                    # set first Unit of sequence
                    main_seq = Unit(me_const)
                # We already created a sequence of IVs
                else: 
                    # concatenate
                    main_seq = Concat(Unit(me_const), main_seq)
        # import pdb; pdb.set_trace()
        self.consts['main_effects'] = main_seq

        # Create and add Z3 consts for Interaction effects
        interactions_seq = None
        if len(self.interaction_effects) > 0: 
            for ixn in self.interaction_effects: 
                tmp = EmptySet(Object)
                # For each interaction tuple
                for v in ixn: 
                    # find the Z3 const that represents this variable
                    ixn_v_const = None
                    # import pdb; pdb.set_trace()
                    for v_const in facts['main_effects']:
                        if v.name == str(v_const): 
                            ixn_v_const = v_const
                            break
                    # If the variable does not exist in main effects (possible though unlikely)
                    if ixn_v_const is None: 
                        # Create a new const!
                        ixn_v_const = Const(v.name, Object)
                    # Create a Z3 set for each interaction tuple
                    tmp = SetAdd(tmp, ixn_v_const)
                # Do we already have a sequence we're building onto?
                if interactions_seq is None: 
                    # Create a sequence
                    interactions_seq = Unit(tmp)
                else: 
                    # Add to an existing sequence
                    interactions_seq = Concat(Unit(tmp), interactions_seq)
        self.consts['interactions'] = interactions_seq

        self.consts['variables'] = var_consts
        
    # @return a list of facts to use when querying the knowledge base
    def to_logical_facts(self): 
        facts = dict()

        dv_const = self.consts['dv']
        main_effects = self.consts['main_effects']
        interactions = self.consts['interactions']
        
        # Add model fact
        facts['model_explanation'] = [Models(dv_const, main_effects), Dependent(dv_const)]

        # TODO: Add fact about link function
        #facts.append(f'link({dv_name}, {self.link}).')

        # TODO: Add fact about variance function
        #facts.append(f'variance({dv_name}, {self.variance}).')

        # TODO: Add facts about variables

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
                    # TODO: check about interactions
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

    # Output mathematical version of the statistical model
    def __str__(self): 
        raise NotImplementedError
    

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