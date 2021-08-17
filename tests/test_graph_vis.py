from tisane import graph
import tisane as ts
from tisane.variable import Has
from tisane.smt.synthesizer import Synthesizer
from tisane.graph_vis_support import dot_formats
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
    #     gr.causes(v1, v3)
    #     gr.causes(v2, v3)
    #
    #     gr.visualize_graph
    #     self.assertIsInstance(v1, ts.Nominal)
    def test_units(self):
        student = ts.Unit("student id")
        school = ts.Unit("school id")
        test_score = student.numeric("test score")

        school.causes(test_score)

        design = ts.Design(dv=test_score, ivs=[student, school])
        # gr = ts.Graph()
        # gr._add_variable(student)
        # gr._add_variable(school)
        # gr._add_variable(test_score)
        # school.causes(test_score)
        # # gr.has(student, test_score)
        # gr.causes(school, test_score)
        # gr.associates(student, test_score)
        gr = design.graph

        gr.get_tikz_graph("examples/standalone2.tex")
        gr.get_dot_graph(path="examples/test_units.png")

    #     race.associates_with(test_score)
    #     student.associates_with(test_score)
    #     race.causes(tutoring)

    #     race.moderates(ses, on=test_score)

    #     design = ts.Design(dv=test_score, ivs=[race, ses])
    #     print(design.get_variables())

    #     gr = design.graph
    #     print(gr.get_nodes())
    #     gr._get_graph_tikz()
    #     # self.assertTrue(gr.has_variable(test_score))
    #     gr.visualize_graph()

    # As of August 10, this is the example used in the README
    def test_exercise_group_simplified(self):
        adult = ts.Unit("member", cardinality=386)
        motivation_level = adult.ordinal("motivation", order=[1, 2, 3, 4, 5, 6])
        # Adults have pounds lost.
        pounds_lost = adult.numeric("pounds_lost")
        age = adult.numeric("age")
        # Adults have one of four racial identities in this study.
        race = adult.nominal("race group", cardinality=4)
        week = ts.SetUp("Week", order=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])

        motivation_level.causes(pounds_lost)
        race.associates_with(pounds_lost)
        week.associates_with(pounds_lost)

        age.moderates(moderator=[motivation_level], on=pounds_lost)

        design = ts.Design(dv=pounds_lost, ivs=[age, race, week])
        gr = design.graph
        # print(gr.get_nodes())
        gr.get_tikz_graph("examples/standalone1.tex")
        # self.assertTrue(gr.has_variable(test_score))
        # gr.visualize_graph()

        gr.get_dot_graph(path="examples/test_more_complex.png")

        gr.get_causes_associates_dot_graph(
            path="test_more_complex-causes_associates.png"
        )

        hasgraph = gr._get_dot_graph(
            edge_filter=lambda edge_data: edge_data["edge_type"] == "has"
        )
        hasgraph.write_png("test_more_complex-has.png")

    # As of August 10, this is the example used in the README
    def test_exercise_group_simplified(self):
        adult = ts.Unit("member", cardinality=386)
        motivation_level = adult.ordinal("motivation", order=[1, 2, 3, 4, 5, 6])
        # Adults have pounds lost.
        pounds_lost = adult.numeric("pounds lost")
        age = adult.numeric("age")
        # Adults have one of four racial identities in this study.
        race = adult.nominal("race group", cardinality=4)
        week = ts.SetUp("Week", order=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])

        motivation_level.causes(pounds_lost)
        race.associates_with(pounds_lost)
        week.associates_with(pounds_lost)

        age.moderate(moderator=[motivation_level], on=pounds_lost)

        design = ts.Design(dv=pounds_lost, ivs=[age, race])
        gr = design.graph
        gr.get_tikz_graph("examples/readme_graph_tikz.tex", dv=pounds_lost)
        # gr._get_graph_tikz()
        dot_gr = gr.get_dot_graph("examples/readme_dot_graph.png", dv=pounds_lost)
        # dot_gr.write_png("readme_dot_graph.png")

        gr.get_dot_graph("dot_example/dot_example.png", format="png")
        # dot = gr._get_dot_graph()
        # for f in dot_formats:
        #     dot.write("dot_example_{}".format(f), format=f)
