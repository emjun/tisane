import tisane as ts 
from tisane.variable import Treatment, Has, RepeatedMeasure, Nest
from tisane.random_effects import RandomSlope, RandomIntercept
from tisane.smt.rules import *
from tisane.smt.input_interface import InputInterface
from tisane.smt.synthesizer import Synthesizer
from tisane.code_generator import *

import unittest
from unittest.mock import patch
from unittest.mock import Mock
import pytest
from random import randrange

# Globals
iv = ts.Nominal('IV')
pid = ts.Nominal('PID')
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

def absolute_path(p: str) -> str:
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), p)

class SynthesizerTest(unittest.TestCase): 

    def test_generate_main_effects_all_in_query_1(self):
        dv = ts.Numeric('DV')
        v1 = ts.Nominal('V1')
        pid = ts.Nominal('PID') 

        # Conceptual relationships
        v1.causes(dv)
        # Data measurement relationships
        pid.has(v1)

        design = ts.Design(
            dv = dv, 
            ivs = [v1]
        )

        synth = Synthesizer()
        self.assertTrue(len(v1.relationships), 1)
        me_candidates = synth.generate_main_effects_from_graph(design.graph, design.ivs, design.dv)
        self.assertIsInstance(me_candidates, dict)
        self.assertIsInstance(me_candidates['input'], list)
        self.assertEqual(len(me_candidates['input']), 1)
        input_vars = [i.name for i in me_candidates['input']]
        self.assertTrue(v1.name in input_vars)
        self.assertEqual(len(me_candidates['derived_direct']), 0)
        self.assertEqual(len(me_candidates['derived_transitive']), 0)

    def test_generate_main_effects_all_in_query_2(self):
        dv = ts.Numeric('DV')
        v1 = ts.Nominal('V1')
        v2 = ts.Nominal('V2')
        pid = ts.Nominal('PID') 

        # Conceptual relationships
        v1.causes(dv)
        v2.causes(dv)
        # Data measurement relationships
        pid.has(v1)
        pid.has(v2)

        design = ts.Design(
            dv = dv, 
            ivs = [v1, v2]
        )

        synth = Synthesizer()
        self.assertTrue(len(v1.relationships), 1)
        me_candidates = synth.generate_main_effects_from_graph(design.graph, design.ivs, design.dv)
        self.assertIsInstance(me_candidates, dict)
        self.assertIsInstance(me_candidates['input'], list)
        self.assertEqual(len(me_candidates['input']), 2)
        input_vars = [i.name for i in me_candidates['input']]
        self.assertTrue(v1.name in input_vars)
        self.assertTrue(v2.name in input_vars)
        self.assertEqual(len(me_candidates['derived_direct']), 0)
        self.assertEqual(len(me_candidates['derived_transitive']), 0)

    def test_generate_main_effects_infer_direct(self):
        dv = ts.Numeric('DV')
        v1 = ts.Nominal('V1')
        v2 = ts.Nominal('V2')
        v3 = ts.Nominal('V3')
        pid = ts.Nominal('PID') 

        # Conceptual relationships
        v1.causes(dv)
        v2.causes(dv)
        v3.causes(dv)
        # Data measurement relationships
        pid.has(v1)
        pid.has(v2)

        design = ts.Design(
            dv = dv, 
            ivs = [v1, v2]
        )

        synth = Synthesizer()
        self.assertTrue(len(v1.relationships), 1)
        me_candidates = synth.generate_main_effects_from_graph(design.graph, design.ivs, design.dv)
        self.assertIsInstance(me_candidates, dict)
        self.assertIsInstance(me_candidates['input'], list)
        self.assertEqual(len(me_candidates['input']), 2)
        input_vars = [i.name for i in me_candidates['input']]
        self.assertTrue(v1.name in input_vars)
        self.assertTrue(v2.name in input_vars)
        self.assertEqual(len(me_candidates['derived_direct']), 1)
        derived_vars = [v.name for v in me_candidates['derived_direct']]
        self.assertTrue(v3.name in derived_vars)
        self.assertEqual(len(me_candidates['derived_transitive']), 0)

    def test_generate_main_effects_infer_transitive_1(self):
        dv = ts.Numeric('DV')
        v1 = ts.Nominal('V1')
        v2 = ts.Nominal('V2')
        v3 = ts.Nominal('V3')
        pid = ts.Nominal('PID') 

        # Conceptual relationships
        v1.causes(dv)
        v2.causes(dv)
        v3.causes(v1)
        # Data measurement relationships
        pid.has(v1)
        pid.has(v2)

        design = ts.Design(
            dv = dv, 
            ivs = [v1, v2]
        )

        synth = Synthesizer()
        self.assertTrue(len(v1.relationships), 1)
        me_candidates = synth.generate_main_effects_from_graph(design.graph, design.ivs, design.dv)
        self.assertIsInstance(me_candidates, dict)
        self.assertIsInstance(me_candidates['input'], list)
        self.assertEqual(len(me_candidates['input']), 2)
        input_vars = [i.name for i in me_candidates['input']]
        self.assertTrue(v1.name in input_vars)
        self.assertTrue(v2.name in input_vars)
        self.assertEqual(len(me_candidates['derived_direct']), 0)
        self.assertEqual(len(me_candidates['derived_transitive']), 1)
        trans_vars = [v.name for v in me_candidates['derived_transitive']]
        self.assertTrue(v3.name in trans_vars)

    def test_generate_main_effects_infer_transitive_2(self):
        dv = ts.Numeric('DV')
        v1 = ts.Nominal('V1')
        v2 = ts.Nominal('V2')
        v3 = ts.Nominal('V3')
        pid = ts.Nominal('PID') 

        # Conceptual relationships
        v1.causes(dv)
        v2.causes(dv)
        v3.causes(v1)
        v3.causes(v2)
        # Data measurement relationships
        pid.has(v1)
        pid.has(v2)
        pid.has(v3)

        design = ts.Design(
            dv = dv, 
            ivs = [v1, v2]
        )

        synth = Synthesizer()
        self.assertTrue(len(v1.relationships), 1)
        me_candidates = synth.generate_main_effects_from_graph(design.graph, design.ivs, design.dv)
        self.assertIsInstance(me_candidates, dict)
        self.assertIsInstance(me_candidates['input'], list)
        self.assertEqual(len(me_candidates['input']), 2)
        input_vars = [i.name for i in me_candidates['input']]
        self.assertTrue(v1.name in input_vars)
        self.assertTrue(v2.name in input_vars)
        self.assertEqual(len(me_candidates['derived_direct']), 0)
        self.assertEqual(len(me_candidates['derived_transitive']), 1)
        trans_vars = [v.name for v in me_candidates['derived_transitive']]
        self.assertTrue(v3.name in trans_vars)

    def test_generate_interaction_effects_1(self):
        dv = ts.Numeric('DV')
        v1 = ts.Nominal('V1')
        v2 = ts.Nominal('V2')
        pid = ts.Nominal('PID') 

        # Conceptual relationships
        v1.causes(dv)
        v2.causes(dv)
        # Data measurement relationships
        pid.has(v1)
        pid.has(v2)

        design = ts.Design(
            dv = dv, 
            ivs = [v1, v2]
        )

        synth = Synthesizer()
        self.assertTrue(len(v1.relationships), 1)
        ixn_candidates = synth.generate_interaction_effects_from_graph(design.graph, design.ivs, design.dv)
        two_way = ixn_candidates['two-way']
        n_way = ixn_candidates['n-way']
        self.assertIsInstance(two_way, list)
        self.assertIsInstance(n_way, list)
        self.assertEqual(len(two_way), 1)
        self.assertEqual(len(n_way), 0)
        self.assertTrue((v1, v2) in two_way)
    
    def test_generate_interaction_effects_2(self):
        dv = ts.Numeric('DV')
        v1 = ts.Nominal('V1')
        v2 = ts.Nominal('V2')
        v3 = ts.Nominal('V3')
        pid = ts.Nominal('PID') 

        # Conceptual relationships
        v1.causes(dv)
        v2.causes(dv)
        v3.causes(dv)
        # Data measurement relationships
        pid.has(v1)
        pid.has(v2)
        pid.has(v3)

        design = ts.Design(
            dv = dv, 
            ivs = [v1, v2, v3]
        )

        synth = Synthesizer()
        self.assertTrue(len(v1.relationships), 1)
        ixn_candidates = synth.generate_interaction_effects_from_graph(design.graph, design.ivs, design.dv)
        two_way = ixn_candidates['two-way']
        n_way = ixn_candidates['n-way']
        self.assertIsInstance(two_way, list)
        self.assertIsInstance(n_way, list)
        self.assertEqual(len(two_way), 3)
        self.assertEqual(len(n_way), 1)
        self.assertTrue((v1, v2) in two_way)
        self.assertTrue((v2, v3) in two_way)
        self.assertTrue((v1, v3) in two_way)
        self.assertTrue((v1, v2, v3) in n_way)

    def test_generate_random_effects(self): 
        pass

    def test_create_statistical_model(self):
        rt = ts.Time('Resp')
        condition = ts.Nominal('Cond', cardinality=2) # A or B
        item = ts.Nominal('ItemID', cardinality=2) # 1, 2, 3, or 4
        subject = ts.Nominal('SubjID', cardinality=24) # 24 subjects


        # Conceptual relationship
        condition.associates_with(rt)
        # Data measurement
        item.has_unique(condition) # condition is treated to each item
        condition.treat(subject, num_assignments=2) # subjects see two conditions

        design = ts.Design(
                    dv = rt,
                    ivs = [condition]
                )

        f = open('./tests/test_model_json/test_model.json', 'r') 
        model_json = f.read()

        synth = Synthesizer()
        
        sm = synth.create_statistical_model(model_json, design)
        
        self.assertEqual(len(sm.fixed_ivs), 1)
        self.assertTrue(condition in sm.fixed_ivs)
        self.assertEqual(len(sm.interactions), 0)
        self.assertEqual(len(sm.random_ivs), 3)
        
        rs = RandomSlope(condition, subject)
        ri_item = RandomIntercept(item)
        ri_subject = RandomIntercept(subject)
        for re in sm.random_ivs: 
            if isinstance(re, RandomSlope): 
                self.assertEqual(re.iv, rs.iv)
                self.assertEqual(re.groups, rs.groups)
            elif isinstance(re, RandomIntercept): 
                self.assertTrue(re.groups == ri_subject.groups or re.groups == ri_item.groups)

    # def test_generate_code_for_statistical_model(self):
    #     rt = ts.Time('Resp')
    #     condition = ts.Nominal('Cond', cardinality=2) # A or B
    #     item = ts.Nominal('ItemID', cardinality=2) # 1, 2, 3, or 4
    #     subject = ts.Nominal('SubjID', cardinality=24) # 24 subjects

    #     # Conceptual relationship
    #     condition.associates_with(rt)
    #     # Data measurement
    #     item.has_unique(condition) # condition is treated to each item
    #     condition.treat(subject, num_assignments=2) # subjects see two conditions

    #     design = ts.Design(
    #                 dv = rt,
    #                 ivs = [condition]
    #             )

    #     f = open('./tests/test_model_json/test_model.json', 'r') 
    #     model_json = f.read()

    #     synth = Synthesizer()
        
    #     sm = synth.create_statistical_model(model_json, design)
    #     data_path = 'test_data/wbsi_24.csv'
    #     data_abs = absolute_path(data_path)
    #     sm.assign_data(data_abs)
    #     generate_code(sm)
    #     import pdb; pdb.set_trace()


    def test_generate_fixed_candidates_cycle(self): 
        dv = ts.Numeric('DV')
        x1 = ts.Nominal('x1', cardinality=2)
        x2 = ts.Nominal('x2', cardinality=2)
        x3 = ts.Numeric('x3')

        x1.cause(dv)
        x2.associates_with(dv)
        x3.associates_with(x2)
        # x3.cause(x1)

        design = ts.Design(
            dv=dv, 
            ivs=[x1, x2, x3]
        )

        synth = Synthesizer() 
        
        error = False
        try: 
            candidates = synth._generate_fixed_candidates(design)
        
        except: 
            error = True 
        self.assertTrue(error)            

    def test_reduce_before_generate_fixed_candidates_cycle(self):
        dv = ts.Numeric('DV')
        x1 = ts.Nominal('x1', cardinality=2)
        x2 = ts.Nominal('x2', cardinality=2)
        x3 = ts.Numeric('x3')

        x1.cause(dv)
        x2.associates_with(dv)
        x3.associates_with(x2)
        # x3.cause(x1)

        design = ts.Design(
            dv=dv, 
            ivs=[x1, x2, x3]
        )

        synth = Synthesizer() 

        error = False
        try: 
            candidates = synth._generate_fixed_candidates_from_graph(design.graph, design.ivs, design.dv)

        except: 
            error = True
        self.assertFalse(error)

    def test_transform_treatment_to_has(self): 
        pid = ts.Nominal('pid')
        acc = ts.Numeric('accuracy')
        expl = ts.Nominal('explanation type')
        variables = [acc, expl]

        # Data measurement relationships
        expl.treats(pid)

        design = ts.Design(
            dv = acc, 
            ivs = [expl]
        )

        # Pre-transformation 
        gr = design.graph
        self.assertEqual(len(gr.get_edges()), 1)
        self.assertTrue(gr.has_edge(expl, pid, 'treat'))
        (n0, n1, edge_data) = gr.get_edge(expl, pid, 'treat')
        self.assertIsInstance(edge_data['edge_obj'], Treatment)

        synth = Synthesizer() 
        updated_gr = synth.transform_to_has_edges(gr)

        # Post-transformation 
        self.assertEqual(len(updated_gr.get_edges()), 2)
        self.assertTrue(updated_gr.has_edge(pid, expl, 'has'))
        (n0, n1, edge_data) = updated_gr.get_edge(pid, expl, 'has')
        self.assertIsInstance(edge_data['edge_obj'], Treatment)
        
    def test_transform_nest_to_has(self): 
        student = ts.Nominal('student id')
        school = ts.Nominal('school') 
        age = ts.Numeric('age')
        math = ts.Numeric('math score')

        age.associates_with(math) # Introduces 2 edges (bidirectional)

        student.has(age)
        student.nest_under(school)

        design = ts.Design(
            dv=math, 
            ivs=[age]
        )

        # Pre-transformation 
        gr = design.graph
        self.assertEqual(len(gr.get_edges()), 4)
        self.assertTrue(gr.has_edge(student, school, 'nest'))
        (n0, n1, edge_data) = gr.get_edge(student, school, 'nest')
        self.assertIsInstance(edge_data['edge_obj'], Nest)

        synth = Synthesizer() 
        updated_gr = synth.transform_to_has_edges(gr)

        # Post-transformation
        self.assertEqual(len(updated_gr.get_edges()), 5)
        self.assertTrue(updated_gr.has_edge(student, school, 'nest'))
        self.assertTrue(updated_gr.has_edge(school, student, 'has'))
        (n0, n1, edge_data) = updated_gr.get_edge(school, student, 'has')
        self.assertIsInstance(edge_data['edge_obj'], Nest)

    def test_transform_repeat_to_has(self): 
        pig = ts.Nominal('pig id', cardinality=24) # 24 pigs
        time = ts.Nominal('week number')
        weight = ts.Numeric('weight')

        pig.repeats(weight, according_to=time) 

        design = ts.Design(
            dv = weight,
            ivs = [time]
        )

        # Pre-transformation 
        gr = design.graph
        self.assertEqual(len(gr.get_edges()), 1)
        self.assertTrue(gr.has_edge(pig, weight, 'repeat'))
        (n0, n1, edge_data) = gr.get_edge(pig, weight, 'repeat')
        self.assertIsInstance(edge_data['edge_obj'], RepeatedMeasure)

        synth = Synthesizer() 
        updated_gr = synth.transform_to_has_edges(gr)

        # Post-transformation 
        self.assertEqual(len(updated_gr.get_edges()), 5) # Has + Associate (introduces 3 edges)
        self.assertTrue(updated_gr.has_edge(pig, weight, 'repeat'))
        self.assertTrue(updated_gr.has_edge(pig, weight, 'has'))
        (n0, n1, edge_data) = updated_gr.get_edge(pig, weight, 'has')
        self.assertTrue(updated_gr.has_edge(time, pig, 'has'))
        (n0, n1, edge_data) = updated_gr.get_edge(time, pig, 'has')
        self.assertIsInstance(edge_data['edge_obj'], RepeatedMeasure)
        self.assertEqual(edge_data['repetitions'], pig.cardinality)

        self.assertTrue(updated_gr.has_edge(time, weight, 'associate'))
        self.assertTrue(updated_gr.has_edge(weight, time, 'associate')) 
        

    def test_transform_repeat_to_has_2(self): 
        pig = ts.Nominal('pig id', cardinality=24) # 24 pigs
        time = ts.Nominal('week number')
        weight = ts.Numeric('weight')

        time.associates_with(weight)
        pig.repeats(weight, according_to=time) 

        design = ts.Design(
            dv = weight,
            ivs = [time]
        )

        # Pre-transformation 
        gr = design.graph
        self.assertEqual(len(gr.get_edges()), 3)
        self.assertTrue(gr.has_edge(pig, weight, 'repeat'))
        (n0, n1, edge_data) = gr.get_edge(pig, weight, 'repeat')
        self.assertIsInstance(edge_data['edge_obj'], RepeatedMeasure)
        self.assertTrue(gr.has_edge(time, weight, 'associate'))
        self.assertTrue(gr.has_edge(weight, time, 'associate'))

        synth = Synthesizer() 
        updated_gr = synth.transform_to_has_edges(gr)

        # Post-transformation 
        self.assertEqual(len(updated_gr.get_edges()), 5) # Has + Associate (introduces 3 edges)
        self.assertTrue(updated_gr.has_edge(pig, weight, 'repeat'))
        self.assertTrue(updated_gr.has_edge(pig, weight, 'has'))
        (n0, n1, edge_data) = updated_gr.get_edge(pig, weight, 'has')
        self.assertTrue(updated_gr.has_edge(time, pig, 'has'))
        (n0, n1, edge_data) = updated_gr.get_edge(time, pig, 'has')
        self.assertIsInstance(edge_data['edge_obj'], RepeatedMeasure)
        self.assertEqual(edge_data['repetitions'], pig.cardinality)

        self.assertTrue(updated_gr.has_edge(time, weight, 'associate'))
        self.assertTrue(updated_gr.has_edge(weight, time, 'associate')) 

    def test_transform_repeat_to_has_3(self): 
        pig = ts.Nominal('pig id', cardinality=24) # 24 pigs
        time = ts.Nominal('week number', cardinality=12) # 12 weeks
        weight = ts.Numeric('weight')

        time.causes(weight)
        pig.repeats(weight, according_to=time) 

        design = ts.Design(
            dv = weight,
            ivs = [time]
        )

        # Pre-transformation 
        gr = design.graph
        self.assertEqual(len(gr.get_edges()), 2)
        self.assertTrue(gr.has_edge(pig, weight, 'repeat'))
        (n0, n1, edge_data) = gr.get_edge(pig, weight, 'repeat')
        self.assertIsInstance(edge_data['edge_obj'], RepeatedMeasure)
        self.assertTrue(gr.has_edge(time, weight, 'cause'))

        synth = Synthesizer() 
        updated_gr = synth.transform_to_has_edges(gr)

        # Post-transformation 
        self.assertEqual(len(updated_gr.get_edges()), 6) # Has + Associate (introduces 3 edges)
        self.assertTrue(updated_gr.has_edge(pig, weight, 'repeat'))
        self.assertTrue(updated_gr.has_edge(pig, weight, 'has'))
        (n0, n1, edge_data) = updated_gr.get_edge(pig, weight, 'has')
        self.assertEqual(edge_data['repetitions'], time.cardinality)
        self.assertTrue(updated_gr.has_edge(time, pig, 'has'))
        (n0, n1, edge_data) = updated_gr.get_edge(time, pig, 'has')
        self.assertIsInstance(edge_data['edge_obj'], RepeatedMeasure)
        self.assertEqual(edge_data['repetitions'], pig.cardinality)

        self.assertTrue(updated_gr.has_edge(time, weight, 'cause'))
        self.assertTrue(updated_gr.has_edge(time, weight, 'associate')) 
        self.assertTrue(updated_gr.has_edge(weight, time, 'associate')) 

    def test_reduce_graph(self):
        v1 = ts.Numeric('V1')
        v2 = ts.Numeric('V2')
        v3 = ts.Numeric('V3')

        gr = ts.Graph()
        gr.cause(v1, v2)
        gr.associate(v2, v3)

        v1.has(v2)
        has_obj = v1.relationships[0]
        self.assertIsInstance(has_obj, Has)
        gr.has(v1, v2, has_obj, 1)

        synth = Synthesizer()
        sub_gr = gr.get_conceptual_subgraph()
        reduced_gr = synth.reduce_graph(sub_gr, v2)
        self.assertEqual(len(reduced_gr.get_edges()), 2)


    # @patch("tisane.smt.input_interface.InputInterface.resolve_unsat")
    # @patch('tisane.smt.input_interface.InputInterface.ask_inclusion')
    # def test_generate_and_select_effects_sets_from_design_fixed_only(self, mock_increment0, mock_increment1): 
    #     dv = ts.Numeric('DV')
    #     v1 = ts.Nominal('V1')

    #     # Simulate end-user selecting between two options at a time repeatedly
    #     mock_increment0.side_effect = ['y']
    #     mock_increment1.side_effect = [FixedEffect(v1.const, dv.const)]

    #     # Conceptual relationships
    #     v1.causes(dv)
    #     # Data measurement relationships
    #     pid.has(v1)

    #     design = ts.Design(
    #         dv = dv, 
    #         ivs = [v1]
    #     )

    #     synth = Synthesizer()
    #     self.assertTrue(len(v1.relationships), 1)
    #     sm = synth.generate_and_select_effects_sets_from_design(design=design)
    #     self.assertTrue(v1 in sm.fixed_ivs)
    #     self.assertEqual(sm.interactions, list())
    #     self.assertEqual(sm.random_ivs, list())
    #     self.assertIsNone(sm.family)
    #     self.assertIsNone(sm.link_function)
    
    # @patch("tisane.smt.input_interface.InputInterface.resolve_unsat")
    # @patch('tisane.smt.input_interface.InputInterface.ask_inclusion')
    # def test_generate_and_select_effects_sets_from_design_fixed_interaction(self, mock_increment0, mock_increment1): 
    #     dv = ts.Numeric('DV')
    #     v1 = ts.Nominal('V1')
    #     v2 = ts.Nominal('V2')
        
    #     # Simulate end-user selecting between two options at a time repeatedly
    #     mock_increment0.side_effect = ['y', 'y']
    #     interaction_set = EmptySet(Object)
    #     interaction_set = SetAdd(interaction_set, v1.const)
    #     interaction_set = SetAdd(interaction_set, v2.const)
    #     interaction = Unit(interaction_set)
    #     mock_increment1.side_effect = [FixedEffect(v1.const, dv.const), FixedEffect(v2.const, dv.const), Interaction(interaction_set)]

    #     # Conceptual relationships
    #     v1.causes(dv)
    #     v2.causes(dv)
    #     # Data measurement relationships
    #     pid.has(v1)
    #     pid.has(v2)

    #     design = ts.Design(
    #         dv = dv, 
    #         ivs = [v1, v2]
    #     )

    #     synth = Synthesizer()
    #     sm = synth.generate_and_select_effects_sets_from_design(design=design)
    #     self.assertTrue(v1 in sm.fixed_ivs)
    #     self.assertTrue((v1, v2) in sm.interactions)
    #     self.assertEqual(sm.random_ivs, list())
    #     self.assertIsNone(sm.family)
    #     self.assertIsNone(sm.link_function)
    
    # @patch("tisane.smt.input_interface.InputInterface.resolve_unsat")
    # @patch('tisane.smt.input_interface.InputInterface.ask_inclusion')
    # def test_generate_and_select_effects_sets_from_design_random(self, mock_increment0, mock_increment1): 
    #     dv = ts.Numeric('DV')
    #     v1 = ts.Nominal('V1')
    #     v2 = ts.Nominal('V2')
        
    #     # Simulate end-user selecting between two options at a time repeatedly
    #     mock_increment0.side_effect = ['y', 'y']
    #     interaction_set = EmptySet(Object)
    #     interaction_set = SetAdd(interaction_set, v1.const)
    #     interaction_set = SetAdd(interaction_set, v2.const)
    #     interaction = Unit(interaction_set)
    #     mock_increment1.side_effect = [FixedEffect(v1.const, dv.const), FixedEffect(v2.const, dv.const), Interaction(interaction_set)]

    #     # Conceptual relationships
    #     v1.causes(dv)
    #     v2.causes(dv)
    #     # Data measurement relationships
    #     pid.has(v1)
    #     pid.has(v2)

    #     design = ts.Design(
    #         dv = dv, 
    #         ivs = [v1, v2]
    #     )

    #     synth = Synthesizer()
    #     sm = synth.generate_and_select_effects_sets_from_design(design=design)
    #     self.assertTrue(v1 in sm.fixed_ivs)
    #     self.assertTrue((v1, v2) in sm.interactions)
    #     self.assertEqual(sm.random_ivs, list())
    #     self.assertIsNone(sm.family)
    #     self.assertIsNone(sm.link_function)
    
    # def test_generate_family_numeric_dv(self): 
    #     global gaussian_family, gamma_family

    #     dv = ts.Numeric('DV')
    #     v1 = ts.Nominal('V1')
    #     v2 = ts.Nominal('V2')

    #     inverse_gaussian_family = InverseGaussianFamily(dv.const)
    #     poisson_family = PoissonFamily(dv.const)
        
    #     # Conceptual relationships
    #     v1.causes(dv)
    #     # Data measurement relationships
    #     pid.has(v1)
    #     pid.has(v2)

    #     design = ts.Design(
    #         dv = dv, 
    #         ivs = [v1, v2]
    #     )

    #     synth = Synthesizer()
    #     family_facts = synth.generate_family(design=design)
    #     self.assertEqual(len(family_facts), 5)
    #     self.assertTrue(gaussian_family in family_facts)
    #     self.assertTrue(inverse_gaussian_family in family_facts)
    #     self.assertTrue(poisson_family in family_facts)
    #     self.assertTrue(gamma_family in family_facts)

    # def test_generate_family_ordinal_binary_dv(self): 
    #     o_dv = ts.Ordinal('Ordinal DV', cardinality=2)
    #     v1 = ts.Nominal('V1')
    #     v2 = ts.Nominal('V2')
    #     pid = ts.Nominal('PID')

    #     o_gaussian_family = GaussianFamily(o_dv.const)
    #     o_gamma_family = GammaFamily(o_dv.const)
    #     inverse_gaussian_family = InverseGaussianFamily(o_dv.const)
    #     poisson_family = PoissonFamily(o_dv.const)
    #     binomial_family = BinomialFamily(o_dv.const)
    #     negative_binomial_family = NegativeBinomialFamily(o_dv.const)
    #     multinomial_family = MultinomialFamily(o_dv.const)
        
    #     # Conceptual relationships
    #     v1.causes(o_dv)
    #     v2.causes(o_dv)
    #     # Data measurement relationships
    #     pid.has(v1)
    #     pid.has(v2)

    #     design = ts.Design(
    #         dv = o_dv, 
    #         ivs = [v1, v2]
    #     )

    #     synth = Synthesizer()
    #     family_facts = synth.generate_family(design=design)
    #     self.assertEqual(len(family_facts), 7)
    #     self.assertTrue(o_gaussian_family in family_facts)
    #     self.assertTrue(inverse_gaussian_family in family_facts)
    #     self.assertTrue(poisson_family in family_facts)
    #     self.assertTrue(o_gamma_family in family_facts)
    #     self.assertTrue(binomial_family in family_facts)
    #     self.assertTrue(negative_binomial_family in family_facts)
    #     self.assertFalse(multinomial_family in family_facts)
    
    # def test_generate_family_ordinal_multi_dv(self): 
    #     n = randrange(3, 1000)
    #     o_dv = ts.Ordinal('Ordinal DV', cardinality=n)
    #     v1 = ts.Nominal('V1')
    #     v2 = ts.Nominal('V2')
    #     pid = ts.Nominal('PID')

    #     o_gaussian_family = GaussianFamily(o_dv.const)
    #     o_gamma_family = GammaFamily(o_dv.const)
    #     inverse_gaussian_family = InverseGaussianFamily(o_dv.const)
    #     poisson_family = PoissonFamily(o_dv.const)
    #     binomial_family = BinomialFamily(o_dv.const)
    #     negative_binomial_family = NegativeBinomialFamily(o_dv.const)
    #     multinomial_family = MultinomialFamily(o_dv.const)
        
    #     # Conceptual relationships
    #     v1.causes(o_dv)
    #     v2.causes(o_dv)
    #     # Data measurement relationships
    #     pid.has(v1)
    #     pid.has(v2)

    #     design = ts.Design(
    #         dv = o_dv, 
    #         ivs = [v1, v2]
    #     )

    #     synth = Synthesizer()
    #     family_facts = synth.generate_family(design=design)
    #     self.assertEqual(len(family_facts), 6)
    #     self.assertTrue(o_gaussian_family in family_facts)
    #     self.assertTrue(inverse_gaussian_family in family_facts)
    #     self.assertTrue(poisson_family in family_facts)
    #     self.assertTrue(o_gamma_family in family_facts)
    #     self.assertFalse(binomial_family in family_facts)
    #     self.assertFalse(negative_binomial_family in family_facts)
    #     self.assertTrue(multinomial_family in family_facts)

    # def test_generate_family_nominal_binary_dv(self): 
    #     n_dv = ts.Nominal('Nominal DV', cardinality=2)
    #     v1 = ts.Nominal('V1')
    #     v2 = ts.Nominal('V2')
    #     pid = ts.Nominal('PID')

    #     n_gaussian_family = GaussianFamily(n_dv.const)
    #     n_gamma_family = GammaFamily(n_dv.const)
    #     inverse_gaussian_family = InverseGaussianFamily(n_dv.const)
    #     poisson_family = PoissonFamily(n_dv.const)
    #     binomial_family = BinomialFamily(n_dv.const)
    #     negative_binomial_family = NegativeBinomialFamily(n_dv.const)
    #     multinomial_family = MultinomialFamily(n_dv.const)
        
    #     # Conceptual relationships
    #     v1.causes(n_dv)
    #     v2.causes(n_dv)
    #     # Data measurement relationships
    #     pid.has(v1)
    #     pid.has(v2)

    #     design = ts.Design(
    #         dv = n_dv, 
    #         ivs = [v1, v2]
    #     )

    #     synth = Synthesizer()
    #     family_facts = synth.generate_family(design=design)
    #     self.assertEqual(len(family_facts), 2)
    #     self.assertFalse(n_gaussian_family in family_facts)
    #     self.assertFalse(inverse_gaussian_family in family_facts)
    #     self.assertFalse(poisson_family in family_facts)
    #     self.assertFalse(n_gamma_family in family_facts)
    #     self.assertTrue(binomial_family in family_facts)
    #     self.assertTrue(negative_binomial_family in family_facts)
    #     self.assertFalse(multinomial_family in family_facts)
    
    # def test_generate_family_nominal_multi_dv(self): 
    #     n = randrange(3, 1000)
    #     n_dv = ts.Nominal('Nominal DV', cardinality=n)
    #     v1 = ts.Nominal('V1')
    #     v2 = ts.Nominal('V2')
    #     pid = ts.Nominal('PID')

    #     n_gaussian_family = GaussianFamily(n_dv.const)
    #     n_gamma_family = GammaFamily(n_dv.const)
    #     inverse_gaussian_family = InverseGaussianFamily(n_dv.const)
    #     poisson_family = PoissonFamily(n_dv.const)
    #     binomial_family = BinomialFamily(n_dv.const)
    #     negative_binomial_family = NegativeBinomialFamily(n_dv.const)
    #     multinomial_family = MultinomialFamily(n_dv.const)
        
    #     # Conceptual relationships
    #     v1.causes(n_dv)
    #     v2.causes(n_dv)
    #     # Data measurement relationships
    #     pid.has(v1)
    #     pid.has(v2)

    #     design = ts.Design(
    #         dv = n_dv, 
    #         ivs = [v1, v2]
    #     )

    #     synth = Synthesizer()
    #     family_facts = synth.generate_family(design=design)
    #     self.assertEqual(len(family_facts), 1)
    #     self.assertFalse(n_gaussian_family in family_facts)
    #     self.assertFalse(inverse_gaussian_family in family_facts)
    #     self.assertFalse(poisson_family in family_facts)
    #     self.assertFalse(n_gamma_family in family_facts)
    #     self.assertFalse(binomial_family in family_facts)
    #     self.assertFalse(negative_binomial_family in family_facts)
    #     self.assertTrue(multinomial_family in family_facts)

    # @patch('tisane.smt.input_interface.InputInterface.ask_family', return_value=gaussian_family)
    # def test_generate_and_select_family_gaussian(self, input): 
    #     dv = ts.Numeric('DV')
    #     v1 = ts.Nominal('V1')
    #     v2 = ts.Nominal('V2')

    #     # Conceptual relationships
    #     v1.causes(dv)
    #     v2.causes(dv)
    #     # Data measurement relationships
    #     pid.has(v1)
    #     pid.has(v2)

    #     design = ts.Design(
    #         dv = dv, 
    #         ivs = [v1, v2]
    #     )
        
    #     sm = ts.StatisticalModel(
    #         dv=dv,
    #         fixed_ivs=[v1, v2]
    #     )
    #     synth = Synthesizer()
    #     sm = synth.generate_and_select_family(design=design, statistical_model=sm)
    #     self.assertEqual(sm.dv, dv)
    #     self.assertTrue(v1 in sm.fixed_ivs)
    #     self.assertTrue(v2 in sm.fixed_ivs)
    #     self.assertEqual(sm.random_ivs, list())
    #     self.assertEqual(sm.interactions, list())
    #     self.assertEqual(sm.family, 'Gaussian')
    #     self.assertIsNone(sm.link_function)
    
    # @patch('tisane.smt.input_interface.InputInterface.ask_family', return_value=gamma_family)
    # def test_generate_and_select_family_gamma(self, input): 
    #     dv = ts.Numeric('DV')
    #     v1 = ts.Nominal('V1')
    #     v2 = ts.Nominal('V2')

    #     # Conceptual relationships
    #     v1.causes(dv)
    #     v2.causes(dv)
    #     # Data measurement relationships
    #     pid.has(v1)
    #     pid.has(v2)

    #     design = ts.Design(
    #         dv = dv, 
    #         ivs = [v1, v2]
    #     )
        
    #     sm = ts.StatisticalModel(
    #         dv=dv,
    #         fixed_ivs=[v1, v2]
    #     )

    #     synth = Synthesizer()
    #     sm = synth.generate_and_select_family(design=design, statistical_model=sm)
    #     self.assertEqual(sm.dv, dv)
    #     self.assertTrue(v1 in sm.fixed_ivs)
    #     self.assertTrue(v2 in sm.fixed_ivs)
    #     self.assertEqual(sm.random_ivs, list())
    #     self.assertEqual(sm.interactions, list())
    #     self.assertEqual(sm.family, 'Gamma')
    #     self.assertIsNone(sm.link_function)

    # @patch("tisane.smt.input_interface.InputInterface.resolve_unsat")
    # @patch('tisane.smt.input_interface.InputInterface.ask_inclusion', return_value='y')
    # def test_generate_and_select_link_gaussian_identity(self, input, mock_increment): 
    #     dv = ts.Numeric('DV')
    #     v1 = ts.Nominal('V1')
    #     v2 = ts.Nominal('V2')

    #     # Simulate end-user selecting between two options at a time repeatedly
    #     mock_increment.side_effect = [IdentityTransform(dv.const), IdentityTransform(dv.const)]

    #     # Conceptual relationships
    #     v1.causes(dv)
    #     v2.causes(dv)
    #     # Data measurement relationships
    #     pid.has(v1)
    #     pid.has(v2)

    #     design = ts.Design(
    #         dv = dv, 
    #         ivs = [v1, v2]
    #     )

    #     # StatisticalModel with all but link 
    #     sm = ts.StatisticalModel(
    #         dv=dv, 
    #         fixed_ivs=[v1, v2],
    #         family='Gaussian'
    #     )

    #     synth = Synthesizer() 
    #     sm = synth.generate_and_select_link(design=design, statistical_model=sm)
    #     self.assertEqual(sm.dv, dv)
    #     self.assertTrue(v1 in sm.fixed_ivs)
    #     self.assertTrue(v2 in sm.fixed_ivs)
    #     self.assertEqual(sm.random_ivs, list())
    #     self.assertEqual(sm.interactions, list())
    #     self.assertEqual(sm.family, 'Gaussian')
    #     self.assertIsNotNone(sm.link_function)
    #     self.assertEqual(sm.link_function, 'Identity')
    
    # @patch("tisane.smt.input_interface.InputInterface.resolve_unsat")
    # @patch('tisane.smt.input_interface.InputInterface.ask_inclusion', return_value='y')
    # def test_generate_and_select_link_gaussian_log(self, input, mock_increment): 
    #     dv = ts.Numeric('DV')
    #     v1 = ts.Nominal('V1')
    #     v2 = ts.Nominal('V2')
        
    #     # Simulate end-user selecting between two options at a time repeatedly
    #     mock_increment.side_effect = [LogTransform(dv.const), LogTransform(dv.const)]

    #     # Conceptual relationships
    #     v1.causes(dv)
    #     v2.causes(dv)
    #     # Data measurement relationships
    #     pid.has(v1)
    #     pid.has(v2)

    #     design = ts.Design(
    #         dv = dv, 
    #         ivs = [v1, v2]
    #     )

    #     # StatisticalModel with all but link 
    #     sm = ts.StatisticalModel(
    #         dv=dv, 
    #         fixed_ivs=[v1, v2],
    #         family='Gaussian'
    #     )

    #     synth = Synthesizer() 
    #     sm = synth.generate_and_select_link(design=design, statistical_model=sm)
    #     self.assertEqual(sm.dv, dv)
    #     self.assertTrue(v1 in sm.fixed_ivs)
    #     self.assertTrue(v2 in sm.fixed_ivs)
    #     self.assertEqual(sm.random_ivs, list())
    #     self.assertEqual(sm.interactions, list())
    #     self.assertEqual(sm.family, 'Gaussian')
    #     self.assertIsNotNone(sm.link_function)
    #     self.assertEqual(sm.link_function, 'Log')

    # @patch("tisane.smt.input_interface.InputInterface.resolve_unsat")
    # @patch('tisane.smt.input_interface.InputInterface.ask_inclusion', return_value='y')
    # def test_generate_and_select_link_gaussian_squareroot(self, input, mock_increment): 
    #     dv = ts.Numeric('DV')
    #     v1 = ts.Nominal('V1')
    #     v2 = ts.Nominal('V2')

    #     mock_increment.side_effect = [IdentityTransform(dv.const), SquarerootTransform(dv.const)]

    #     # Conceptual relationships
    #     v1.causes(dv)
    #     v2.causes(dv)
    #     # Data measurement relationships
    #     pid.has(v1)
    #     pid.has(v2)

    #     design = ts.Design(
    #         dv = dv, 
    #         ivs = [v1, v2]
    #     )

    #     # StatisticalModel with all but link 
    #     sm = ts.StatisticalModel(
    #         dv=dv, 
    #         fixed_ivs=[v1, v2],
    #         family='Gaussian'
    #     )

    #     synth = Synthesizer() 
    #     sm = synth.generate_and_select_link(design=design, statistical_model=sm)
    #     self.assertEqual(sm.dv, dv)
    #     self.assertTrue(v1 in sm.fixed_ivs)
    #     self.assertTrue(v2 in sm.fixed_ivs)
    #     self.assertEqual(sm.random_ivs, list())
    #     self.assertEqual(sm.interactions, list())
    #     self.assertEqual(sm.family, 'Gaussian')
    #     self.assertIsNotNone(sm.link_function)
    #     self.assertEqual(sm.link_function, 'Squareroot')
    
    # @patch('tisane.smt.input_interface.InputInterface.ask_inclusion', return_value='y')
    # def test_generate_and_select_link_binomial(self, input): 
    #     pass

    # def test_genearate_and_select_random_effects(self): 
    #     pass

    # @pytest.mark.skip(reason="Sanity check that the interaction loop works after testing all the individual components")
    # def test_one_level_fixed(self): 
    #     """
    #     Example from Bansal et al. CHI 2021
    #     """
    #     acc = ts.Numeric('accuracy')
    #     expl = ts.Nominal('explanation type')
    #     variables = [acc, expl]

    #     # Conceptual relationships
    #     expl.associates_with(acc)
    #     # Data measurement relationships
    #     expl.treats(pid)

    #     design = ts.Design(
    #         dv = acc, 
    #         ivs = [expl]
    #     )

    #     design = ts.Design(
    #         dv = acc, 
    #         ivs = ts.Level(identifier='id', measures=[expl])
    #     )

    #     ts.synthesize_statistical_model(design=design)
    #     
    
    # @pytest.mark.skip(reason="Sanity check that the interaction loop works after testing all the individual components")
    # def test_one_level_fixed_interaction(self): 
    #     """
    #     Example from Kreft & de Leeuw, 1989
    #     """
    #     student = ts.Nominal('Student')
    #     school = ts.Nominal('School')
    #     math = ts.Numeric('MathAchievement')
    #     hw = ts.Numeric('HomeWork')
    #     race = ts.Nominal('Race')
    #     ses = ts.Numeric('SES')

    #     # Conceptual relationships
    #     hw.causes(math)
    #     race.associates_with(math)
    #     ses.associates_with(math) # TODO: Transitive cause should be something Tisane surface/suggests to user?

    #     # Data measurement relationships
    #     student.has(hw)
    #     student.has(race)
    #     student.has(ses)

    #     design = ts.Design(
    #         dv = math, 
    #         ivs = [hw, race, ses]
    #     )

    #     ts.synthesize_statistical_model(design=design)
    
    # @pytest.mark.skip(reason="Sanity check that the interaction loop works after testing all the individual components")
    # def test_two_levels_fixed_interaction(self): 
    #     # Variables
    #     student = ts.Nominal('Student')
    #     school = ts.Nominal('School')
    #     math = ts.Numeric('MathAchievement')
    #     hw = ts.Numeric('HomeWork')
    #     race = ts.Nominal('Race')
    #     mean_ses = ts.Numeric('MeanSES')
    #     variables = [math, hw, race, mean_ses]

    #     # Conceptual relationships
    #     hw.causes(math)
    #     race.associates_with(math)
    #     mean_ses.associates_with(math)

    #     # Data measurement relationships
    #     student.has(hw)
    #     student.has(race)
    #     school.has(mean_ses)
        
    #     design = ts.Design(
    #         dv = math, 
    #         ivs = [hw, race, mean_ses]
    #     )

    #     ts.synthesize_statistical_model(design=design)

    # @pytest.mark.skip(reason="Sanity check that the interaction loop works after testing all the individual components")
    # def test_two_levels_random(self): 
    #     # Variables
    #     student = ts.Nominal('Student')
    #     school = ts.Nominal('School')
    #     math = ts.Numeric('MathAchievement')
    #     hw = ts.Numeric('HomeWork')
    #     race = ts.Nominal('Race')
    #     mean_ses = ts.Numeric('MeanSES')
    #     variables = [math, hw, race, mean_ses]

    #     # Conceptual relationships
    #     hw.causes(math)
    #     race.associates_with(math)
    #     mean_ses.associates_with(math)

    #     # Data measurement relationships
    #     student.has(hw)
    #     student.has(race)
    #     school.has(mean_ses)
        
    #     design = ts.Design(
    #         dv = math, 
    #         ivs = [hw, race, mean_ses]
    #     )

    #     ts.synthesize_statistical_model(design=design)
        