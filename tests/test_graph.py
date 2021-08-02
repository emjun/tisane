from tisane import graph
import tisane as ts
from tisane.variable import Causes, Has, Nests, Associates
from tisane.smt.synthesizer import Synthesizer

import unittest


class GraphTest(unittest.TestCase):
    def test_variables_node(self):
        v1 = ts.Unit("V1")
        v2 = ts.Unit("V2")
        v3 = ts.Unit("V3")

        gr = ts.Graph()
        gr._add_variable(v1)
        gr._add_variable(v2)
        gr._add_variable(v3)

        self.assertEqual(len(gr.get_variables()), len(gr.get_nodes()))

    def test_get_conceptual_subgraph(self):
        v1 = ts.Unit("V1")
        v2 = v1.nominal("V2")
        v3 = v1.nominal("V3")

        gr = ts.Graph()
        causes_obj_1 = Causes(v1, v2)
        causes_obj_2 = Causes(v2, v3)
        gr.causes(v1, v2, causes_obj_1)
        gr.causes(v2, v3, causes_obj_2)

        has_obj = v1.relationships[0]
        self.assertIsInstance(has_obj, Has)
        gr.has(v1, v2, has_obj, 1)

        sub_gr = gr.get_conceptual_subgraph()
        self.assertEqual(len(sub_gr.get_edges()), 2)

    def test_get_causal_subgraph(self):
        v1 = ts.Unit("V1")
        v2 = v1.nominal("V2")
        v3 = v1.nominal("V3")

        gr = ts.Graph() 
        causes_obj = Causes(v1, v2)
        gr.causes(v1, v2, causes_obj)
        associates_obj = Associates(v2, v3)
        gr.associates(v2, v3, associates_obj) # Question: When should the edge_obj be created? by whom? --> make consistent for all edges; Why do some edge types create them sooner than others?

        has_obj = v1.relationships[0]
        self.assertIsInstance(has_obj, Has)
        gr.has(v1, v2, has_obj, 1)

        sub_gr = gr.get_causal_subgraph()
        self.assertEqual(len(sub_gr.get_edges()), 1)

    def test_get_identifiers_direct(self):
        v1 = ts.Unit("V1")
        v2 = v1.nominal("V2")
        v3 = v1.nominal("V3")

        gr = ts.Graph()
        has_obj = v1.relationships[0]
        self.assertIsInstance(has_obj, Has)
        gr.has(v1, v2, has_obj, 1)

        ids = gr.get_identifiers()
        self.assertEqual(len(ids), 1)
        self.assertTrue(v1 in ids)

    def test_get_identifiers_nest(self):
        student = ts.Unit("student id")
        school = ts.Unit("school")
        age = student.numeric("age")
        math = student.numeric("math score")

        age.associates_with(math)  # Introduces 2 edges (bidirectional)

        student.nests_within(school)

        design = ts.Design(dv=math, ivs=[age])

        # Pre-transformation
        gr = design.graph
        ids = gr.get_identifiers()
        self.assertEqual(len(ids), 2)
        self.assertTrue(student in ids)
        self.assertTrue(school in ids)

        ids = gr.get_identifiers()
        id_names = [i.name for i in ids]
        self.assertEqual(len(ids), 2)
        self.assertTrue(student in ids)
        self.assertTrue(student.name in id_names)
        self.assertTrue(school in ids)
        self.assertTrue(school.name in id_names)

    def test_get_identifiers_treatment(self):
        pid = ts.Unit("pid")
        acc = pid.numeric("accuracy")
        expl = pid.nominal("explanation type")
        variables = [acc, expl]

    
        design = ts.Design(dv=acc, ivs=[expl])

        # Pre-transformation
        gr = design.graph
        ids = gr.get_identifiers()
        id_names = [i.name for i in ids]
        self.assertEqual(len(ids), 1)
        self.assertTrue(pid.name in id_names)

    def test_get_identifiers_repeat(self):
        pig = ts.Unit("pig id", cardinality=24)  # 24 pigs
        time = pig.nominal("week number", cardinality=12)
        weight = pig.numeric("weight")

        pig.repeats(measure=weight, according_to=time)

        design = ts.Design(dv=weight, ivs=[time])
        gr = design.graph
        ids = gr.get_identifiers()
        id_names = [i.name for i in ids]
        self.assertEqual(len(ids), 1)
        self.assertTrue(pig.name in id_names)

    def test_graph_construction_with_units(self):
        pig = ts.Unit("pig id")
        litter = ts.Unit("litter")
        weight = pig.numeric("weight")

        # pig.nests_within(litter, up_to=30)
        pig.nests_within(litter)

        design = ts.Design(dv=weight, ivs=[pig, litter])

        gr = design.graph
        self.assertTrue(gr.has_variable(weight))
        self.assertTrue(gr.has_variable(pig))
        self.assertTrue(gr.has_variable(litter))

    def test_get_identifiers_with_units(self):
        pig = ts.Unit("pig id")
        litter = ts.Unit("litter")
        weight = pig.numeric("weight")

        # pig.nests_within(litter, up_to=30)
        pig.nests_within(litter)

        design = ts.Design(dv=weight, ivs=[pig, litter])

        gr = design.graph
        vars = gr.get_identifiers()
        self.assertEqual(len(vars), 2)  # 2 units/levels in the graph
        self.assertIn(pig, vars)
        self.assertIn(litter, vars)

    def test_get_variables_with_units(self):
        pig = ts.Unit("pig id")
        litter = ts.Unit("litter")
        weight = pig.numeric("weight")

        # pig.nests_within(litter, up_to=30)
        pig.nests_within(litter)
        
        design = ts.Design(dv=weight, ivs=[pig, litter])

        gr = design.graph
        vars = gr.get_identifiers()
        self.assertEqual(len(vars), 2)  # 2 units/levels in the graph
        self.assertIn(pig, vars)
        self.assertIn(litter, vars)

        self.assertEqual(len(pig.relationships), 2)
        for obj in pig.relationships:
            if isinstance(obj, Has):
                self.assertEqual(pig, obj.variable)
                self.assertIsNotNone(gr.has_edge(pig, obj.measure, "has"))
            elif isinstance(obj, Nests):
                self.assertEqual(pig, obj.base)
                self.assertEqual(litter, obj.group)
                self.assertIsNotNone(gr.has_edge(pig, litter, "nest"))

        self.assertEqual(len(litter.relationships), 1)
        for obj in litter.relationships:
            self.assertIsInstance(obj, Nests)
            self.assertEqual(pig, obj.base)
            self.assertEqual(litter, obj.group)        

    def test_add_interaction_effects(self):
        student = ts.Unit("Student")
        # Variables instantiated through Units
        race = student.nominal("Race", cardinality=5)
        ses = student.numeric("SES")
        test_score = student.numeric("Test score")
        tutoring = student.nominal("treatment", cardinality=3)

        # Conceptual relationships
        race.associates_with(test_score)
        student.associates_with(test_score)
    
        # Data measurement relationships
        # student.has(race, exactly=1)
        # student.has(ses, exactly=1)
        # student.has(test_score, exactly=1)
        # student.has(tutoring, exactly=3) # complete factorial design
        # student.has(tutoring, up_to=3) # incomplete factorial design 

        # tutoring.has(student, exactly=30) # introduces ambiguity

        race.moderate(ses, on=test_score)

        self.assertEqual(len(student.relationships), 5)

        design = ts.Design(dv=test_score, ivs=[race, ses])

        gr = design.graph
        identifiers = gr.get_identifiers()
        self.assertIn(student, identifiers)
        self.assertTrue(gr.has_edge(student, race, "has"))
        self.assertTrue(gr.has_edge(student, ses, "has"))
        self.assertTrue(gr.has_edge(student, test_score, "has"))
        self.assertFalse(gr.has_edge(student, tutoring, "has")) # SHOULD THIS BE TRUE OR FALSE

        variables = gr.get_variables()
        self.assertEqual(
            len(variables), 5
        )  # Check that interaction effect is part of graph as a new variable/node
        v_names = [v.name for v in variables]
        self.assertIn("Student", v_names)
        self.assertIn("Race", v_names)
        self.assertIn("SES", v_names)
        self.assertIn("Test score", v_names)
        self.assertIn(
            "Race*SES", v_names
        )  # Check that interaction effect is part of graph as a new variable/node

        edges = gr.get_edges()

        count_has_edges = 0
        count_associates_edges = 0
        count_other_edges = 0
        for (start, end, data) in edges:
            if isinstance(data['edge_obj'], Has):
                count_has_edges += 1
            elif isinstance(data['edge_obj'], Associates):
                count_associates_edges += 1
            else:
                count_other_edges += 1
        
        import pdb; pdb.set_trace()
        self.assertEqual(count_has_edges, 4) # Should this be 5?
        self.assertEqual(count_associates_edges, 6)
        self.assertEqual(count_other_edges, 0)


        # Identifier has interaction effect only once (no duplicates)
        # Associate (between Race*SES and Test score introduces to edges)
        self.assertEqual(len(edges), 10)

        # Check associate edge for interaction effect
        lhs = None
        for v in variables:
            if v.name == "Race*SES":
                lhs = v
        self.assertIsNotNone(lhs)
        self.assertTrue(gr.has_edge(lhs, test_score, "associate"))
        self.assertTrue(gr.has_edge(test_score, lhs, "associate"))

        # Check that the interaction effect inherits from Student unit
        self.assertTrue(gr.has_edge(student, lhs, "has"))

    # # def test_add_interaction_effects_units(self):
    # #     student = ts.Unit("Student")
    # #     race = ts.Nominal("Race")
    # #     ses = ts.Numeric("SES")
    # #     test_score = ts.Numeric("Test score")

    # #     race.moderate(ses, on=test_score)

    # #     design = ts.Design(dv=test_score, ivs=[race, ses])

    # #     gr = design.graph

    # #     edges = gr.get_edges()
