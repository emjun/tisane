##### Helper functions for KnowledgeBase #####

from tisane.concept import Concept
from tisane.variable import AbstractVariable
from tisane.effect_set import EffectSet

import os 
import subprocess
import re 
from typing import List

def absolute_path(p: str) -> str:
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), p)

def format_concept_variable_constraint(concept: Concept, key: str, val: str): 
            c_name = concept.getVariableName()

            ## Variable constraints
            if key.upper() == 'DTYPE': 
                if val == 'numeric': 
                    return f'numeric({c_name}).'
                elif val =='nominal': 
                    # return f'nominal({c_name}).'
                    return f'categorical({c_name}).'
                else: 
                    # import pdb; pdb.set_trace()
                    raise NotImplementedError
            elif key.upper() == 'CARDINALITY': 
                return f'binary({c_name}).'
            else:
                # import pdb; pdb.set_trace()
                return NotImplementedError

def format_effect_set_constraint(effect_set: EffectSet, key: str, val: str): 
            ivs = list()
            for e in effect_set.get_main_effects().effect:
                e_name = e.lower().replace(' ', '_') 
                ivs.append(e_name)
            ivs_names = ','.join(ivs)

            dv_name = effect_set.get_dv().name.lower().replace(' ', '_') 
            all_names = ','.join(ivs) + f',{dv_name}'

            ## Effect set constraints
            if key.upper() == 'TOLERATE_CORRELATION': 
                if val: 
                    return f'tolerate_correlation({ivs_names}).'
                else: 
                    return f'not_tolerate_correlation({ivs_names}).'
            elif key.upper() == 'DISTRIBUTION': 
                if val == 'normal': 
                    return f'normal({ivs_names}).'
                else: 
                    raise NotImplementedError
            elif key.upper() == 'HOMOSCEDASTIC_RESIDUALS': 
                if val: 
                    return f'homoscedastic_residuals({all_names}).'
            elif key.upper() == 'NORMAL_RESIDUALS': 
                if val: 
                    return f'normal_residuals({all_names}).'

# Helper to update any logicl phrase
# Dispatch to other update methods
def update_phrase(phrase: str, effects_list: List[str]): 
    if 'XN' in phrase: 
        return update_multiples(phrase, effects_list)
    elif 'DX' in phrase:
        return update_duplicates(phrase, effects_list)
    else: # Nothing to change or update
        return phrase

# Helper to replace 'XN' with 'X0, X1, ...' to match arity of @param effects_list
def update_multiples(phrase: str, effects_list: List[str]): 
    effects_str = ','.join(effects_list)
    
    assert('XN' in phrase)
    new_phrase = phrase.replace("XN", effects_str)

    return new_phrase
# Helper to replace 'DX' phrases with duplicate facts for each 'X0', 'X1', ... to match arity of effects_list
def update_duplicates(phrase: str, effects_list: List[str]): 
    new_phrases = list()
    if 'DX' in phrase: 
        for e in effects_list: 
            new_ph = phrase.replace('DX', e)
            new_phrases.append(new_ph)
    
    return new_phrases
