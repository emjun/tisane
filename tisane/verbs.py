"""
Difference between Predict vs. Explain: 
- weights for constraints? 
- selection process? 
- prediction: only include those vars that have significant effects but explanation: might want to include even if not stat sig because have theoretical meaning (see Shmueli article, below)
SEE: https://www.stat.berkeley.edu/~aldous/157/Papers/shmueli.pdf
"""
analysis.
    predict(y=Var) or predict(y=Var, env=ConceptGraph)
    predictWith(y=Var, x=[])
    predictWithOnly(y=Var, x=[])
    predictWithout(y=Var, x=[])

analysis.
    explain(y=Var) or explain(y=Var, env=ConceptGraph)
    explainWith(y=Var, x=[])
    explainWithOnly(y=Var, x=[])
    explainWithout(y=Var, x=[])
## Explanation might require some statement of the important causal relationships

# Testing might be part of explain! 
analysis. 
    predict().test(...) # may require some kind of hypothesis grammar
    explain().test(...)



## Verbs for conceptual graph 

## Verbs for study design (data schema)

## Verbs for asserting vs. assuming data properties 

## Verbs for predicting, vs. explaining, vs. hypothesis testing

