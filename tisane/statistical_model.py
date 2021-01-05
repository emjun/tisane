from tisane.concept import Concept
from tisane.variable import AbstractVariable
from tisane.effect_set import EffectSet, MainEffect, InteractionEffect, MixedEffect

from abc import abstractmethod
import pandas as pd

from typing import Any

supported_model_types = ['LINEAR_REGRESSION', 'LOGISTIC_REGRESSION']
# TODO: Make this an abstract class?
class StatisticalModel(object): 
    dv: Concept
    main: MainEffect
    interaction: InteractionEffect
    mixed: MixedEffect
    residuals: AbstractVariable
    # TODO: May not need properties since not sure what the properties would be if not the indivdiual variables or the residuals
    properties: list # list of properties that this model exhibits

    @abstractmethod
    def __init__(self, effect_set: EffectSet): 
        self.dv = effect_set.get_dv()
        self.main = effect_set.get_main_effects()
        self.interaction = effect_set.get_interaction_effects()
        self.mixed = effect_set.get_mixed_effects()

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


# OLS is default fitting
class Regression(StatisticalModel): 
    
    def __init__(self, dv: Concept, main: list, interaction: list): 
        import pdb; pdb.set_trace()

class LinearRegression(StatisticalModel): 
    # residuals: AbstractVariable

    def __init__(self, effect_set: EffectSet):
        super().__init__(effect_set=effect_set)
        self.residuals = AbstractVariable.create(dtype='numeric')
    
    def get_residuals(self): 
        return self.residuals

class LogisticRegression(StatisticalModel): 
    # residuals: AbstractVariable

    def __init__(self, effect_set: EffectSet):
        super().__init__(effect_set=effect_set)
        self.residuals = AbstractVariable.create(dtype='numeric')
