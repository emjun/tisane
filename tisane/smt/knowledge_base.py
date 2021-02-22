from tisane.smt.declare_constraints import *
from tisane.smt.helpers import *
from tisane.smt.rules import *

from z3 import *

class KnowledgeBase(object): 
    def ground_effects_rules(self, dv_const: Const): 
        self.effects_rules = [
                ForAll([x], Xor(MainEffect(x, dv_const), NoMainEffect(x, dv_const))),
                # ForAll([x0, x1, i], Implies(And(Contains(interactions, Unit(i)), And(IsMember(x0, i), IsMember(x1, i))), Contains(main_effects, Unit(x)))),
                # ForAll([x0, x1], Implies(Interaction(x0, x1), And(Contains(interactions, Unit(x0)), Contains(interactions, Unit(x1))))),
                # TODO: Expand this for multiple xs for n-way interactions
                ForAll([xs], Xor(Interaction(xs), NoInteraction(xs))),
                # TODO: ADD RULE FOR CANT INTERACTION X with Y?
            ]

    # Store all logical rules internally for now, may want to modularize in separate objects...
    def ground_rules(self, dv_const: Const, main_effects: SeqSort, interactions: SeqSort, **kwargs): 
        
        self.graph_rules = [
            ForAll([x], Implies(Contains(main_effects, Unit(x)), Xor(Cause(x, dv_const), Correlate(x, dv_const)))),
            ForAll([x0, x1], Implies(Cause(x0, x1), Not(Cause(x1, x0)))), # If x0 causes x1, x1 cannot cause x0
            ForAll([x0, x1], Xor(Cause(x0, x1), Correlate(x0, x1))), # If x0 causes x1, x1 cannot cause x0
        ] 

        

        self.data_type_rules = [
            ForAll([x], Xor(CategoricalDataType(x), NumericDataType(x))), 
            ForAll([x], Implies(CategoricalDataType(x), Xor(OrdinalDataType(x), NominalDataType(x)))),
            ForAll([x], Implies(CategoricalDataType(x), Xor(BinaryDataType(x), Multinomial(x)))),
            ForAll([x], Implies(BinaryDataType(x), CategoricalDataType(x))),
            ForAll([x], Implies(Multinomial(x), CategoricalDataType(x))),
            ForAll([x], Implies(NominalDataType(x), CategoricalDataType(x))),
            ForAll([x], Implies(OrdinalDataType(x), CategoricalDataType(x))),
        ]

        self.data_transformation_rules = [
            ForAll([x], Implies(Identity(x), NumericDataType(x))),
            ForAll([x], Implies(LogTransform(x), NumericDataType(x))), 
            ForAll([x], Implies(SquarerootTransform(x), NumericDataType(x))),  # Sqrt is predefined in Z3
            ForAll([x], Implies(LogLogTransform(x), CategoricalDataType(x))),
            ForAll([x], Implies(ProbitTransform(x), CategoricalDataType(x))), 
            ForAll([x], Implies(LogitTransform(x), CategoricalDataType(x))),
            # From data type to possible transformations...
            ForAll([x], Xor(Transformation(x), NoTransformation(x))),
            ForAll([x], Implies(Transformation(x), Xor(NumericTransformation(x), CategoricalTransformation(x)))),
            ForAll([x], Implies(NumericTransformation(x), Xor(LogTransform(x), SquarerootTransform(x)))),
            # Can be LogLog OR Probit OR Logit
            ForAll([x], Implies(CategoricalTransformation(x), Xor(LogLogTransform(x), ProbitTransform(x)))),
            ForAll([x], Implies(CategoricalTransformation(x), Xor(LogLogTransform(x), LogitTransform(x)))),
            ForAll([x], Implies(CategoricalTransformation(x), Xor(ProbitTransform(x), LogitTransform(x)))),
            ForAll([x], Implies(NoTransformation(x), Not(Transformation(x)))),
        ]

        self.variance_functions_rules = [
            ForAll([x], Implies(Gaussian(x), NumericDataType(x))),
            ForAll([x], Implies(Binomial(x), BinaryDataType(x))),
            ForAll([x], Implies(Multinomial(x), CategoricalDataType(x))),
        ]

KB = KnowledgeBase()