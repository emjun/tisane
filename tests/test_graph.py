from tisane import graph
import tisane as ts
from tisane.variable import Has
from tisane.smt.synthesizer import Synthesizer

import unittest


class GraphTest(unittest.TestCase):
    def test_variables_node(self):
        v1 = ts.Nominal("V1")
        v2 = ts.Nominal("V2")
        v3 = ts.Nominal("V3")

        gr = ts.Graph()
        gr._add_variable(v1)
        gr._add_variable(v2)
        gr._add_variable(v3)

        self.assertEqual(len(gr.get_variables()), len(gr.get_nodes()))

    def test_get_conceptual_subgraph(self):
        v1 = ts.Numeric("V1")
        v2 = ts.Numeric("V2")
        v3 = ts.Numeric("V3")

        gr = ts.Graph()
        gr.cause(v1, v2)
        gr.cause(v2, v3)

        v1.has(v2)
        has_obj = v1.relationships[0]
        self.assertIsInstance(has_obj, Has)
        gr.has(v1, v2, has_obj, 1)

        sub_gr = gr.get_conceptual_subgraph()
        self.assertEqual(len(sub_gr.get_edges()), 2)

    def test_get_causal_subgraph(self):
        v1 = ts.Numeric("V1")
        v2 = ts.Numeric("V2")
        v3 = ts.Numeric("V3")

        gr = ts.Graph()
        gr.cause(v1, v2)
        gr.associate(v2, v3)

        v1.has(v2)
        has_obj = v1.relationships[0]
        self.assertIsInstance(has_obj, Has)
        gr.has(v1, v2, has_obj, 1)

        sub_gr = gr.get_causal_subgraph()
        self.assertEqual(len(sub_gr.get_edges()), 1)

    def test_get_identifiers_direct(self):
        v1 = ts.Numeric("V1")
        v2 = ts.Numeric("V2")
        v3 = ts.Numeric("V3")

        gr = ts.Graph()
        v1.has(v2)
        has_obj = v1.relationships[0]
        self.assertIsInstance(has_obj, Has)
        gr.has(v1, v2, has_obj, 1)

        ids = gr.get_identifiers()
        self.assertEqual(len(ids), 1)
        self.assertTrue(v1 in ids)

    def test_get_identifiers_nest(self):
        student = ts.Nominal("student id")
        school = ts.Nominal("school")
        age = ts.Numeric("age")
        math = ts.Numeric("math score")

        age.associates_with(math)  # Introduces 2 edges (bidirectional)

        student.has(age)
        student.nest_under(school)

        design = ts.Design(dv=math, ivs=[age])

        # Pre-transformation
        gr = design.graph
        ids = gr.get_identifiers()
        self.assertEqual(len(ids), 2)
        self.assertTrue(student in ids)
        self.assertTrue(school in ids)

        synth = Synthesizer()
        updated_gr = synth.transform_to_has_edges(gr)

        # Post-transformation
        ids = updated_gr.get_identifiers()
        id_names = [i.name for i in ids]
        self.assertEqual(len(ids), 2)
        self.assertFalse(student in ids)
        self.assertTrue(student.name in id_names)
        self.assertFalse(school in ids)
        self.assertTrue(school.name in id_names)

    def test_get_identifiers_treatment(self):
        pid = ts.Nominal("pid")
        acc = ts.Numeric("accuracy")
        expl = ts.Nominal("explanation type")
        variables = [acc, expl]

        # Data measurement relationships
        expl.treats(pid)

        design = ts.Design(dv=acc, ivs=[expl])

        # Pre-transformation
        gr = design.graph
        ids = gr.get_identifiers()
        self.assertEqual(len(ids), 0)

        synth = Synthesizer()
        updated_gr = synth.transform_to_has_edges(gr)

        # Post-transformation
        ids = updated_gr.get_identifiers()
        id_names = [i.name for i in ids]
        self.assertEqual(len(ids), 1)
        self.assertTrue(pid.name in id_names)

    def test_get_identifiers_repeat(self):
        pig = ts.Nominal("pig id", cardinality=24)  # 24 pigs
        time = ts.Nominal("week number")
        weight = ts.Numeric("weight")

        pig.repeats(weight, according_to=time)

        design = ts.Design(dv=weight, ivs=[time])

        # Pre-transformation
        gr = design.graph
        ids = gr.get_identifiers()
        self.assertEqual(len(ids), 0)

        synth = Synthesizer()
        updated_gr = synth.transform_to_has_edges(gr)

        # Post-transformation
        ids = updated_gr.get_identifiers()
        id_names = [i.name for i in ids]
        self.assertEqual(len(ids), 1)
        self.assertTrue(pig.name in id_names)

    def test_graph_construction_with_units(self):
        pig = ts.Unit("pig id")
        litter = ts.Unit("litter")
        weight = ts.Numeric("weight")

        pig.has(weight, exactly=1)
        pig.has(litter, exactly=1)
        litter.has(pig, up_to=30)

        design = ts.Design(dv=weight, ivs=[pig, litter])

        gr = design.graph
        self.assertTrue(gr.has_variable(weight))
        self.assertTrue(gr.has_variable(pig))
        self.assertTrue(gr.has_variable(litter))

    def test_get_identifiers_with_units(self):
        pig = ts.Unit("pig id")
        litter = ts.Unit("litter")
        weight = ts.Numeric("weight")

        pig.has(weight, exactly=1)
        pig.has(litter, exactly=1)
        litter.has(pig, up_to=30)

        design = ts.Design(dv=weight, ivs=[pig, litter])

        gr = design.graph
        vars = gr.get_identifiers()
        self.assertEqual(len(vars), 2)  # 2 units/levels in the graph
        self.assertIn(pig, vars)
        self.assertIn(litter, vars)

    def test_get_variables_with_units(self):
        pig = ts.Unit("pig id")
        litter = ts.Unit("litter")
        weight = ts.Numeric("weight")

        pig.has(weight, exactly=1)

        pig.has(litter, exactly=1)
        litter.has(pig, up_to=30)

        design = ts.Design(dv=weight, ivs=[pig, litter])

        gr = design.graph
        vars = gr.get_identifiers()
        self.assertEqual(len(vars), 2)  # 2 units/levels in the graph
        self.assertIn(pig, vars)
        self.assertIn(litter, vars)

        self.assertEqual(len(pig.relationships), 3)
        for obj in pig.relationships:
            self.assertIsInstance(obj, Has)

            if pig == obj.variable:
                self.assertIsNotNone(gr.has_edge(pig, obj.measure, "has"))
            else:
                self.assertEqual(litter, obj.variable)
                self.assertEqual(pig, obj.measure)
                self.assertIsNotNone(gr.has_edge(litter, pig, "has"))

        self.assertEqual(len(litter.relationships), 2)
        for obj in litter.relationships:
            self.assertIsInstance(obj, Has)

            if litter == obj.variable:
                self.assertIsNotNone(gr.has_edge(litter, obj.measure, "has"))
            else:
                self.assertEqual(pig, obj.variable)
                self.assertEqual(litter, obj.measure)
                self.assertIsNotNone(gr.has_edge(litter, pig, "has"))

        # WHAT happens once construct graph?? - end to end examples with test case?
