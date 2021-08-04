# Overview and pseudocode for inferring model structures

## Inferring main effects
Inputs: Graph IR conceptual subgraph, query (all variables included have the same "high" weight)
Output: Set of candidate main effects

Rule 1: Shared ancestor (confounding variable): For all IVs included in the query, find any common ancestors of two or more IVs. Add these ancestors to a temporary set of candidates. For the ancestors in this temporary set, find any of their common ancestors. Repeat this process recursively until there are no more shared ancestors. At this point, add the candidates to final set of main effects. [recursive]

Rule 2: Conceptual parent (underlying variable): For each IV in the query, identify their conceptual parents. For these conceptual parents, identify their conceptual ancestors. Repeat recursively until there are is a set of conceptual ancestors to the original IVs in the query that do not have any parents. Add these root variables to the set of candidate main effects. 

Rule 3: Raise potential overlooked, possible confounding, raise potential issues with multicollinearity: For each IV in the query, check if another variable (V1) is _associated with_ the IV. If V1 also causes or is associated with the DV in the query, add V1 to the set of candidate main effects. [one level, directly]

Rule 4: Raise potential overlooked, possible confounding, raise potential issues with multicollinearity, confounding: For each IV in the query, check if another variable (V1) causes it. If V1 also causes or is associated with the DV in the query,  add V1 to the set of candidate main effects. [one level, directly]

**Do we highlight potential multicollinearity issues?** --> Maybe there is something here for future work/limitation of this current work?

# To discuss: If we want to say we do these things in order to prevent/avoid cherry-picking/p-hacking, what additional rules might we want to enforce? (e.g., require labeling importance of all variables in the query?)
TODO: Re-read the UIST paper section on deriving main effects

# --> We should make it clear how using the conceptual subgraph and the measurement subgraph is good for cherry picking, promoting best practices

## Inferring interaction effects
Inputs: Graph IR conceptual subgraph


## Inferring random effects
Inputs: Graph IR data measurement subgraph
