# tisane
Mixed Initiative System for Linear Modeling 

Interface + DSL + Knowledge Base 

DSL and Knowledge Base: 
1. Effects sets generation
    - Interaction: Select which sets of variables the end-user is interested in.
2. Dynamically generate the constraints according to the set of variables. (in a for-loop)
    - The next step happens in a loop 
    - For the next step, need a way to store results of vis for anything that is not specific to a set of effects... (can be reused)
3. Property verification for selected sets. 
    - Interaction: Variable data types
    - Interaction: 
        - If have no data: assumptions that hold (checkboxes or something)
        - If have data: Visualization for all residual properties.
4. Steps 1 and 2 generate constraints that are used to figure out the set of statistical models that hold. 
5. Parse Knowledge Base output into statistical scripts for each set of effects! (Draco example: https://github.com/uwdata/draco/blob/master/js/src/asp2vl.ts)

Important files: 
tests/sample.py : Sample program. 

# Design Rationale
Design API
- Definitions: https://docs.google.com/document/d/16b1u8WUQFcYdcswJJqIjKzV11VLG2p7ozFQkYX51JaI/edit
- Early prototype feedback: https://gist.github.com/emjun/97acf6666ed6d4d457efa2edf55eee86 
- Formative, related work: https://docs.google.com/document/d/1LGfZ3_WKsyGOeZecA-w-cFqDslFRYdqlKCyo6fgdexM/edit



# Benefits of using Tisane
```
# These are all different phases/steps in compilation

# Checks
# Generate possible main effects
# Generate possible interaction effects [nope, must be specified when writing program]
# Generate random effects [depends on main effects]
# Generate candidate family and link functions
# Interaction loop(?) with user --> how to go about structuring this?
```

Overall: Author statistical models that are conceptually and statistically sensical and valid (?). 
1. Conceptual check: Tisane ensures that only variables that have a conceptual influence on the DV are included. 
2. Data measurement check: Tiasne ensures that data measurement details are properly accounted for by automatically inferring and including random effects. Units and measures must be associated with one another. (Another way to say this: Tisane avoids a common mistake to omit random effects structures that should be included)
3. Conceptual and statistical check: 


pre-empt 
(Another way to say this: omit important variables that should be included as ivs --> How?)

- What happens if include all the variables
- What happens if include only some of the variables (there are mediators that are not included)



# - omit important variables that should be included as ivs --> How?
    
    Simplest case: Only main effects 

    Two types of errors that are avoided: 
    
    


Omit important variables that should be included as IVs

In terms of *validity*, Tisane avoids common threats to validity. See here.

# Implementation details
Not clear that SMT is necessary. The generation of possible effects structures seems to be doable just on the graph alone through different graph traversals.

Without supporting model revision, we don't need to ask for weights for variables.


# [x] Implement the updated variable API just for nested and repeated measures
# [] Write test cases and implement the main, interaction, and random effects generation functions
# Write test cases and implement the family/link function generation functions
# [start here tomorrow] Write function for generating all combinations of model effects + family/link
# Sketch through GUI again


# Questions: 
1. What should we do about Repeats that are declared? An associates/cause relationship between Time and DV is implied. What should we do about that? - This was implicit before, so why not also add Associates(Time, DV) now?
