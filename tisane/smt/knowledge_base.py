from tisane.smt.declare_constraints import *
from tisane.smt.helpers import *
from tisane.smt.rules import *

from z3 import *

class KnowledgeBase(object): 

    # Store all logical rules internally for now, may want to modularize in separate objects...
    def ground_rules(self, dv_const: Const, main_effects: SeqSort, interactions: SeqSort, **kwargs): 
        
        self.graph_rules = [
            ForAll([x], Implies(Contains(main_effects, Unit(x)), Xor(Cause(x, dv_const), Correlate(x, dv_const)))),
        ] 
        interaction_rules = [
            # ForAll([x0, x1, i], Implies(And(Contains(interactions, Unit(i)), And(IsMember(x0, i), IsMember(x1, i))), Contains(main_effects, Unit(x)))),
            # ForAll([x0, x1], Implies(Interaction(x0, x1), And(Contains(interactions, Unit(x0)), Contains(interactions, Unit(x1))))),
            ForAll([x0, x1], Xor(Interaction(x0, x1), NoInteraction(x0, x1))),
            # TODO: ADD RULE FOR CANT INTERACTION X with Y?
        ]

        if 'possible_interactions' in kwargs: 
            if kwargs['possible_interactions']: 
                self.graph_rules += interaction_rules
        if interactions is not None: 
                self.graph_rules.append(ForAll([x0, x1, i], Implies(And(Contains(interactions, Unit(i)), And(IsMember(x0, i), IsMember(x1, i))), Xor(Cause(x0, x1), Correlate(x0, x1))))),

        self.data_type_rules = [
            ForAll([x], Xor(Categorical(x), Numeric(x))), 
            ForAll([x], Implies(Categorical(x), Xor(Ordinal(x), Nominal(x)))),
            ForAll([x], Implies(Categorical(x), Xor(Binary(x), Multinomial(x)))),
            ForAll([x], Implies(Binary(x), Categorical(x))),
            ForAll([x], Implies(Multinomial(x), Categorical(x))),
            ForAll([x], Implies(Nominal(x), Categorical(x))),
            ForAll([x], Implies(Ordinal(x), Categorical(x))),
        ]

        self.data_transformation_rules = [
            ForAll([x], Implies(Identity(x), Numeric(x))),
            ForAll([x], Implies(Log(x), Numeric(x))), 
            # ForAll([x], Implies(Sqrt(x), Numeric(x))),  # Sqrt is predefined in Z3
            ForAll([x], Implies(LogLog(x), Categorical(x))),
            ForAll([x], Implies(LogLog(x), Categorical(x))),
            ForAll([x], Implies(Probit(x), Categorical(x))), 
            ForAll([x], Implies(Logit(x), Categorical(x)))
        ]

        self.variance_functions_rules = [
            ForAll([x], Implies(Gaussian(x), Numeric(x))),
            ForAll([x], Implies(Binomial(x), Binary(x))),
            ForAll([x], Implies(Multinomial(x), Categorical(x))),
        ]

KB = KnowledgeBase()