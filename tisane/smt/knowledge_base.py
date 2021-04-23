from tisane.smt.rules import *

from z3 import *

class KnowledgeBase(object): 
    def ground_effects_rules(self, dv_const: Const): 
        self.effects_rules = [
                ForAll([x], Xor(FixedEffect(x, dv_const), NoFixedEffect(x, dv_const))),
                ForAll([xs], Xor(Interaction(xs), NoInteraction(xs))),
                ForAll([x0, x1], Xor(RandomSlopeEffect(x0, x1), NoRandomSlopeEffect(x0, x1))),
                ForAll([x], Xor(RandomInterceptEffect(x), NoRandomInterceptEffect(x))),
                ForAll([x0, x1], Xor(CorrelatedRandomSlopeInterceptEffects(x0, x1), UncorrelatedRandomSlopeInterceptEffects(x0, x1))),
                ForAll([x0, x1], Implies(CorrelatedRandomSlopeInterceptEffects(x0, x1), And([RandomSlopeEffect(x0, x1), RandomInterceptEffect(x1)]))) # Assumes that x1 is the grouping variable
                # TODO: ADD RULE FOR CANT INTERACTION X with Y?
            ]

    def ground_family_rules(self, dv_const: Const): 
        self.family_rules = [
            # Xor(GaussianFamily(dv_const), InverseGaussianFamily(dv_const), PoissonFamily(dv_const), GammaFamily(dv_const), BinomialFamily(dv_const), NegativeBinomialFamily(dv_const), MultinomialFamily(dv_const))
            Xor(GaussianFamily(dv_const), InverseGaussianFamily(dv_const)),
            Xor(GaussianFamily(dv_const), PoissonFamily(dv_const)),
            Xor(GaussianFamily(dv_const), GammaFamily(dv_const)),
            # Xor(InverseGaussianFamily(dv_const), PoissonFamily(dv_const)),
            # Xor(InverseGaussianFamily(dv_const), GammaFamily(dv_const)),
            # Xor(PoissonFamily(dv_const), GammaFamily(dv_const))
            # Xor(Xor(GaussianFamily(dv_const), InverseGaussianFamily(dv_const)), PoissonFamily(dv_const))
            Xor(BinomialFamily(dv_const), NegativeBinomialFamily(dv_const)),
            Xor(BinomialFamily(dv_const), MultinomialFamily(dv_const))
        ]

    def ground_data_transformation_rules(self, dv_const: Const): 
        self.default_family_to_transformation = [
            Implies(GaussianFamily(dv_const), IdentityTransform(dv_const)),

            Implies(InverseGaussianFamily(dv_const), InverseSquaredTransform(dv_const)),

            Implies(PoissonFamily(dv_const), LogTransform(dv_const)),

            Implies(GammaFamily(dv_const), InverseTransform(dv_const)),
            
            Implies(TweedieFamily(dv_const), LogTransform(dv_const)),

            Implies(BinomialFamily(dv_const), LogitTransform(dv_const)),

            Implies(NegativeBinomialFamily(dv_const), LogTransform(dv_const)),
        ]

        self.family_to_transformation_rules = [
            Implies(GaussianFamily(dv_const), LogTransform(dv_const)), 
            Implies(GaussianFamily(dv_const), SquarerootTransform(dv_const)),
            Implies(GaussianFamily(dv_const), IdentityTransform(dv_const)),
            
            Implies(InverseGaussianFamily(dv_const), InverseSquaredTransform(dv_const)),
            Implies(InverseGaussianFamily(dv_const), InverseTransform(dv_const)), 
            Implies(InverseGaussianFamily(dv_const), LogTransform(dv_const)), 
            Implies(InverseGaussianFamily(dv_const), IdentityTransform(dv_const)),

            Implies(PoissonFamily(dv_const), LogTransform(dv_const)),
            Implies(PoissonFamily(dv_const), SquarerootTransform(dv_const)),
            Implies(PoissonFamily(dv_const), IdentityTransform(dv_const)),
            
            Implies(GammaFamily(dv_const), LogTransform(dv_const)),
            Implies(GammaFamily(dv_const), InverseTransform(dv_const)),
            Implies(GammaFamily(dv_const), IdentityTransform(dv_const)),
        
            Implies(TweedieFamily(dv_const), LogTransform(dv_const)),
            Implies(TweedieFamily(dv_const), PowerTransform(dv_const)),

            Implies(BinomialFamily(dv_const), LogitTransform(dv_const)),
            Implies(BinomialFamily(dv_const), ProbitTransform(dv_const)),
            Implies(BinomialFamily(dv_const), CauchyTransform(dv_const)),
            Implies(BinomialFamily(dv_const), LogTransform(dv_const)),
            Implies(BinomialFamily(dv_const), CLogLogTransform(dv_const)),

            Implies(NegativeBinomialFamily(dv_const), LogTransform(dv_const)),
            Implies(NegativeBinomialFamily(dv_const), CLogLogTransform(dv_const)),
            Implies(NegativeBinomialFamily(dv_const), NegativeBinomialTransform(dv_const)),
            Implies(NegativeBinomialFamily(dv_const), IdentityTransform(dv_const)),
            # Power not yet supported in statsmodels
            # Implies(NegativeBinomialFamily(dv_const), PowerTransform(dv_const)),
            
            # Multinomial family is not supported in statsmodels for GLM
            # Implies(MultinomialFamily(dv_const), IdentityTransform(dv_const))
        ]

        self.data_transformation_rules = [
            # For Gaussian Family
            Or(And([LogTransform(dv_const), Not(SquarerootTransform(dv_const)), Not(IdentityTransform(dv_const)), GaussianFamily(dv_const)]),
                And([SquarerootTransform(dv_const), Not(LogTransform(dv_const)), Not(IdentityTransform(dv_const)), GaussianFamily(dv_const)]),
                And([IdentityTransform(dv_const), Not(LogTransform(dv_const)), Not(SquarerootTransform(dv_const)), GaussianFamily(dv_const)])),
            # For Inverse Gaussian Family
            Or(And([LogTransform(dv_const), Not(InverseTransform(dv_const)), Not(InverseSquaredTransform(dv_const)), Not(IdentityTransform(dv_const)), InverseGaussianFamily(dv_const)]),
                And([InverseTransform(dv_const), Not(LogTransform(dv_const)), Not(InverseSquaredTransform(dv_const)), Not(IdentityTransform(dv_const)), InverseGaussianFamily(dv_const)]),
                And([InverseSquaredTransform(dv_const), Not(LogTransform(dv_const)), Not(InverseTransform(dv_const)), Not(IdentityTransform(dv_const)), InverseGaussianFamily(dv_const)]),
                And([IdentityTransform(dv_const), Not(LogTransform(dv_const)), Not(InverseSquaredTransform(dv_const)), Not(InverseTransform(dv_const)), InverseGaussianFamily(dv_const)])),
            # For Poisson Family
            Or(And([LogTransform(dv_const), Not(SquarerootTransform(dv_const)), Not(IdentityTransform(dv_const)), PoissonFamily(dv_const)]),
                And([SquarerootTransform(dv_const), Not(LogTransform(dv_const)), Not(IdentityTransform(dv_const)), PoissonFamily(dv_const)]),
                And([IdentityTransform(dv_const), Not(LogTransform(dv_const)), Not(SquarerootTransform(dv_const)), PoissonFamily(dv_const)])),
            # For Gamma Family
            Or(And([LogTransform(dv_const), Not(InverseTransform(dv_const)), Not(IdentityTransform(dv_const)), GammaFamily(dv_const)]),
                And([InverseTransform(dv_const), Not(LogTransform(dv_const)), Not(IdentityTransform(dv_const)), GammaFamily(dv_const)]),
                And([IdentityTransform(dv_const), Not(LogTransform(dv_const)), Not(InverseTransform(dv_const)), GammaFamily(dv_const)])),
            # For Tweedie Family
            Or(And([LogTransform(dv_const), Not(PowerTransform(dv_const)), TweedieFamily(dv_const)]),
                And([PowerTransform(dv_const), Not(LogTransform(dv_const)), TweedieFamily(dv_const)])),
            # For Binomial Family
            Or(And([LogTransform(dv_const), Not(ProbitTransform(dv_const)), Not(LogitTransform(dv_const)), Not(CauchyTransform(dv_const)), Not(CLogLogTransform(dv_const)), BinomialFamily(dv_const)]),
                And([ProbitTransform(dv_const), Not(LogTransform(dv_const)), Not(LogitTransform(dv_const)), Not(CauchyTransform(dv_const)), Not(CLogLogTransform(dv_const)), BinomialFamily(dv_const)]),
                And([LogitTransform(dv_const), Not(LogTransform(dv_const)), Not(ProbitTransform(dv_const)), Not(CauchyTransform(dv_const)), Not(CLogLogTransform(dv_const)), BinomialFamily(dv_const)]),
                And([CauchyTransform(dv_const), Not(LogTransform(dv_const)), Not(LogitTransform(dv_const)), Not(ProbitTransform(dv_const)), Not(CLogLogTransform(dv_const)), BinomialFamily(dv_const)]),
                And([CLogLogTransform(dv_const), Not(LogTransform(dv_const)), Not(ProbitTransform(dv_const)), Not(LogitTransform(dv_const)), Not(CauchyTransform(dv_const)), BinomialFamily(dv_const)])),
            # For Negative Binomial Family
            Or(And([LogTransform(dv_const), Not(NegativeBinomialTransform(dv_const)), Not(CLogLogTransform(dv_const)), Not(IdentityTransform(dv_const)), NegativeBinomialFamily(dv_const)]),
                And([NegativeBinomialTransform(dv_const), Not(LogTransform(dv_const)), Not(CLogLogTransform(dv_const)), Not(IdentityTransform(dv_const)), NegativeBinomialFamily(dv_const)]),
                And([CLogLogTransform(dv_const), Not(LogTransform(dv_const)), Not(NegativeBinomialTransform(dv_const)), Not(IdentityTransform(dv_const)), NegativeBinomialFamily(dv_const)]),
                And([IdentityTransform(dv_const), Not(LogTransform(dv_const)), Not(NegativeBinomialTransform(dv_const)), Not(CLogLogTransform(dv_const)), NegativeBinomialFamily(dv_const)])),
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
            ForAll([x], Implies(CategoricalDataType(x), Xor(NominalDataType(x), OrdinalDataType(x)))),

            # ForAll([x], Implies(NominalDataType(x), Not(OrdinalDataType(x)))),
            # ForAll([x], Implies(NominalDataType(x), Not(NumericDataType(x)))),
            # ForAll([x], Implies(NumericDataType(x), And(Not(OrdinalDataType(x), Not(NominalDataType(x)))))),

            # ForAll([x], Implies(OrdinalDataType(x), CategoricalDataType(x))),
            # ForAll([x], Implies(NominalDataType(x), CategoricalDataType(x))),
            
            # ForAll([x], Implies(CategoricalDataType(x), Xor(OrdinalDataType(x), NominalDataType(x)))),
            ForAll([x], Implies(CategoricalDataType(x), Xor(BinaryDataType(x), Multinomial(x)))),
            ForAll([x], Implies(BinaryDataType(x), CategoricalDataType(x))),
            ForAll([x], Implies(Multinomial(x), CategoricalDataType(x))),
            ForAll([x], Implies(NominalDataType(x), CategoricalDataType(x))),
            ForAll([x], Implies(OrdinalDataType(x), CategoricalDataType(x))),
        ]

        self.data_transformation_rules = [
            ForAll([x], Implies(IdentityTransform(x), NumericDataType(x))),
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