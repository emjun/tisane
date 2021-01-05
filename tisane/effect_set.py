from tisane.concept import Concept

from collections import namedtuple
from typing import List


MainEffect = namedtuple('MainEffect', 'effect')
InteractionEffect = namedtuple('InteractionEffect', 'effect')
MixedEffect = namedtuple('MixedEffect', 'effect')

class EffectSet(object):
    dv: Concept
    main: MainEffect
    interaction: InteractionEffect
    mixed: MixedEffect
    properties: List

    def __init__(self, dv: Concept, main: MainEffect, interaction: InteractionEffect, mixed: MixedEffect=None): 
        self.dv = dv
        self.main = main
        self.interaction = interaction
        self.mixed = mixed

        self.properties = list() # start empty

    # def __repr__(self):
    #     return f"DV: {self.dv}, Main: {self.main}, Interaction: {self.interaction}, Mixed: {self.mixed}, properties: {self.properties}"
    
    def __str__(self):
        return str(f"DV: {self.dv}, Main: {self.main}, Interaction: {self.interaction}, Mixed: {self.mixed}, properties: {self.properties}")

    def has_dv(self, dv_name: str):
        return self.dv.name == dv_name

    def has_main(self, main_name: str):
        if self.main.effect is None:
            return main_name is None
        return main_name in self.main.effect

    def has_interaction(self, interaction_name: str):
        if self.interaction.effect is None:
            return interaction_name is None
        return interaction_name in self.interaction.effect
    
    def has_mixed(self, mixed_name: str):
        if self.mixed.effect is None:
            return mixed_name is None
        return mixed_name in self.mixed.effect
    
    # @returns dictionary with all effects and properties
    def to_dict(self): 
        main_set = None
        if self.main.effect: 
            for m in self.main.effect: 
                if not main_set: 
                    main_set = set()
                main_set.add(m)
        
        interaction_set = None
        if self.interaction.effect: 
            for i in self.interaction.effect: 
                if not interaction_set: 
                    interaction_set = set()
                interaction_set.add(i)

        mixed_set = None
        if self.mixed and self.mixed.effect: 
            for mi in self.mixed.effect: 
                if not mixed_set: 
                    mixed_set = set()
                mixed_set.add(mi)

        prop_set = None
        # TODO: update property list once have that designed!

        dict_rep = {
            'dv': self.dv.name, 
            'main': main_set, 
            'interaction': interaction_set, 
            'mixed': mixed_set
        }

        return dict_rep

    def assert_property(self, prop: str):
        pass