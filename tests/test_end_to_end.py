import tisane as ts
from tisane.effect_set import EffectSet, MainEffect, InteractionEffect, MixedEffect
from tisane.statistical_model import StatisticalModel, LinearRegression

import unittest

class EndToEndTests(unittest.TestCase): 

    def test_sample_tisane_program(self): 
        analysis = ts.Tisane(task="explanation")

        # Add conceptual information 
        test_score = ts.Concept("Test Score")
        intelligence = ts.Concept("Intelligence")
        tutoring = ts.Concept("Tutoring")
    
        # Add relationships
        # analysis.addRelationship(intelligence, test_score, "cause")
        # analysis.addRelationship(tutoring, test_score, "cause")
        # analysis.addRelationship(intelligence, tutoring, "correlate")
        analysis.relate(intelligence, 'cause', test_score)
        analysis.relate(tutoring, 'cause', test_score)
        analysis.relate(intelligence, 'correlate', tutoring)

        # Generate effects sets
        effects = analysis.generate_effects_sets(ivs=[intelligence, tutoring], dv=test_score)

        # Specify data (schema) --> generates assertions about variables/data
        # If have data: automatically detect and verify these based on uploaded data
        test_score.specifyData(dtype="numeric")
        intelligence.specifyData(dtype="numeric")
        tutoring.specifyData(dtype="nominal", categories=["After school", "Before school"])

        # THIS MIMICS END-USERS SELECTING A SET OF EFFECTS TO MODEL 
        linear_reg_es = None
        for es in effects: 
            if es.to_dict() == DataForTests.expected_effects_set[2]: 
                linear_reg_es = es
                break
        # Add assertions that pertain to effects sets
        linear_reg_es.assert_property(prop="tolerate_correlation", val=True)
        linear_reg_es.assert_property(prop="normal_residuals", val=True)
        linear_reg_es.assert_property(prop="homoscedastic_residuals", val=True)

        valid_models = analysis.start_model(effect_set=linear_reg_es) 
        print(valid_models) # "Linear Regression"
        self.assertTrue(len(valid_models), 1)
        model = valid_models[0]
        self.assertTrue(isinstance(model, LinearRegression))

        for v in valid_models: 
            v.to_script()

    def test_sample(self): 
        aptitude = ts.Concept("Aptitude")
        intelligence = ts.Concept("Intelligence")
        tutoring = ts.Concept("Tutoring")

        # Conceptual: RQ - Analysis
        # intelligence.cause(tutoring)
        # tutoring.cause(aptitude)

        # Data: Experimental Design - Analysis
        # IDEA: Visual grammar for experimental design  -- Grammar of experimental design?
        """
        - units of observation 
        - structure: nesting, randomize
        - manipulate (input, configuration) vs. measure (outcome) 
        - block 
        - workflow? 
        - Fully factorial vs. partial factorial designs -- should be some structure to control this?

        unit=student
        student.nested_in(class)
        class.nested_in(tutoring)
        assign={tutoring} # fixed effects
        measure={age, gender} # random effects


        ## Naturally there is some overlap between conceptual and experimental design declarations.
        ## There may be ways to reduce or remove this verbosity/duplication. 
        
        # TODO: Same conceptual relationships for all Experimental Designs?
        # TODO: Forward and backward inference for all three sides of triangle?

        # Experiment with 2 groups. 
        # Students who either receive some tutoring or no tutoring. 
        # Explain impact of tutoring on aptitude test. 

        unit=Student # row in tidy data
        Tutoring.levels = ["Tutoring", "No tutoring"] # could infer from data schema
        Student.nested_in(Tutoring)
        outcome={Aptitude}
        fixed={Tutoring} # could be "assign" instead of "fixed", assume that these are related to/apply to Unit
        random={ID, Age, Gender, Intelligence} # could be "observe" instead of "random" -- not sure what this does to observational studies...

        # Experiment with 3 groups. 
        # Students who receive Before-school tutoring, After-school tutoring, or no tutoring. 
        # Explain impact of tutoring on aptitude test. 

        unit=Student # row in tidy data
        Tutoring.levels = ["Before-school", "After-school", "No tutoring"] # could infer from data schema
        Student.nested_in(Tutoring)
        outcome={Aptitude}
        fixed={Tutoring}
        random={ID, Age, Gender, Intelligence}

        # Experiment with 2 groups where one group has two options. 
        # Students who receive Tutoring vs. No tutoring. Students who do receive Tutoring are assigned to Before-school or After-school. 
        # Explain impact of tutoring on aptitude test. 
        
        unit=Student # row in tidy data
        Tutoring.levels = ["Tutoring", "No tutoring"] # could infer from data schema
        Tutoring_time.levels = ["Before-school", "After-school"] # could infer from data schema
        Tutoring_time.nested_in(Tutoring)
        Student.nested_in(Tutoring) # implies nested in Tutoring_time
        outcome={Aptitude}
        fixed={Tutoring, Tutoring_Time} # Tutoring_Time does not have to be fixed
        random={ID, Age, Gender, Intelligence}

        # Experiment with 2 groups where one group has two options. 
        # Students who receive Tutoring vs. No tutoring. Students who do receive Tutoring can choose Before-school or After-school. 
        # Explain impact of tutoring on aptitude test. 

        unit=Student # row in tidy data
        Tutoring.levels = ["Tutoring", "No tutoring"] # could infer from data schema
        Tutoring_time.levels = ["Before-school", "After-school"] # could infer from data schema
        Tutoring_time.nested_in(Tutoring)
        Student.nested_in(Tutoring) # implies nested in Tutoring_time
        outcome={Aptitude}
        fixed={Tutoring} # because can choose Tutoring_time, Tutoring time is no longer fixed
        random={ID, Age, Gender, Intelligence, Tutoring_Time}

        # Experiment with 2 groups. 
        # Students in classes where entire classes either receive some tutoring or no tutoring. 
        # Explain impact of tutoring on aptitude test. 
        
        unit=Student # row in tidy data
        Tutoring.levels = ["Tutoring", "No tutoring"] # could infer from data schema
        Student.nested_in(Classes) 
        Classes.nested_in(Tutoring)
        outcome={Aptitude}
        fixed={Tutoring} 
        random={ID, Age, Gender, Intelligence, Class}

        # Experiment with 2 groups. 
        # Students assigned to classes where entire classes either receive some tutoring or no tutoring. 
        # Explain impact of class on aptitude test. 
        
        unit=Student # row in tidy data
        Tutoring.levels = ["Tutoring", "No tutoring"] # could infer from data schema
        Student.nested_in(Classes) 
        Classes.nested_in(Tutoring)
        outcome={Aptitude}
        fixed={Tutoring, Class} # because assigned to Class
        random={ID, Age, Gender, Intelligence}
        # This would be same as explaining impact of tutoring on aptitude test. 
        # TODO: Example of where our system might help identify flaw or redundancy in experimental design, both class and tutoring should not be in stat model

        # Experiment with 3 groups. 
        # Students in classes where entire classes either receive Before-school tutoring, After-school tutoring, or no tutoring. 
        # Explain impact of tutoring on aptitude test. 

        unit=Student # row in tidy data
        Tutoring.levels = ["Tutoring", "No tutoring"] # could infer from data schema
        Tutoring_time.levels = ["Before-school", "After-school"]
        Tutoring_time.nested_in(Tutoring)
        Student.nested_in(Classes) 
        Classes.nested_in(Tutoring) # implies nested in Tutoring_time
        outcome={Aptitude}
        fixed={Tutoring, Tutoring_time} 
        random={ID, Age, Gender, Intelligence, Class} # because not assigned to Class

        # Experiment wih 3 groups. 
        # Students in classes where entire classes either receive Before-school tutoring, After-school tutoring, or no tutoring. 
        # Explain impact of tutoring on aptitude test. 
        # If unit is Class, have to take mean over students? Unit should be different than data row? If different, have to elicit some mapping from unit to row (data transformation)

        unit=Class # spans multiple rows in tidy data - maybe require that unit corresponds to row of tidy data planning to collect?
        Tutoring.levels = ["Tutoring", "No tutoring"] # could infer from data schema
        Tutoring_time.levels = ["Before-school", "After-school"]
        Tutoring_time.nested_in(Tutoring)
        Student.nested_in(Classes) 
        Classes.nested_in(Tutoring) # implies nested in Tutoring_time
        outcome={Aptitude}
        fixed={Tutoring, Tutoring_time} 
        random={ID, Age, Gender, Intelligence, Class} # because not assigned to Class
        """


    def test_generate_effects_sets(self):
        analysis = ts.Tisane(task="explanation") # analysis has one task

        test_score = ts.Concept("Test Score")
        intelligence = ts.Concept("Intelligence")
        tutoring = ts.Concept("Tutoring")
        concepts = [test_score, intelligence, tutoring]

        analysis.addRelationship(intelligence, test_score, "cause")
        analysis.addRelationship(tutoring, test_score, "cause")
        analysis.addRelationship(intelligence, tutoring, "correlate")

        effects = analysis.generate_effects_sets(ivs=[intelligence, tutoring], dv=test_score)
        
        # check total number of effect sets 
        self.assertEqual(len(effects), 7)
        # check each effect set is valid
        for es in effects: 
            es_dict = es.to_dict()
            self.assertTrue(es_dict in DataForTests.expected_effects_set)    

        
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