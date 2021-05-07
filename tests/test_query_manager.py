import tisane as ts
from tisane.statistical_model import StatisticalModel
from tisane.smt.query_manager import QM
from tisane.smt.knowledge_base import KnowledgeBase
from tisane.smt.rules import *

import unittest
from unittest.mock import patch
from unittest.mock import Mock
from z3 import *
from typing import Dict

# Declare data type
Object = DeclareSort("Object")

# Globals
iv = ts.Nominal("IV")
pid = ts.Nominal("PID")
dv = ts.Numeric("DV")
fixed_effect = FixedEffect(iv.const, dv.const)
v1 = ts.Nominal("V1")
v2 = ts.Nominal("V2")
interaction = EmptySet(Object)
interaction = SetAdd(interaction, v1.const)
interaction = SetAdd(interaction, v2.const)
interaction_effect = Interaction(interaction)
gaussian_family = GaussianFamily(dv.const)
gamma_family = GammaFamily(dv.const)


class QueryManagerTest(unittest.TestCase):
    def test_collect_rules_effects(self):
        dv = ts.Nominal("DV")
        rules = QM.collect_rules(output="effects", dv_const=dv.const)

        kb = KnowledgeBase()
        kb.ground_effects_rules(dv_const=dv.const)

        self.assertIsInstance(rules, dict)
        self.assertTrue("effects_rules" in rules.keys())
        self.assertEqual(rules["effects_rules"], kb.effects_rules)

    def test_collect_rules_family(self):
        dv = ts.Nominal("DV")
        rules = QM.collect_rules(output="FAMILY", dv_const=dv.const)

        kb = KnowledgeBase()
        kb.ground_family_rules(dv_const=dv.const)

        self.assertIsInstance(rules, dict)
        self.assertTrue("family_rules" in rules.keys())
        self.assertEqual(rules["family_rules"], kb.family_rules)

        s = Solver()
        s.add(GaussianFamily(dv.const))
        s.add(InverseGaussianFamily(dv.const))
        s.add(PoissonFamily(dv.const))
        res = s.check(rules["family_rules"])
        self.assertEqual(str(res), "unsat")

    def test_collect_rules_transformation(self):
        dv = ts.Numeric("DV")
        rules = QM.collect_rules(output="TRANSFORMATION", dv_const=dv.const)

        kb = KnowledgeBase()
        kb.ground_data_transformation_rules(dv_const=dv.const)

        self.assertIsInstance(rules, dict)
        self.assertTrue("data_transformation_rules" in rules.keys())
        self.assertEqual(
            rules["data_transformation_rules"], kb.data_transformation_rules
        )

        s = Solver()
        res = s.check(rules["data_transformation_rules"])
        self.assertEqual(str(res), "sat")

        s.add(GaussianFamily(dv.const))
        res = s.check(rules["data_transformation_rules"])
        self.assertEqual(str(res), "sat")

        s.add(IdentityTransform(dv.const))
        res = s.check(rules["data_transformation_rules"])
        self.assertEqual(str(res), "sat")

        s.add(LogTransform(dv.const))
        s.add(SquarerootTransform(dv.const))
        res = s.check(rules["data_transformation_rules"])
        self.assertEqual(str(res), "unsat")

    def test_update_clauses(self):
        global iv, dv, fixed_effect

        pushed_constraints = [NominalDataType(iv.const), NumericDataType(dv.const)]
        unsat_core = [fixed_effect, NoFixedEffect(iv.const, dv.const)]

        updated_constraints = QM.update_clauses(
            pushed_constraints=pushed_constraints,
            unsat_core=unsat_core,
            keep_clause=fixed_effect,
        )
        self.assertEqual(len(updated_constraints), 3)
        self.assertTrue(fixed_effect in updated_constraints)
        self.assertTrue(NominalDataType(iv.const) in updated_constraints)
        self.assertTrue(NumericDataType(dv.const) in updated_constraints)

    def test_update_clauses_repeated_clauses(self):
        global iv, dv, fixed_effect

        pushed_constraints = [
            fixed_effect,
            NominalDataType(iv.const),
            NumericDataType(dv.const),
        ]
        unsat_core = [fixed_effect, NoFixedEffect(iv.const, dv.const)]

        updated_constraints = QM.update_clauses(
            pushed_constraints=pushed_constraints,
            unsat_core=unsat_core,
            keep_clause=fixed_effect,
        )
        self.assertEqual(len(updated_constraints), 3)
        self.assertTrue(fixed_effect in updated_constraints)
        self.assertTrue(NominalDataType(iv.const) in updated_constraints)
        self.assertTrue(NumericDataType(dv.const) in updated_constraints)
