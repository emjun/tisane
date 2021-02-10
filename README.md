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

