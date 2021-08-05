"""
Inferring model effects structures from the graph IR
"""

from tisane.graph import Graph
from tisane.design import Design
from itertools import chain, combinations

##### HELPER #####
def powerset(iterable):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))

def find_common_ancestors(): 
    pass

def infer_main_effects(gr: Graph, query: Design):
    main_candidates = set()

    conceptual_subgraph = gr.get_conceptual_subgraph()
    
    ivs = query.ivs
    ## Rule 1: Find common ancestors 
    # Get powerset of ivs 
    pset_ivs = powerset(ivs)
    import pdb; pdb.set_trace()
    # For each elt in the powerset, find_common_ancestors()
    for e in pset_ivs: 
        if len(e) >= 2: 
            main_candidates.add(find_common_ancestors(e))


    return main_candidates

def infer_interaction_effects(gr: Graph):
    pass

def infer_random_effects(gr: Graph):
    pass

