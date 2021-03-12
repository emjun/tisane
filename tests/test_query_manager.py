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
Object = DeclareSort('Object')

# Globals
iv = ts.Nominal('IV')
dv = ts.Numeric('DV')
fixed_effect = FixedEffect(iv.const, dv.const)
v1 = ts.Nominal('V1')
v2 = ts.Nominal('V2')
interaction = EmptySet(Object)
interaction = SetAdd(interaction, v1.const)
interaction = SetAdd(interaction, v2.const)
interaction_effect = Interaction(interaction)
gaussian_family = GaussianFamily(dv.const)
gamma_family = GammaFamily(dv.const)

class QueryManagerTest(unittest.TestCase): 

    def test_collect_rules_effects(self): 
        dv = ts.Nominal('DV')
        rules = QM.collect_rules(output='effects', dv_const=dv.const)
        
        kb = KnowledgeBase()
        kb.ground_effects_rules(dv_const=dv.const)

        self.assertIsInstance(rules, dict)
        self.assertTrue('effects_rules' in rules.keys())
        self.assertEqual(rules['effects_rules'], kb.effects_rules)

    def test_collect_rules_family(self): 
        dv = ts.Nominal('DV')
        rules = QM.collect_rules(output='FAMILY', dv_const=dv.const)
        
        kb = KnowledgeBase()
        kb.ground_family_rules(dv_const=dv.const)
        
        self.assertIsInstance(rules, dict)
        self.assertTrue('family_rules' in rules.keys())
        self.assertEqual(rules['family_rules'], kb.family_rules)

        s = Solver() 
        s.add(GaussianFamily(dv.const))
        s.add(InverseGaussianFamily(dv.const))
        s.add(PoissonFamily(dv.const))
        res = s.check(rules['family_rules'])
        self.assertEqual(str(res), 'unsat')
    
    def test_collect_rules_transformation(self): 
        dv = ts.Numeric('DV')
        rules = QM.collect_rules(output='TRANSFORMATION', dv_const=dv.const)

        kb = KnowledgeBase()
        kb.ground_data_transformation_rules(dv_const=dv.const)

        self.assertIsInstance(rules, dict)
        self.assertTrue('transformation_rules' in rules.keys())
        self.assertEqual(rules['transformation_rules'], kb.data_transformation_rules)

        s = Solver() 
        res = s.check(rules['transformation_rules'])
        self.assertEqual(str(res), 'sat')

        s.add(GaussianFamily(dv.const))
        res = s.check(rules['transformation_rules'])
        self.assertEqual(str(res), 'sat')

        s.add(IdentityTransform(dv.const))
        res = s.check(rules['transformation_rules'])
        self.assertEqual(str(res), 'sat')

        s.add(LogTransform(dv.const))
        s.add(SquarerootTransform(dv.const))
        res = s.check(rules['transformation_rules'])
        self.assertEqual(str(res), 'unsat')
    
    def test_update_clauses(self): 
        global iv, dv, fixed_effect

        pushed_constraints=[NominalDataType(iv.const), NumericDataType(dv.const)]
        unsat_core=[fixed_effect, NoFixedEffect(iv.const, dv.const)]

        updated_constraints = QM.update_clauses(pushed_constraints=pushed_constraints, unsat_core=unsat_core, keep_clause=fixed_effect)
        self.assertEqual(len(updated_constraints), 3)
        self.assertTrue(fixed_effect in updated_constraints)
        self.assertTrue(NominalDataType(iv.const) in updated_constraints)
        self.assertTrue(NumericDataType(dv.const) in updated_constraints)

    def test_update_clauses_repeated_clauses(self): 
        global iv, dv, fixed_effect

        pushed_constraints=[fixed_effect, NominalDataType(iv.const), NumericDataType(dv.const)]
        unsat_core=[fixed_effect, NoFixedEffect(iv.const, dv.const)]

        updated_constraints = QM.update_clauses(pushed_constraints=pushed_constraints, unsat_core=unsat_core, keep_clause=fixed_effect)
        self.assertEqual(len(updated_constraints), 3)
        self.assertTrue(fixed_effect in updated_constraints)
        self.assertTrue(NominalDataType(iv.const) in updated_constraints)
        self.assertTrue(NumericDataType(dv.const) in updated_constraints)

    @patch('tisane.smt.input_interface.InputInterface.resolve_unsat', return_value=fixed_effect)
    def test_check_update_constraints(self, input): 
        global iv, dv, fixed_effect

        fixed_facts = list()
        fixed_facts.append(fixed_effect)
        fixed_facts.append(NoFixedEffect(iv.const, dv.const))
        
        s = Solver()
        kb = KnowledgeBase()
        kb.ground_effects_rules(dv_const=dv.const)
        s.add(kb.effects_rules)
        (solver, assertions) = QM.check_update_constraints(solver=s, assertions=fixed_facts)
        
        self.assertEqual(len(assertions), 1)

    @patch('tisane.smt.input_interface.InputInterface.resolve_unsat', return_value=gamma_family)
    def test_check_update_constraints_family(self, input): 
        dv = ts.Nominal('DV')
        rules = QM.collect_rules(output='FAMILY', dv_const=dv.const)
        
        kb = KnowledgeBase()
        kb.ground_family_rules(dv_const=dv.const)
    
        s = Solver() 
        assertions=[GaussianFamily(dv.const), InverseGaussianFamily(dv.const), PoissonFamily(dv.const), GammaFamily(dv.const)]
        (solver, updated_assertions) = QM.check_update_constraints(solver=s, assertions=assertions)

        res = solver.check()
        self.assertEqual(str(res), 'sat')

    @patch('tisane.smt.input_interface.InputInterface.resolve_unsat', return_value=gaussian_family)
    def test_resolve_unsat_family_rules(self, input): 
        dv = ts.Nominal('DV')
        rules = QM.collect_rules(output='FAMILY', dv_const=dv.const)
        
        kb = KnowledgeBase()
        kb.ground_family_rules(dv_const=dv.const)
    
        s = Solver() 
        assertions=[GaussianFamily(dv.const), InverseGaussianFamily(dv.const), PoissonFamily(dv.const)]
        (solver, updated_assertions) = QM.check_update_constraints(solver=s, assertions=assertions)

        res = solver.check()
        self.assertEqual(str(res), 'sat')
    
    @patch('tisane.smt.input_interface.InputInterface.resolve_unsat', return_value=fixed_effect)
    def test_postprocess_to_statistical_model_fixed(self, input): 
        global iv, dv, fixed_effect

        design = ts.Design(
            dv = dv, 
            ivs = ts.Level(identifier='id', measures=[iv])
        )

        fixed_facts = list()
        fixed_facts.append(fixed_effect)
        fixed_facts.append(NoFixedEffect(iv.const, dv.const))
        
        s = Solver()
        kb = KnowledgeBase()
        kb.ground_effects_rules(dv_const=dv.const)
        s.add(kb.effects_rules)
        (solver, assertions) = QM.check_update_constraints(solver=s, assertions=fixed_facts)
        
        model = solver.model()
        updated_facts = assertions
        graph = design.graph 
        statistical_model = StatisticalModel(dv=dv) 

        sm = QM.postprocess_to_statistical_model(model=model, facts=updated_facts, graph=graph, statistical_model=statistical_model)
        self.assertEqual(sm.dv, dv)
        self.assertTrue(iv in sm.fixed_ivs)
        self.assertEqual(sm.random_slopes, list())
        self.assertEqual(sm.random_intercepts, list())
        self.assertEqual(sm.interactions, list())
        self.assertIsNone(sm.family)
        self.assertIsNone(sm.link_func)

    @patch('tisane.smt.input_interface.InputInterface.resolve_unsat', return_value=interaction_effect)
    def test_postprocess_to_statistical_model_interaction(self, input): 
        global dv, v1, v2, interaction, interaction_effect

        design = ts.Design(
            dv = dv, 
            ivs = ts.Level(identifier='id', measures=[v1, v2])
        )

        facts = list()
        facts.append(FixedEffect(v1.const, dv.const))        
        facts.append(interaction_effect)
        facts.append(NoInteraction(interaction))

        s = Solver()
        kb = KnowledgeBase()
        kb.ground_effects_rules(dv_const=dv.const)
        s.add(kb.effects_rules)
        (solver, assertions) = QM.check_update_constraints(solver=s, assertions=facts)
        
        model = solver.model()
        updated_facts = assertions
        graph = design.graph 
        statistical_model = StatisticalModel(dv=dv) 
        
        sm = QM.postprocess_to_statistical_model(model=model, facts=updated_facts, graph=graph, statistical_model=statistical_model)
        self.assertEqual(sm.dv, dv)
        self.assertTrue(v1 in sm.fixed_ivs)
        self.assertFalse(v2 in sm.fixed_ivs)
        self.assertEqual(sm.random_slopes, list())
        self.assertEqual(sm.random_intercepts, list())
        self.assertEqual([(v1, v2)], sm.interactions)
        self.assertIsNone(sm.family)
        self.assertIsNone(sm.link_func)

    # @patch('tisane.smt.input_interface.InputInterface.resolve_unsat', return_value=gaussian_family)
    # def test_postprocess_to_statistical_model_family(self, input): 
    #     global dv, v1, v2, interaction, interaction_effect, gaussian_family

    #     design = ts.Design(
    #         dv = dv, 
    #         ivs = ts.Level(identifier='id', measures=[v1, v2])
    #     )

    #     facts = list()
    #     facts.append(FixedEffect(v1.const, dv.const))        
    #     facts.append(interaction_effect)
    #     facts.append(gaussian_family)
    #     facts.append(InverseGaussianFamily(dv.const))
    #     facts.append(PoissonFamily(dv.const))
    #     facts.append(GammaFamily(dv.const))

    #     s = Solver()
    #     kb = KnowledgeBase()
    #     kb.ground_family_rules(dv_const=dv.const)
    #     s.add(kb.family_rules)
    #     (solver, assertions) = QM.check_update_constraints(solver=s, assertions=facts)
        
    #     model = solver.model()
    #     updated_facts = assertions
    #     graph = design.graph 
    #     statistical_model = StatisticalModel(dv=dv) 

        
    #     sm = QM.postprocess_to_statistical_model(model=model, facts=updated_facts, graph=graph, statistical_model=statistical_model)
    #     self.assertEqual(sm.dv, dv)
    #     self.assertTrue(v1 in sm.fixed_ivs)
    #     self.assertFalse(v2 in sm.fixed_ivs)
    #     self.assertEqual(sm.random_slopes, list())
    #     self.assertEqual(sm.random_intercepts, list())
    #     self.assertEqual([(v1, v2)], sm.interactions)
    #     self.assertEqual(sm.family, 'Gaussian')
    #     self.assertIsNone(sm.link_func)

    # @patch('tisane.smt.input_interface.InputInterface.resolve_unsat', return_value=gamma_family)
    # def test_postprocess_to_statistical_model_family_gamma(self, input): 
    #     global dv, v1, v2, interaction, interaction_effect, gamma_family

    #     design = ts.Design(
    #         dv = dv, 
    #         ivs = ts.Level(identifier='id', measures=[v1, v2])
    #     )

    #     facts = list()
    #     facts.append(FixedEffect(v1.const, dv.const))        
    #     facts.append(interaction_effect)
    #     facts.append(gaussian_family)
    #     facts.append(InverseGaussianFamily(dv.const))
    #     facts.append(PoissonFamily(dv.const))
    #     facts.append(GammaFamily(dv.const))

    #     s = Solver()
    #     kb = KnowledgeBase()
    #     kb.ground_family_rules(dv_const=dv.const)
    #     s.add(kb.family_rules)
    #     (solver, assertions) = QM.check_update_constraints(solver=s, assertions=facts)
        
    #     model = solver.model()
    #     updated_facts = assertions
    #     graph = design.graph 
    #     statistical_model = StatisticalModel(dv=dv) 

        
    #     sm = QM.postprocess_to_statistical_model(model=model, facts=updated_facts, graph=graph, statistical_model=statistical_model)
    #     self.assertEqual(sm.dv, dv)
    #     self.assertTrue(v1 in sm.fixed_ivs)
    #     self.assertFalse(v2 in sm.fixed_ivs)
    #     self.assertEqual(sm.random_slopes, list())
    #     self.assertEqual(sm.random_intercepts, list())
    #     self.assertEqual([(v1, v2)], sm.interactions)
    #     self.assertEqual(sm.family, 'Gamma')
    #     self.assertIsNone(sm.link_func)


# Ordinal
