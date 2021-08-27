# Overview (and pseudocode) for inferring model structures
FYI: The candidate statistical model generation passes over the graph are implemented in ``graph_inference.py``

As of August 14, 2021: I (Eunice) is still re-implementing and testing passes, so it is not complete!

## Inferring main effects
Inputs: Graph IR (specifically, conceptual subgraph), query with analyst-specified IVs and DV
<!-- (all variables included have the same "high" weight) -->
Output: Set of candidate main effects

**Rule 1: Causal ancestors:** For each IV in the query, identify their conceptual parents. For these conceptual parents, identify their conceptual ancestors. Repeat recursively until there is a set of conceptual ancestors to the original IVs in the query that do not have any parents. Add these root variables to the set of candidate main effects. [recursive]
**Rule 2: Find shared causal ancestors:** For all IVs included in the query, find any common ancestors of two or more IVs. Add these ancestors to a temporary set of candidates. For the ancestors in this temporary set, find any of their common ancestors. Repeat this process recursively until there are no more shared ancestors. At this point, add the candidates to final set of main effects. [recursive]

*Rationale for Rules 1, 2:* 
1. Shared causal ancstors may be potentially underlying variables that exert causal influence on one or more of the specified independent variables
2. Help analysts not overlook conceptually relevant variables. In a strictly causal subgraph (if all the IVs in a query cause the DV), including the IVs in the model would d-separate their causal ancestors from the dependent variable. An implication is that including their causal ancestors, shared or not, would be ``unnecessary'' (e.g., influence of parameter on dependent variable would be statistically not significant). However, if there are shared ancestors, these ancestors may be better to condition on in the first place since they exert causal influence over the other IVs. The other IVs may simply mediate, for example, the causal ancestors' influence on the DV. Including a mixture of causal ancestors and IVs is justifiable based on analysis goals. 

**Rule 3: Potential confounders:** For each IV in the query, check if another variable (V1) is _associated with_ the IV. If V1 also causes or is associated with the DV in the query, add V1 to the set of candidate main effects. [one level/direct, not recursive]

*Rationale for Rule 3:*
1. Raise potential overlooked, possible confounding variables. 

> FEEDBACK REQUESTED: The IVs in the analysts' queries as well as the ones they choose to be main effects during interactive compilation may be correlated with another, introducing potential issues around multicollinearity. Currently, we don't do anything to prevent this. Arguably, GLMs are robust to multicollinear issues and these can be resolved during model revision. However, if we want to help analysts avoid unnecessary model revision loops, maybe we should "flag" potential multicollinear problems? Should we also suggest which variables to include/exclude using heuristics (e.g., prefer to include variables that cause the DV rather than those just associated with the DV)? 


## Inferring interaction effects
Inputs: Graph IR (specifically, conceptual subgraph), query with analyst-specified IVs and DV, candidate main effects that the analyst has included/added during disambiguation (optional)
Output: Set of candidate interaction effects 

Because we provide a language construct for specifying ``moderates`` relationships that are translated into interaction effects, we do not need to infer additional interaction effects that are not specified in the conceptual subgraph.

**Rule 1: Avoid omissions:** For the DV in the query, obtain all the moderating relationships in the conceptual subgraph. For each moderating relationship, if two or more of the moderating variables in the moderating relatiosnship are included as main effects candidates (could include variables that are added as main effects in addition to the IVs in the query), add the moderating relationship to the set of interaction effects. 

*Note:* The ``moderates`` language construct and the interaction effect generation process/rule is agnostic to if the interaction term is within-level or across-levels in a generalized linear mixed-effects model. 


## Inferring random effects
Inputs: Graph IR, specifically data measurement subgraph, selected main effects and interaction effects
Output: Set of random effects must include to obtain maximal random effects structure

### Inferring random effects for main effects
The below rules operationalize the recommendations from Barr et al. 2013 [2]. Barr et al. use the terms "unit" and "treatment" in a couple different ways throughout the paper that does not always align with our usage of the terms, but I have translated the recommendations into our definitions below. 

<!-- Rule A: If two units do not point to the same measure, following the below rules:  -->
**Rule 1: Repated measures:** For the DV included, get its unit U. If U has more than one instance of the DV (repeated measure) according to a SetUp variable (e.g., time) in the graph, include a random intercept of U to the set of random effects. Also include a random intercept for the SetUp variable. In other words, make sure to pool across observational unit and stimulus/differentiator.

*Assumption:*
1. The study design is either fully factorial/fully crossed or fractionally factorial with multiple observations per time/treatment unit (implied in a fully factorial design)

