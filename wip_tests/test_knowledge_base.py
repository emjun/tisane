import tisane as ts
from tisane.effect_set import EffectSet
from tisane.statistical_model import LinearRegression

import unittest


class KnowledgeBaseTests(unittest.TestCase):

    # def test_ctor(self):
    #     # analysis = ts.Tisane(task="prediction") # analysis has one task

    #     test_score = ts.Concept("Test Score")
    #     intelligence = ts.Concept("Intelligence")
    #     tutoring = ts.Concept("Tutoring")

    #     test_score.specifyData(dtype="numeric") # Score 0 - 100
    #     intelligence.specifyData(dtype="numeric") # IQ score
    #     tutoring.specifyData(dtype="nominal", categories=["afterschool", "none"])

    #     ivs = [intelligence, tutoring]
    #     dvs = [test_score]

    #     kb = KnowledgeBase(ivs, dvs)

    #     # ASSERT
    #     self.assertEqual(len(kb.all_stat_models), 2)
    #     self.assertEqual(kb.all_stat_models[0].name, 'Linear Regression')
    #     self.assertEqual(len(kb.all_stat_models[0].properties), 2)
    #     self.assertEqual(kb.all_stat_models[0].properties[0], kb.all_properties['numeric_dv'])
    #     self.assertEqual(kb.all_stat_models[0].properties[1], kb.all_properties['normal_distribution_residuals'])
    #     # self.assertEqual(kb.all_stat_models[0].properties[1], kb.all_properties['residual_normal_distribution'])

    # def test_pick_linear_regression(self):
    #     test_score = ts.Concept("Test Score")
    #     intelligence = ts.Concept("Intelligence")
    #     tutoring = ts.Concept("Tutoring")

    #     test_score.specifyData(dtype="numeric") # Score 0 - 100
    #     intelligence.specifyData(dtype="numeric") # IQ score
    #     tutoring.specifyData(dtype="nominal", categories=["afterschool", "none"])

    #     ivs = [intelligence, tutoring]
    #     dvs = [test_score]

    #     valid_models = find_statistical_models(ivs=ivs, dvs=dvs)

    #     self.assertEqual(len(valid_models), 2)
    #     self.assertEqual(valid_models[0], 'Linear Regression')
    # def test_concept(self):
    #     analysis = ts.Tisane(task="explanation")

    #     # Add concepts
    #     test_score = ts.Concept("Test Score")
    #     intelligence = ts.Concept("Intelligence")
    #     tutoring = ts.Concept("Tutoring")
    #     concepts = [test_score, intelligence, tutoring]

    #

    #     # Add relationships
    #     analysis.addRelationship(intelligence, test_score, "cause")
    #     analysis.addRelationship(tutoring, test_score, "cause")
    #     analysis.addRelationship(intelligence, tutoring, "correlate")

    #

    def test_variable_format_assertions(self):
        analysis = ts.Tisane(task="explanation")

        # Add concepts
        test_score = ts.Concept("Test Score")
        intelligence = ts.Concept("Intelligence")
        tutoring = ts.Concept("Tutoring")
        concepts = [test_score, intelligence, tutoring]

        # Specify data (schema)
        test_score.specifyData(dtype="numeric")
        intelligence.specifyData(dtype="numeric")
        tutoring.specifyData(
            dtype="nominal", categories=["After school", "Before school"]
        )

        # Some assertions are inferred from data schema, see above
        self.assertTrue(
            test_score.getVariable().has_property_value(prop="dtype", val="numeric")
        )
        self.assertTrue(
            intelligence.getVariable().has_property_value(prop="dtype", val="numeric")
        )
        self.assertTrue(
            tutoring.getVariable().has_property_value(prop="dtype", val="nominal")
        )

        self.assertFalse(test_score.getVariable().has_property(prop="cardinality"))
        self.assertFalse(intelligence.getVariable().has_property(prop="cardinality"))
        self.assertTrue(
            tutoring.getVariable().has_property_value(prop="cardinality", val="binary")
        )

        kb = analysis.knowledge_base

        # This tells us that as long as we pass the correct parameters, the ASP constraints for variables are generated correctly.
        self.assertEqual(
            format_concept_variable_constraint(
                concept=test_score, key="dtype", val="numeric"
            ),
            "numeric(test_score).",
        )
        self.assertEqual(
            format_concept_variable_constraint(
                concept=intelligence, key="dtype", val="numeric"
            ),
            "numeric(intelligence).",
        )
        self.assertEqual(
            format_concept_variable_constraint(
                concept=tutoring, key="dtype", val="nominal"
            ),
            "categorical(tutoring).",
        )
        self.assertEqual(
            format_concept_variable_constraint(
                concept=tutoring, key="cardinality", val="binary"
            ),
            "binary(tutoring).",
        )

    def test_effect_set_format_assertions(self):
        analysis = ts.Tisane(task="explanation")

        # Add concepts
        test_score = ts.Concept("Test Score")
        intelligence = ts.Concept("Intelligence")
        tutoring = ts.Concept("Tutoring")
        concepts = [test_score, intelligence, tutoring]

        # Add relationships
        analysis.addRelationship(intelligence, test_score, "cause")
        analysis.addRelationship(tutoring, test_score, "cause")
        analysis.addRelationship(intelligence, tutoring, "correlate")

        # Specify data (schema)
        test_score.specifyData(dtype="numeric")
        intelligence.specifyData(dtype="numeric")
        tutoring.specifyData(
            dtype="nominal", categories=["After school", "Before school"]
        )
        # tutoring.specifyData(dtype="nominal", categories=["After school", "Before school", "None"])

        # Get valid statistical models
        # Assert statistical properties needed for linear regression
        # Generate effects sets
        effects = analysis.generate_effects_sets(
            ivs=[intelligence, tutoring], dv=test_score
        )

        # Add individual variable assertions
        # Some assertions are inferred from data schema, see above
        self.assertTrue(
            test_score.getVariable().has_property_value(prop="dtype", val="numeric")
        )
        self.assertTrue(
            intelligence.getVariable().has_property_value(prop="dtype", val="numeric")
        )
        self.assertTrue(
            tutoring.getVariable().has_property_value(prop="dtype", val="nominal")
        )

        self.assertFalse(test_score.getVariable().has_property(prop="cardinality"))
        self.assertFalse(intelligence.getVariable().has_property(prop="cardinality"))
        self.assertTrue(
            tutoring.getVariable().has_property_value(prop="cardinality", val="binary")
        )

        # Add assertions that pertain to effects sets
        linear_reg_es = None
        for es in effects:
            if es.to_dict() == DataForTests.expected_effects_set[2]:
                linear_reg_es = es
                break
        linear_reg_es.assert_property(prop="tolerate_correlation", val=True)

        kb = analysis.knowledge_base

        # because Effects Set generation may swap order of variables

        res = format_effect_set_constraint(
            effect_set=linear_reg_es, key="tolerate_correlation", val=True
        )
        if res == DataForTests.expected_tolerate_constraint_intelligence_first:
            self.assertNotEqual(
                res, DataForTests.expected_tolerate_constraint_tutoring_first
            )
        else:
            self.assertNotEqual(
                res, DataForTests.expected_tolerate_constraint_intelligence_first
            )
            self.assertEqual(
                res, DataForTests.expected_tolerate_constraint_tutoring_first
            )
        self.assertEqual(
            len(
                [
                    format_effect_set_constraint(
                        effect_set=linear_reg_es, key="tolerate_correlation", val=True
                    )
                ]
            ),
            1,
        )

    def test_get_all_assertions(self):
        analysis = ts.Tisane(task="explanation")

        # Add concepts
        test_score = ts.Concept("Test Score")
        intelligence = ts.Concept("Intelligence")
        tutoring = ts.Concept("Tutoring")
        concepts = [test_score, intelligence, tutoring]

        # Add relationships
        analysis.addRelationship(intelligence, test_score, "cause")
        analysis.addRelationship(tutoring, test_score, "cause")
        analysis.addRelationship(intelligence, tutoring, "correlate")

        # Specify data (schema)
        test_score.specifyData(dtype="numeric")
        intelligence.specifyData(dtype="numeric")
        tutoring.specifyData(
            dtype="nominal", categories=["After school", "Before school"]
        )

        # Generate effects sets
        effects = analysis.generate_effects_sets(
            ivs=[intelligence, tutoring], dv=test_score
        )

        # Add assertions that pertain to effects sets
        linear_reg_es = None
        for es in effects:
            if es.to_dict() == DataForTests.expected_effects_set[2]:
                linear_reg_es = es
                break
        linear_reg_es.assert_property(prop="tolerate_correlation", val=True)
        linear_reg_es.assert_property(prop="normal_residuals", val=True)
        linear_reg_es.assert_property(prop="homoscedastic_residuals", val=True)

        # Verify
        assertions = analysis.collect_assertions(linear_reg_es)
        for a in assertions:
            if a in DataForTests.expected_assertions_intelligence_first:
                self.assertFalse(a in DataForTests.expected_assertions_tutoring_first)
            else:
                self.assertTrue(a in DataForTests.expected_assertions_tutoring_first)
                self.assertFalse(
                    a in DataForTests.expected_assertions_intelligence_first
                )

    def test_query(self):
        analysis = ts.Tisane(task="explanation")

        # Add concepts
        test_score = ts.Concept("Test Score")
        intelligence = ts.Concept("Intelligence")
        tutoring = ts.Concept("Tutoring")
        concepts = [test_score, intelligence, tutoring]

        # Specify data (schema)
        test_score.specifyData(dtype="numeric")
        intelligence.specifyData(dtype="numeric")
        tutoring.specifyData(
            dtype="nominal", categories=["After school", "Before school"]
        )

        # Add relationships
        analysis.addRelationship(intelligence, test_score, "cause")
        analysis.addRelationship(tutoring, test_score, "cause")
        analysis.addRelationship(intelligence, tutoring, "correlate")

        # Generate effects sets
        effects = analysis.generate_effects_sets(
            ivs=[intelligence, tutoring], dv=test_score
        )

        # Add assertions that pertain to effects sets
        linear_reg_es = None
        for es in effects:
            if es.to_dict() == DataForTests.expected_effects_set[2]:
                linear_reg_es = es
                break
        linear_reg_es.assert_property(prop="tolerate_correlation", val=True)
        linear_reg_es.assert_property(prop="normal_residuals", val=True)
        linear_reg_es.assert_property(prop="homoscedastic_residuals", val=True)

        # Collect assertions
        assertions = analysis.collect_assertions(linear_reg_es)

        kb = analysis.knowledge_base
        res = kb.query(
            file_name="/Users/emjun/Git/tisane/tisane/asp/specific_constraints_test.lp",
            assertions=assertions,
        )
        valid_models = kb.construct_models_from_query_result(
            query_result=res, effect_set=linear_reg_es
        )

        self.assertEqual(len(valid_models), 1)
        self.assertTrue(isinstance(valid_models[0], LinearRegression))

    # TODO connect to the main file, test model selection (esp for all possible model variations)

    def test_dtor(self):
        # Test resetting or nulling out all the properties and tests!

        pass


