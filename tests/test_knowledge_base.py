import tisane as ts
from tisane.asp.knowledge_base import KnowledgeBase
from tisane.effect_set import EffectSet

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

    def test_variable_get_assertions(self):
        analysis = ts.Tisane(task="explanation")

        # Add concepts
        test_score = ts.Concept("Test Score")
        intelligence = ts.Concept("Intelligence")
        tutoring = ts.Concept("Tutoring")
        concepts = [test_score, intelligence, tutoring]

        # Specify data (schema)
        test_score.specifyData(dtype="numeric")
        intelligence.specifyData(dtype="numeric")
        tutoring.specifyData(dtype="nominal", categories=["After school", "Before school"])

        # Some assertions are inferred from data schema, see above
        self.assertTrue(test_score.getVariable().has_property_value(prop="dtype", val="numeric"))
        self.assertTrue(intelligence.getVariable().has_property_value(prop="dtype", val="numeric"))
        self.assertTrue(tutoring.getVariable().has_property_value(prop="dtype", val="nominal"))

        self.assertFalse(test_score.getVariable().has_property(prop="cardinality"))
        self.assertFalse(intelligence.getVariable().has_property(prop="cardinality"))
        self.assertTrue(tutoring.getVariable().has_property_value(prop="cardinality", val="binary"))

        kb = analysis.knowledge_base

        # This tells us that as long as we pass the correct parameters, the ASP constraints for variables are generated correctly. 
        self.assertEqual(kb.get_concept_variable_constraint(concept=test_score, key='dtype', val='numeric'), "numeric(test_score).")
        self.assertEqual(kb.get_concept_variable_constraint(concept=intelligence, key='dtype', val='numeric'), "numeric(intelligence).")
        self.assertEqual(kb.get_concept_variable_constraint(concept=tutoring, key='dtype', val='nominal'), "nominal(tutoring).")
        self.assertEqual(kb.get_concept_variable_constraint(concept=tutoring, key='cardinality', val='binary'), "binary(tutoring).")

    def test_effect_set_get_assertions(self):
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
        tutoring.specifyData(dtype="nominal", categories=["After school", "Before school"])
        # tutoring.specifyData(dtype="nominal", categories=["After school", "Before school", "None"])

        # Get valid statistical models
        # Assert statistical properties needed for linear regression
        # Generate effects sets
        effects = analysis.generate_effects_sets(ivs=[intelligence, tutoring], dv=test_score)

        # Add individual variable assertions
        # Some assertions are inferred from data schema, see above
        self.assertTrue(test_score.getVariable().has_property_value(prop="dtype", val="numeric"))
        self.assertTrue(intelligence.getVariable().has_property_value(prop="dtype", val="numeric"))
        self.assertTrue(tutoring.getVariable().has_property_value(prop="dtype", val="nominal"))
        
        self.assertFalse(test_score.getVariable().has_property(prop="cardinality"))
        self.assertFalse(intelligence.getVariable().has_property(prop="cardinality"))
        self.assertTrue(tutoring.getVariable().has_property_value(prop="cardinality", val="binary"))

        # Add assertions that pertain to effects sets
        linear_reg_es = None
        for es in effects: 
            if es.to_dict() == DataForTests.expected_effects_set[2]: 
                linear_reg_es = es
                break
        linear_reg_es.assert_property(prop="tolerate_correlation", val=True)
        
        kb = analysis.knowledge_base

        self.assertEqual(kb.get_effect_set_constraint(effect_set=linear_reg_es, key='tolerate_correlation', val=True), "tolerate_correlation(tutoring,intelligence).")

    
    # def test_query(self):
    #     test_score = ts.Concept("Test Score")
    #     intelligence = ts.Concept("Intelligence")
    #     tutoring = ts.Concept("Tutoring")

    #     test_score.specifyData(dtype="numeric") # Score 0 - 100 
    #     intelligence.specifyData(dtype="numeric") # IQ score 
    #     tutoring.specifyData(dtype="nominal", categories=["afterschool", "none"])

    #     ivs = [intelligence, tutoring]
    #     dvs = [test_score]
        
    #     kb = KnowledgeBase()

    #     kb.query('/Users/emjun/Git/tisane/tisane/asp/specific_constraints_test.lp')

# TODO connect to the main file, test model selection (esp for all possible model variations)

    def test_dtor(self): 
        # Test resetting or nulling out all the properties and tests! 

        pass


class DataForTests: 
    test_score = ts.Concept("Test Score")
    intelligence = ts.Concept("Intelligence")
    tutoring = ts.Concept("Tutoring")

    expected_effects_set = [
        {'dv': test_score.name, 'main': set({intelligence.name}), 'interaction': None, 'mixed': None},
        {'dv': test_score.name, 'main': set({tutoring.name}), 'interaction': None, 'mixed': None},
        {'dv': test_score.name, 'main': set({tutoring.name, intelligence.name}), 'interaction': None, 'mixed': None},
        {'dv': test_score.name, 'main': set({tutoring.name, intelligence.name}), 'interaction': set({(intelligence.name, tutoring.name)}), 'mixed': None},
        {'dv': test_score.name, 'main': set({intelligence.name}), 'interaction': set({(intelligence.name, tutoring.name)}), 'mixed': None},
        {'dv': test_score.name, 'main': set({tutoring.name}), 'interaction': set({(intelligence.name, tutoring.name)}), 'mixed': None},
        {'dv': test_score.name, 'main': None, 'interaction': set({(intelligence.name, tutoring.name)}), 'mixed': None},
    ]