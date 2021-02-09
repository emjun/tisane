Logical Rules I want to encode in the Knowledge Base (using Z3)

## Model Explanation 
1. If Xs "models" Y, Xs "explains" Y. In other words, Models(Xs, Y) == Explains(Xs, Y)
Implies(Models(Xs, Y), Explains(Xs, Y))
Models(Xs, Y) \and Explains(Xs, Y)
2. If Xs "models"/"explains" Y, Y is-a Predicted
Implies(Models(Xs, Y), IsPredicted(Y))
Models(Xs, Y) \and IsPredicted(Y)
3. If Xs "models"/"explains" Y, Every X in Xs is-a Predictor
Implies(Models(Xs, Y), And(Contains(Xs, X), IsPredictor(X)))
Models(Xs, Y) \and IsPredictor(X1) \and IsPredictor(X2)

Main effects, No interactions
Implies(Main_effects(X1), Xor(Cause(X1, Y), Correlate(X1, Y)))
Implies(Interaction(X1, X2), Xor(Cause(X1, X2), Correlate(X1, X2)))

## Variable Relationship Graph 
4. For every X that is-a Predictor, X "correlates" with Y OR X "causes" Y. 
    - For every X in Xs (Xs "models"/"explains" Y), it must either "correlate" with OR "cause Y
\and Xor(Correlate(X, Y), Cause(X, Y)) \and .... (for all Xs)
5. For every X that is-a Predictor, X _may_ also "correlate" with OR "cause" any other X. 
Implies(Correlate(X1, X2), Interaction(X1, X2))
\and Correlate(X1, X2) -- for interactions only??

6. If Y is-a Predicted, Y canNOT "correlate" with any X in Xs AND canNOT "cause" any other X in Xs. 
\and Not(Cause(Y, X1)) \and Not(Cause(Y, X2)) \and ...

## Data schema
7. Every X in Xs and Y has-a datatype
- There is only one Y
8. If X in Xs has two categories (is binary), it is categorical. 
9. If X in Xs is ordinal (has an order), it is categorical.
10. If X in Xs is categorical, it is not numeric. 
11. If X in Xs is numeric, it is not categorical.
12. If Y has two categories (is binary), it is categorical.
13. If Y is ordinal, it is categorical,
14. If Y is categorical, it is not numeric. 
15. If Y is numeric, it is not categorical.

### TODO: 
## Link functions
16. If Model(Xs, Y) has an identity link function, Y is numeric. 
## Variance functions

# Hypothesis -> Goal 

Goal: Variable Relationship Graph 
Hypothesis: Models(Xs, Y) AND For every X in Xs, X either "correlates" with Y OR x "causes" Y -- must know/get user specification. 


