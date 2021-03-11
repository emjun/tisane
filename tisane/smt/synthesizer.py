from tisane.design import Design
from tisane.statistical_model import StatisticalModel
from tisane.smt.input_interface import InputInterface
from tisane.smt.rules import *
from tisane.smt.query_manager import QM

from z3 import * 
from itertools import chain, combinations

# Declare data type
Object = DeclareSort('Object')

def powerset(iterable):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))

class Synthesizer(object): 

    def generate_and_select_effects_sets_from_design(self, design: Design): 
        sm = StatisticalModel(dv=design.dv)

        ##### Fixed effects 
        fixed_candidates = set() 

        # Find candidates based on predecessors to the @param design.dv
        # Get the predecessors to the DV 
        dv_pred = design.graph.get_predecessors(design.dv)
        for p in dv_pred: 
            p_var = design.graph.get_variable(name=p)
            if design.graph.has_edge(start=p_var, end=design.dv, edge_type='contribute'): 
                fixed_candidates.add(p_var)
        
        # Ask for user-input 
        include_fixed = InputInterface.ask_inclusion(subject='fixed effects')
        if include_fixed: 
            fixed_facts = list()
            dv = design.dv
            
            # Get facts
            for f in fixed_candidates: 
                fixed_facts.append(FixedEffect(f.const,dv.const))
                fixed_facts.append(NoFixedEffect(f.const,dv.const))
            
            # Get rules 
            rules_dict = QM.collect_rules(output='effects', dv_const=dv.const)

            # Solve constraints + rules
            (res_model_fixed, res_facts_fixed) = QM.solve(facts=fixed_facts, rules=rules_dict)
            
            # Update result StatisticalModel based on user selection 
            sm = QM.postprocess(model=res_model_fixed, facts=res_facts_fixed, graph=design.graph, statistical_model=sm)

        ##### Interaction effects
        # Do we have enough fixed effects to create interactions?
        if len(fixed_candidates) >= 2:
            # Ask for user-input
            include_interactions = InputInterface.ask_inclusion(subject='interaction effects')
            if include_interactions: 
                interaction_facts = list() 
                dv = design.dv

                # Generate possible interaction candidates from fixed_candidates
                interaction_candidates = [c for c in powerset(fixed_candidates) if len(c)>=2]
                
                # Get facts
                interaction_seq = None 
                for ixn in interaction_candidates: 
                    # Build interaction sequence
                    interaction = EmptySet(Object)

                    for v in ixn:   
                        interaction = SetAdd(interaction, v.const)
                    # if interaction_seq is None: 
                    #     interaction_seq = Unit(interaction)
                    #     import pdb; pdb.set_trace()
                    # else: 
                    #     interaction_seq = Concat(Unit(interaction), interaction_seq)
                
                    interaction_facts.append(Interaction(interaction))
                    interaction_facts.append(NoInteraction(interaction))
                    
                    interaction_seq = None 

                # Get rules 
                rules_dict = QM.collect_rules(output='effects', dv_const=dv.const)

                # Solve constraints + rules
                (res_model_interaction, res_facts_interaction) = QM.solve(facts=interaction_facts, rules=rules_dict)
        
                # Update result StatisticalModel based on user selection 
            sm = QM.postprocess(model=res_model_interaction, facts=res_facts_interaction, graph=design.graph, statistical_model=sm)

        ##### Random effects
        # Random slopes and intercepts are possible if there is more than one level in design 
        if design.get_number_of_levels() >= 2:
            pass
            # Look for "elbow" pattern in graph IR 

            # Random slopes vs. Random intercepts 

            # Correlations
            # Look for elbow 

        # Return a Statistical Model obj with effects set
        return sm
    
    # Input: Design 
    # Output: StatisticalModel
    def synthesize_statistical_model(self, design: Design): 
        """
        Step-based, feedback-based (both) synthesis algorithm
        Incrementally builds up an output StatisticalModel object
        """
        # Effects set generation 
        sm = self.generate_and_select_effects_sets_from_design(design=design)
        assert(isinstance(sm, StatisticalModel))

        # Data property checking + Model characteristic selection 

        # Multicollinearity

        # TODO: Do we have a revision notion?
        # Model construction 