# Overview and pseudocode for inferring model structures

## Inferring main effects
Inputs: Graph IR conceptual subgraph, query (all variables included have the same "high" weight)
Output: Set of candidate main effects

Rule 1: Shared ancestor (confounding variable): For all IVs included in the query, find any common ancestors of two or more IVs. Add these ancestors to a temporary set of candidates. For the ancestors in this temporary set, find any of their common ancestors. Repeat this process recursively until there are no more shared ancestors. At this point, add the candidates to final set of main effects. [recursive]

Rule 2: Causal parent (underlying variable): For each IV in the query, identify their conceptual parents. For these conceptual parents, identify their conceptual ancestors. Repeat recursively until there is a set of conceptual ancestors to the original IVs in the query that do not have any parents. Add these root variables to the set of candidate main effects. 
>>> We only look at causal relationships in this step because we are interested in potentially underlying confounding factors that exert causal influence on one or more of the specified independent variables. 

Rule 3: Raise potential overlooked, possible confounding, raise potential issues with multicollinearity: For each IV in the query, check if another variable (V1) is _associated with_ the IV. If V1 also causes or is associated with the DV in the query, add V1 to the set of candidate main effects. [one level, directly]

Rule 4: Raise potential overlooked, possible confounding, raise potential issues with multicollinearity, confounding: For each IV in the query, check if another variable (V1) causes it. If V1 also causes or is associated with the DV in the query,  add V1 to the set of candidate main effects. [one level, directly]

**Do we highlight potential multicollinearity issues?** --> Maybe there is something here for future work/limitation of this current work?

# To discuss: If we want to say we do these things in order to prevent/avoid cherry-picking/p-hacking, what additional rules might we want to enforce? (e.g., require labeling importance of all variables in the query?)

# --> We should make it clear how using the conceptual subgraph and the measurement subgraph is good for cherry picking, promoting best practices

## Inferring interaction effects
Inputs: Graph IR conceptual subgraph, query (all variables included have the same "high" weight)
Output: Set of candidate interaction effects 

Because we provide a language construct for specifying ``moderate`` relationships that are translated into interaction effects, we do not need to infer additional interaction effects that are not specified in the conceptual subgraph.

<!-- Avoid omissions: Any that have an interaction effect already between them, suggest.  -->
Rule 1: Avoid omissions: For the DV in the query, obtain all the moderating relationships in the subgraph. For each moderating relationship, if two or more of the moderating variables in the moderating relatiosnship are included as IVs in the query, add the moderating relationship to the set of interaction effects. 
<!-- Rule 1: Moderations: For each IV in the query, find any moderating relationships that involve the IV in the graph. Add these to the set of candidate interaction effects.  -->
<!-- >>>> Does this work for within-level interactions? cross-level interactions? Do we maybe need to check for what level/unit the DV is in? The other variables?  -->

TODO: Read Cox on interaction effects, best practices on interaction effects and discuss our rules in light of the best practices/Cox 

## Inferring random effects
Inputs: Graph IR data measurement subgraph
Output: Set of random effects

The derivation of random effects is dependent both on the main and interaction effects included in the final statistical model. 

### Deriving random effects for main effects: 

Rule A: If two units do not point to the same measure, following the below rules: 
    Rule 1: Repated measures: For the DV included, get its unit U. If U has more than one instance of the DV (repeated measure) according to a SetUp variable (time) in the graph, include a random intercept of U to the set of random effects. 

    Rule 2: Nested relationships: For each main effect that is included, get its unit, U0. If U0 is nested within another unit, U1, add U1 as a random intercept to the set of random effects. Do this recursively until there are no more nested relationships between units/ancestors. 

    <!-- Rule 4: For the DV included, get its unit U. If U is nested within another unit, add its parent as a random intercept to the set of random effects. Do this recursively until there are no more nested relationships between units.  -->


Non-nested
Rule B: If two units point to the same measure, follow the below rules: 
    Rule 1: For each main effect that is included, get its unit, U. If U has exaclty one instance of the IV, add a random intercept for U to the set of random effects. 

    Rule 2: For each main effect that is included, get its unit, U. If U has more than one instance of the IV, include a random slope of the IV for each group in U to the set of random effects. 

Rule 1: How many Units are represented in the graph? If one, .... If more than one,...


### Deriving random effects for interaction effects: 
Note: Must specify if the random slope and effect are correlated

Limitation: If user does not include any variables at one level, no random effects will be generated, cross-level interactions included. Is this justifiable?

Discussion: It would be really neat if we could connect each of these rules and the errors they prevent to threats of validity that Tisane helps users avoid. 