**Rule 2: Nested relationships:** For each main effect that is included, get its unit, U0. If U0 is nested within another unit, U1, add U1 as a random intercept to the set of random effects. Do this recursively until there are no more nested relationships between units/ancestors. 

*Rules 1, 2 operationalize the following recommendation from Barr et al.:* "If a factor is between-unit, then a random intercept is usually sufficient." 
- Repeated measures is between-subjects since each observational unit contributes their own cluster of observations. Also, each time point is separate from the others, making it between-subjects. 
- Repeated measures can coincide with non-nesting relationships (see Rule 3), as in the Barr et al.'s linguistic study example. 
- Nesting is between-unit since each unit can only be nested within one nesting unit.

**Rule 3: Non-nesting relationships:** For each main effect that, M, is included and varied within-subjects (each instance of the main effect's, U0, unit contributes multiple instances/observations of the main effect variable), check to see if M is a Measure variable type that also has/consists of a Unit variable type, U1. If so, check how many instances of the Unit the Measure contains. If greater than one, there is a non-nesting/composition relationship that requires a random slope of U0 and M. Otherwise, M and U1 are redundant (1:1), and there is only one observation per ``treatment level per unit,'' which requires a random intercept of U0. 

*Rule 3 operationalizes the following recommendations from Barr et al.:* "If a factor is within-unit (i.e., main effect) and there are multiple observations per treatment level per unit, then you need a by-unit random slope for that factor. The only exception to this rule is when you only have a single observation for every treatment level of every unit; in this case...a ranndom intercept would be sufficient."

### [WIP] Inferring random effects for interaction effects
The below rules operationalize the updated recommendations for interaction effects from Barr 2013 [1]. Barr recommends "...when testing interactions in mixed designs with replications, it is critical to include the random slope corresponding to the highest-order combination of within-subject factors subsumed by each interaction of interest." 
*Note:* Barr's recommendation is straightforward for within-level interactions that involve variables pertaining to the same unit. For cross-level interactions that invovle variables from two or more units, we include the "oldest" unit (highest nest) in the random slope. 

**Rule 4: Random slopes for all within-subject units subsumed by an interaction effect:** For each interaction effect that involves n variables, find all k within-subjects variables. Of these k within-subjects variables, find the "oldest" unit (there may be only one unit that all the variables share). Then add a random slope involving an interaction term involving the k terms and the oldest unit. 

Finally, for any random effects where there is a random slope and a random intercept involving a unit, analysts must specify if the random slope and intercept are correlated or uncorrelated. By default, they are treated as correlated. 

## Inferring candidate family and link functions 
Tisane generates candidate family functions based on the dependent variable's data type. Specifically...

- Numeric data type: Gaussian, Inverse Gaussian, Gamma, Tweedie, Poisson
- Ordinal data type: Gaussian, Inverse Gaussian, Gamma, Tweedie, Poisson, Binomial (if binary), Negative Binomial, Multinomial
- Nominal: Binomial (if binary), Negative Binomial, Multinomial

Tisane generates candidate link functions based on the family types. 
- Gaussian: Identity, Log, Logit, Probit, CLogLog, Power, OPower, Negative Binomial, LogLog
- Inverse Gaussian: Identity, Log, Power
- Gamma: Identity, Log, Power
- Tweedie: Identity, Log, Power
- Poisson: Identity, Log, Power
- Binomial: Identity, Log, Logit, Probit, CLogLog, Power, OPower, LogLog
- Negative Binomial: Identity, Log, Power, Negative Binomial
- Multinomial: Identity, Log, Logit, Probit

**Implication:** Tisane only suggests family, link function pairs that are plausible given the dependent variable's data type, avoiding unncessary modeling errors and subsequent revisions that may arise due to selecting incompatible family and link functions for the data. 

*Note:* Because Tisane uses `statsmodels` to generate the code, for fitting the final output statistical model, Tisane is limited in the implementations of family and link functions it provides. See the [statsmodels page](https://www.statsmodels.org/stable/generated/statsmodels.genmod.generalized_linear_model.GLM.html#statsmodels.genmod.generalized_linear_model.GLM). In the future, Tisane can support multiple backends for generating code to `lmer`, for example. 

## References
1. Barr, D. J. (2013). Random effects structure for testing interactions in linear mixed-effects models. Frontiers in psychology, 4, 328.
2. Barr, D. J., Levy, R., Scheepers, C., & Tily, H. J. (2013). Random effects structure for confirmatory hypothesis testing: Keep it maximal. Journal of memory and language, 68(3), 255-278.