from tisane.design import Design
from tisane.statistical_model import StatisticalModel
from tisane.smt.input_interface import InputInterface
from tisane.smt.rules import *
from tisane.smt.query_manager import QM

from z3 import * 

# Declare data type
Object = DeclareSort('Object')

def powerset(iterable):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))

class Synthesizer(object): 

    def generate_and_select_effects_sets_from_design(self, design: Design): 
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
        include_fixed = InputInterface.ask_inclusion_prompt('fixed effects')
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
            # TODO: Probably hold on to, keep track of all res_models and res_facts??
            (res_model_fixed, res_facts_fixed) = QM.solve(facts=fixed_facts, rules=rules_dict)
        import pdb; pdb.set_trace()
        ##### Interaction effects
        # Ask for user-input
        include_interactions = InputInterface.ask_inclusion_prompt('interaction effects')
        if include_interactions: 
            interaction_facts = list() 
            dv = design.dv

            # Generate possible interaction candidates from fixed_candidates
            interaction_candidates = [c for c in powserset(fixed_candidates) if len(c)>=2]
            
            # Get facts
            interaction_seq = None 
            for ixn in interaction_candidates: 
                # Build interaction sequence
                interaction = EmptySet(Object)
                for v in ixn:   
                    SetAdd(interaction, v.const)
                if interaction_seq is None: 
                    interaction_seq = Unit(interaction)
                else: 
                    interaction_seq = Concat(Unit(interaction), interaction_seq)
            
                interaction_facts.append(Interaction(interaction))
                interaction_facts.append(NoInteraction(interaction))
            
            # Get rules 
            rules_dict = QM.collect_rules(output='effects', dv_const=dv.const)

            # Solve constraints + rules
            (res_model_interaction, res_facts_interaction) = QM.solve(facts=interaction_facts, rules=rules_dict)
        import pdb; pdb.set_trace()
        ##### Random effects
        # Random if more than one level in design 
        # Random slopes vs. Random intercepts 
        # Correlations
        # Look for elbow 

        # Output effects sets --> a Statistical Model obj with "partial" initializiation?
        
    
    # Input: Design 
    # Output: StatisticalModel
    def synthesize_statistical_model(self, design: Design): 
        """
        Step-based, feedback-based (both) synthesis algorithm
        """
        # Effects set generation 
        self.generate_and_select_effects_sets_from_design(design=design)


        # Data property checking + Model characteristic selection 

        # Multicollinearity

        # TODO: Do we have a revision notion?
        # Model construction 