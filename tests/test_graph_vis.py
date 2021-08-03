from tisane import graph
import tisane as ts
from tisane.variable import Has
from tisane.smt.synthesizer import Synthesizer

import unittest


class GraphVisTest(unittest.TestCase):
    # def test_vis(self):
    #     v1 = ts.Nominal("V1")
    #     v2 = ts.Nominal("V2")
    #     v3 = ts.Nominal("V3")
    #
    #
    #
    #     gr = ts.Graph()
    #     gr._add_variable(v1)
    #     gr._add_variable(v2)
    #     gr.cause(v1, v3)
    #     gr.cause(v2, v3)
    #
    #     gr.visualize_graph
    #     self.assertIsInstance(v1, ts.Nominal)
    def test_units(self):
        student = ts.Unit("student id")
        school = ts.Unit("school id")
        test_score = student.numeric("test score")

        gr = ts.Graph()
        gr._add_variable(student)
        gr._add_variable(school)
        gr._add_variable(test_score)
        school.causes(test_score)
        # gr.has(student, test_score)
        gr.cause(school, test_score)
        gr.associate(student, test_score)

        gr._get_graph_tikz()

        # gr.visualize_graph()

    def test_more_complex(self):

        student = ts.Unit(
            "Student", attributes=[]
        )  # object type, specify data types through object type
        race = student.nominal("Race", cardinality=5, exactly=1)  # proper OOP
        ses = student.numeric("SES")
        test_score = student.nominal("Test score")
        tutoring = student.nominal("treatment")

        race.associates_with(test_score)
        student.associates_with(test_score)
        race.causes(tutoring)

        race.moderate(ses, on=test_score)

        design = ts.Design(dv=test_score, ivs=[race, ses])
        print(design.get_variables())

        gr = design.graph
        print(gr.get_nodes())
        gr._get_graph_tikz()
        # self.assertTrue(gr.has_variable(test_score))
        gr.visualize_graph()
