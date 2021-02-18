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
                ForAll([x0, x1], Xor(Interaction(x0, x1), NoInteraction(x0, x1))),
                # TODO: ADD RULE FOR CANT INTERACTION X with Y?
            ]

    # Store all logical rules internally for now, may want to modularize in separate objects...
    def ground_rules(self, dv_const: Const, main_effects: SeqSort, interactions: SeqSort, **kwargs): 
        
        self.graph_rules = [
            ForAll([x], Implies(Contains(main_effects, Unit(x)), Xor(Cause(x, dv_const), Correlate(x, dv_const)))),
        ] 

        if 'possible_interactions' in kwargs: 
            if kwargs['possible_interactions']: 
                self.graph_rules += self.effect_rules
        if interactions is not None: 
                self.graph_rules.append(ForAll([x0, x1, i], Implies(And(Contains(interactions, Unit(i)), And(IsMember(x0, i), IsMember(x1, i))), Xor(Cause(x0, x1), Correlate(x0, x1))))),

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
            ForAll([x], Implies(Log(x), NumericDataType(x))), 
            ForAll([x], Implies(Squareroot(x), NumericDataType(x))),  # Sqrt is predefined in Z3
            ForAll([x], Implies(LogLog(x), CategoricalDataType(x))),
            ForAll([x], Implies(Probit(x), CategoricalDataType(x))), 
            ForAll([x], Implies(Logit(x), CategoricalDataType(x))),
            # From data type to possible transformations...
            ForAll([x], Xor(Transformation(x), NoTransformation(x))),
            ForAll([x], Implies(Transformation(x), Xor(NumericTransformation(x),CategoricalTransformation(x)))),
            ForAll([x], Implies(NumericTransformation(x), Xor(Log(x), Squareroot(x)))),
            ForAll([x], Implies(CategoricalTransformation(x), Xor(Xor(LogLog(x), Probit(x)), Logit(x))))
        ]

        self.variance_functions_rules = [
            ForAll([x], Implies(Gaussian(x), NumericDataType(x))),
            ForAll([x], Implies(Binomial(x), BinaryDataType(x))),
            ForAll([x], Implies(Multinomial(x), CategoricalDataType(x))),
        ]

KB = KnowledgeBase()