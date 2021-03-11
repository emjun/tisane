import tisane as ts 
from tisane.smt.input_interface import InputInterface

import unittest 
from unittest.mock import patch
from unittest.mock import Mock

class InputInterfaceTest(unittest.TestCase): 
    
    @patch('tisane.smt.input_interface.InputInterface.ask_inclusion_prompt', return_value='y')
    def test_answer_inclusion_yes(self, input):
        self.assertTrue(InputInterface.ask_inclusion('subject'))

    @patch('tisane.smt.input_interface.InputInterface.ask_inclusion_prompt', return_value='n')
    def test_answer_inclusion_no(self, input):
        self.assertFalse(InputInterface.ask_inclusion('subject'))

    @patch('tisane.smt.input_interface.InputInterface.ask_multiple_choice_prompt', return_value=0)
    def test_resolve_unsat(self, input):
        fact_1 = Mock()
        fact_2 = Mock()
        facts = [fact_1, fact_2]

        ufact_1 = Mock()
        ufact_1.name = 'Unsat constraint 1'
        ufact_2 = Mock()
        ufact_2.name = 'NOT Unsat constraint 1'
        unsat_core = [ufact_1, ufact_1]

        self.assertEquals(InputInterface.resolve_unsat(facts=facts, unsat_core=unsat_core), ufact_1)