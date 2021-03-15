from tisane.variable import Nominal, Ordinal, Numeric
from tisane.design import Design
from tisane.statistical_model import StatisticalModel
from tisane.smt.input_interface import InputInterface
from tisane.smt.rules import *
from tisane.smt.query_manager import QM

from z3 import * 
from itertools import chain, combinations
from typing import List

# Declare data type
Object = DeclareSort('Object')

def powerset(iterable):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))

class Synthesizer(object): 

    # Synthesizer generates possible effects, End-user interactively selects single effect set they want
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
            sm = QM.postprocess_to_statistical_model(model=res_model_fixed, facts=res_facts_fixed, graph=design.graph, statistical_model=sm)

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

                # Use rules from above

                # Solve constraints + rules
                (res_model_interaction, res_facts_interaction) = QM.solve(facts=interaction_facts, rules=rules_dict)
        
                # Update result StatisticalModel based on user selection 
                sm = QM.postprocess_to_statistical_model(model=res_model_interaction, facts=res_facts_interaction, graph=design.graph, statistical_model=sm)

        ##### Random effects
        # Random slopes and intercepts are possible if there is more than one level in design 
        # TODO: Update when move away from levels design
        random_pairs = list()
        if design.get_number_of_levels() >= 2:
            random_facts = list()
        
            # TODO: Limitation of algo below: (i) What happens if there are >2
            # levels? (ii) Does the number of nesting (1|g2/g1) matter on if
            # end-user specifies which ones to include in study design? 
            # Look for "elbow" pattern in graph IR 
            # Elbow pattern: Dv <- V <- ID1 -> ID2
            for v in fixed_candidates: 
                # Get 'has' predecessors 
                has_predecesors = set()
                v_pred = design.graph.get_predecessors(v)
                for p in v_pred: 
                    p_var = design.graph.get_variable(name=p)
                    if design.graph.has_edge(start=p_var, end=v, edge_type='has'): 
                        has_predecesors.add(p_var)

                # Of those 'has' predecessors of v, see if they are 'nested' in another level 
                for h in has_predecesors: 
                    parents = design.graph.get_neighbors(variable=h, edge_type='nest')
                    for p in parents: 
                        # Get facts
                        random_facts.append(RandomSlope(v.const, p.const))        
                        random_facts.append(NoRandomSlope(v.const, p.const))      
                        random_facts.append(RandomIntercept(v.const, p.const))        
                        random_facts.append(NoRandomIntercept(v.const, p.const))        
                        # Keep track of pairs to ask about correlation below
                        random_pairs.append((RandomSlope(v.const, p.const), RandomIntercept(v.const, p.const), v.const, p.const))
                    
            # Use rules from above

            # Solve constraints + rules
            (res_model_random, res_facts_random) = QM.solve(facts=random_facts, rules=rules_dict)
            
            # Ask if random slopes and intercepts are correlated
            # Get facts
            random_correlation_facts = list()
            for (slope, intercept, variable, parent) in random_pairs: 
                if slope in res_facts_random and intercept in res_facts_random: 
                    random_correlation_facts.append(CorrelateRandomSlopeIntercept(variable, parent))
                    random_correlation_facts.append(NoCorrelateRandomSlopeIntercept(variable, parent))
                    
            # Use rules from above

            # Solve constraints + rules
            (res_model_random, res_facts_random) = QM.solve(facts=random_correlation_facts, rules=rules_dict)

            # Update result StatisticalModel based on user selections 
            sm = QM.postprocess_to_statistical_model(model=res_model_random, facts=res_facts_random, graph=design.graph, statistical_model=sm)

            
            # Return a Statistical Model obj with effects set
            return sm
    
    # Synthesizer generates statistical model properties that depend on data 
    # End-user interactively selects properties they want about their statistical model
    def generate_and_select_data_model_properties(self, design: Design, statistical_model: StatisticalModel): 
        # TODO: Ask end-user if they want to consider transformations before families? 
        # Ideally: Would be ideal to let them go back and forth between transformation and family...
        
        pass
    
    def generate_family(self, design: Design): 
        family_facts = list() 

        # Get facts from data types
        dv = design.dv
        if isinstance(dv, Numeric) or isinstance(dv, Ordinal): 
            family_facts.append(GaussianFamily(dv.const))
            family_facts.append(InverseGaussianFamily(dv.const))
            family_facts.append(PoissonFamily(dv.const))
            family_facts.append(GammaFamily(dv.const))
            family_facts.append(TweedieFamily(dv.const)) # TODO: Add test
        if isinstance(dv, Nominal) or isinstance(dv, Ordinal): 
            if dv.cardinality is not None: 
                if dv.cardinality == 2:
                    family_facts.append(BinomialFamily(dv.const))
                    family_facts.append(NegativeBinomialFamily(dv.const))
                elif dv.cardinality > 2: 
                    family_facts.append(MultinomialFamily(dv.const))
            # TODO: Get missing info about cardinality?
            else: 
                pass

        return family_facts
        
    def generate_and_select_family(self, design: Design, statistical_model: StatisticalModel): 
        family_facts = self.generate_family(design=design)
        dv = design.dv

        # End-user: Ask about which family 
        selected_family_fact = [InputInterface.ask_family(options=family_facts, dv=design.dv)]

        # Get rules
        rules_dict = QM.collect_rules(output='FAMILY', dv_const=dv.const)

        # Solve constraints + rules
        (res_model_family, res_facts_family) = QM.solve(facts=selected_family_fact, rules=rules_dict)
        
        # Update result StatisticalModel based on user selection 
        statistical_model = QM.postprocess_to_statistical_model(model=res_model_family, facts=res_facts_family, graph=design.graph, statistical_model=statistical_model)

        # Return updated StatisticalModel 
        return statistical_model

    # Synthesizer generates viable data transformations to the variables 
    # End-user interactively selects which transformations they want
    # These transformations are the link functions
    def generate_and_select_link(self, design: Design, statistical_model: StatisticalModel): 
        # TODO: Start with no vis 
        # TODO: Add in vis

        family_fact = list()
        # Re-create family fact based on statistical model fact
        family = statistical_model.family
        if family == 'Gaussian': 
            family_fact.append(GaussianFamily(design.dv.const))
        elif family == 'InverseGaussian': 
            family_fact.append(InverseGaussianFamily(design.dv.const))
        elif family == 'Poisson': 
            family_fact.append(PoissonFamily(design.dv.const))
        elif family == 'Gamma': 
            family_fact.append(GammaFamily(design.dv.const))
        elif family == 'Tweedie': 
            family_fact.append(TweedieFamily(design.dv.const))
        elif family == 'Binomial': 
            family_fact.append(BinomialFamily(design.dv.const))
        elif family == 'NegativeBinomial': 
            family_fact.append(NegativeBinomialFamily(design.dv.const))
        elif family == 'Multinomial': 
            family_fact.append(MultinomialFamily(design.dv.const))

        # Ask for user-input 
        transform_data = InputInterface.ask_inclusion(subject='data transformations')
        
        if transform_data:
            dv = design.dv
            
            ##### Derive possible valid transforms from knowledge base
            # Get rules
            rules_dict = QM.collect_rules(output='TRANSFORMATION', dv_const=dv.const)
            # Get rules for possible link functions
            family_to_transformation_rules = rules_dict['family_to_transformation_rules']

            # Solve fact + rules to get possible link functions
            (res_model_transformations, res_facts_family) = QM.solve(facts=family_fact, rules={'family_to_transformation_rules': family_to_transformation_rules})

            ##### Pick link/data transformation 
            # Get link/data transformation rules
            data_transformation_rules = rules_dict['data_transformation_rules']
            
            # Get link facts
            transformation_candidate_facts = QM.model_to_transformation_facts(model=res_model_transformations, design=design)
    
            # Solve facts + rules
            (res_model_link, res_facts_link) = QM.solve(facts=transformation_candidate_facts, rules={'data_transformation_rules': data_transformation_rules})
        
            # Update result StatisticalModel based on user selection 
            statistical_model = QM.postprocess_to_statistical_model(model=res_model_link, facts=res_facts_link, graph=design.graph, statistical_model=statistical_model)

            # Return statistical model
            return statistical_model


    # Input: Design 
    # Output: StatisticalModel
    def synthesize_statistical_model(self, design: Design): 
        """
        Step-based, feedback-based (both) synthesis algorithm
        Incrementally builds up an output StatisticalModel object
        """
        ##### Effects set generation 
        sm = self.generate_and_select_effects_sets_from_design(design=design)
        assert(isinstance(sm, StatisticalModel))

        ##### Data property checking + Model characteristic selection 
        ##### Updates the StatisticalModel constructed above
        # Family 
        sm = self.generate_and_select_family(design=design, statistical_model=sm)

        # Link function    
        sm = self.generate_and_select_link(design=design, statistical_model=sm)

        # TODO: Do we have a revision notion?
        # Diagnostics: Multicollinearity

    # Not yet necessary
    # Synthesizer generates possible variance functions based on the family
    # End-user selects variance function
    def generate_and_select_variance_function(self, design: Design, statistical_model: StatisticalModel): 
        # If the statistical model has no specified family, pick a family first
        if statistical_model.family is None: 
            self.generate_and_select_family(design=design, statistical_model=statistical_model)
        
        # We have already specified a family
        # Get the default variance function  
        default_variance_func = None # TODO

        # Ask user if they want to change the default
        InputInterface.ask_change_default(subject='variance function', default=default_variance_func)
        
        variance_facts = list()

        # Get facts from variance function 
