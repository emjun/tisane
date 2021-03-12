from tisane.variable import Nominal, Ordinal, Numeric
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

                # Get rules 
                rules_dict = QM.collect_rules(output='effects', dv_const=dv.const)

                # Solve constraints + rules
                (res_model_interaction, res_facts_interaction) = QM.solve(facts=interaction_facts, rules=rules_dict)
        
                # Update result StatisticalModel based on user selection 
            sm = QM.postprocess_to_statistical_model(model=res_model_interaction, facts=res_facts_interaction, graph=design.graph, statistical_model=sm)

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

        # Ask for user-input 
        transform_data = InputInterface.ask_inclusion(subject='data transformations')
        
        if transform_data:
            transformation_facts = list()
            dv = design.dv
            
            # Depending on family, only some link functions make sense 
            family = statistical_model.family.upper()
            if family == 'GAUSSIAN': 
                pass
            elif family == 'INVERSEGAUSSIAN': 
                pass
            # elif family == ''

            # Get facts about data types
            # Depending on variable data type, add more constraints for possible transformations
            if isinstance(dv, Numeric): 
                facts.append(NumericTransformation(var.const))
                facts.append(LogTransform(var.const))
                facts.append(SquarerootTransform(var.const))
            elif isinstance(var, Nominal) or isinstance(var, Ordinal): 
                facts.append(CategoricalTransformation(var.const))
                facts.append(LogLogTransform(var.const))
                facts.append(ProbitTransform(var.const))
                # facts.append(LogitTransform(var.const)) # TODO: Might only make sense for binary data??                

            
            # Get rules 
            rules_dict = QM.collect_rules(output='effects', dv_const=dv.const)

            # Solve constraints + rules
            (res_model_fixed, res_facts_fixed) = QM.solve(facts=fixed_facts, rules=rules_dict)
            
            # Update result StatisticalModel based on user selection 
            sm = QM.postprocess_to_statistical_model(model=res_model_fixed, facts=res_facts_fixed, graph=design.graph, statistical_model=sm)


        # Collect rules about data types and possible transformations

        # Solve facts + constraints 

        # Update statistical model 

        # Return updated statistical model 

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

        # Multicollinearity

        # Diagnostics

        # TODO: Do we have a revision notion?
        # Model construction 

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
