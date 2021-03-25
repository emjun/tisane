from tisane.variable import AbstractVariable
# from tisane.smt.app import add_inclusion_prompt

from typing import List, Any
import subprocess
from subprocess import DEVNULL
import os
import sys

        
class InputInterface(object): 
    
    def get_input(self): 
        pass
    
    @classmethod
    def ask_inclusion_prompt(cls, subject: str) -> bool: 

        prompt = f'Would you like to include {subject}?'
        choices = f' Y or N: '

        while True: 
            ans = input(prompt + choices)
            if ans.upper() == 'Y': 
                return ans.upper()
            elif ans.upper() == 'N': 
                return ans.upper()
            else: 
                pass
    
    @classmethod
    def ask_inclusion(cls, subject: str) -> bool: 
    
        ans = cls.ask_inclusion_prompt(subject)

        if ans.upper() == 'Y':
            # TODO: write to a file here 
            return True
        elif ans.upper() == 'N': 
            return False
        else: 
            pass
    
    # TODO: Format the interactions to be more readable
    @classmethod 
    def format_options(cls, options: List) -> List: 
        return options

    @classmethod
    def ask_multiple_choice_prompt(cls, options: List) -> Any: 
        prompt = f'These cannot be true simultaneously.'
        formatted_options = cls.format_options(options)
        choices = f' Pick index (starting at 0) to select option in: {formatted_options}: '
        while True: 
            idx = int(input(prompt + choices))
            # st.write()

            if idx in range(len(options)): 
                # only keep the constraint that is selected. 
                constraint = options[idx] 
                print(f'Ok, going to add {constraint} and remove the others.')
                return idx
            else:
                print(f'Pick a value in range')
                pass
    
    @classmethod
    def resolve_unsat(cls, facts: List, unsat_core: List) -> List: 
        idx = cls.ask_multiple_choice_prompt(options=unsat_core)
    
        return unsat_core[idx]

    # TODO: Format options for specifying family of a distribution
    @classmethod
    def format_family(cls, options: List): 
        return options
    
    @classmethod
    def ask_family_prompt(cls, options: List, dv: AbstractVariable): 
        prompt = f'Which distribution best approximates your dependent variable {dv}?'
        formatted_options = cls.format_options(options)
        choices = f' Pick index (starting at 0) to select option in: {formatted_options}: '

        while True: 
            idx = int(input(prompt + choices))

            if idx in range(len(options)): 
                # only keep the constraint that is selected. 
                constraint = options[idx] 
                print(f'Ok, going to add {constraint} and remove the others.')
                return idx
            else:
                print(f'Pick a value in range')
                pass
    
    @classmethod
    def ask_family(cls, options: List, dv: AbstractVariable): 
        idx = cls.ask_family_prompt(options=options, dv=dv)

        return options[idx]

    @classmethod
    def ask_link_prompt(cls, options: List, dv: AbstractVariable): 
        prompt = f'W'


    @classmethod
    def ask_link(cls, options: List, dv: AbstractVariable): 
        idx = cls.ask_link_prompt(options=options, dv=dv)

        return options[idx]

    # @classmethod
    # def ask_change_default_prompt(cls, subject: str, default: str, options: List): 
    #     prompt = f'The default {subject} is {default}. Would you like to change it to one of {options}?'

    # @classmethod
    # def ask_change_default(cls, subject: str, default: str, options: List): 
    #     idx = cls.ask_change_default_prompt(subject=subject, default=default, options=options)
    #     pass