class DataForTests:
    test_score = ts.Concept("Test Score")
    intelligence = ts.Concept("Intelligence")
    tutoring = ts.Concept("Tutoring")

    expected_effects_set = [
        {
            "dv": test_score.name,
            "main": set({intelligence.name}),
            "interaction": None,
            "mixed": None,
        },
        {
            "dv": test_score.name,
            "main": set({tutoring.name}),
            "interaction": None,
            "mixed": None,
        },
        {
            "dv": test_score.name,
            "main": set({tutoring.name, intelligence.name}),
            "interaction": None,
            "mixed": None,
        },
        {
            "dv": test_score.name,
            "main": set({tutoring.name, intelligence.name}),
            "interaction": set({(intelligence.name, tutoring.name)}),
            "mixed": None,
        },
        {
            "dv": test_score.name,
            "main": set({intelligence.name}),
            "interaction": set({(intelligence.name, tutoring.name)}),
            "mixed": None,
        },
        {
            "dv": test_score.name,
            "main": set({tutoring.name}),
            "interaction": set({(intelligence.name, tutoring.name)}),
            "mixed": None,
        },
        {
            "dv": test_score.name,
            "main": None,
            "interaction": set({(intelligence.name, tutoring.name)}),
            "mixed": None,
        },
    ]

    expected_tolerate_constraint_intelligence_first = (
        "tolerate_correlation(intelligence,tutoring)."
    )
    expected_tolerate_constraint_tutoring_first = (
        "tolerate_correlation(tutoring,intelligence)."
    )

    expected_assertions_intelligence_first = [
        "variable(intelligence).",
        "variable(tutoring).",
        "variable(test_score).",
        "normal_residuals(intelligence,tutoring,test_score).",
        "homoscedastic_residuals(intelligence,tutoring,test_score).",
        "tolerate_correlation(intelligence,tutoring).",
        "numeric(test_score).",
        "numeric(intelligence).",
        "categorical(tutoring).",
        "binary(tutoring).",
    ]

    expected_assertions_tutoring_first = [
        "normal_residuals(tutoring,intelligence,test_score).",
        "homoscedastic_residuals(tutoring,intelligence,test_score).",
        "tolerate_correlation(tutoring,intelligence).",
    ]
