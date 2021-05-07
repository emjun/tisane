from tisane.concept import Concept

from collections import namedtuple
from typing import Any, List


MainEffect = namedtuple("MainEffect", "effect")
InteractionEffect = namedtuple("InteractionEffect", "effect")
MixedEffect = namedtuple("MixedEffect", "effect")


class EffectSet(object):
    dv: Concept
    main: MainEffect
    interaction: InteractionEffect
    mixed: MixedEffect
    properties: dict

    def __init__(
        self,
        dv: Concept,
        main: MainEffect,
        interaction: InteractionEffect,
        mixed: MixedEffect = None,
    ):
        self.dv = dv
        self.main = main
        self.interaction = interaction
        self.mixed = mixed

        self.properties = dict()  # start empty

    # def __repr__(self):
    #     return f"DV: {self.dv}, Main: {self.main}, Interaction: {self.interaction}, Mixed: {self.mixed}, properties: {self.properties}"

    # TODO: Maybe the Effect Set should have a mathematical representation (not the StatisticalModel?)
    def __str__(self):
        return str(
            f"DV: {self.dv}, Main: {self.main}, Interaction: {self.interaction}, Mixed: {self.mixed}, properties: {self.properties}"
        )

    """
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
    """

    def has_dv(self):
        if not self.dv:
            return True

        return False

    def has_main_effects(self):
        if not self.main:
            return False
        if self.main:  # because there's a bug
            if not self.main.effect:
                return False
        return True

    def has_interaction_effects(self):
        if not self.interaction:
            return False
        if self.interaction:  # because there's a bug
            if not self.interaction.effect:
                return False
        return True

    def has_mixed_effects(self):
        if not self.mixed:
            return False
        if self.mixed:  # because there's a bug
            if not self.mixed.effect:
                return False
        return True

    def get_dv(self):
        return self.dv

    def get_main_effects(self):
        return self.main

    def get_interaction_effects(self):
        return self.interaction

    def get_mixed_effects(self):
        return self.mixed

    # def get_all_iv_effects(self):
    #     for m in self.get_main_effects().effect:
    #

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
            "dv": self.dv.name,
            "main": main_set,
            "interaction": interaction_set,
            "mixed": mixed_set,
        }

        return dict_rep

    def assert_property(self, prop: str, val: Any) -> None:
        key = prop.upper()
        self.properties[key] = val

    # @returns if effect set has properties to assert
    def has_assertions(self) -> bool:
        return bool(self.properties)

    # @returns effect set properties
    def get_assertions(self) -> dict:
        return self.properties
