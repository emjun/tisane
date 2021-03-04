def test_synthesize_conceptual_model_main_1(self): 
        acc = Numeric('accuracy')
        expl = Nominal('explanation type')
        participant = Nominal('id')
        variables = [acc, expl, participant]

        design = Design(
            dv = acc, 
            # TODO: What if list: expl(treat=participant) -- pose as option in IDL?
            ivs = [expl.treat(participant)], # expl which was treated on participant
            groupings = None # what is the unit that is assumed here? -- This needs to be formalized?
        )

        sm = synthesize_statistical_model(design)
        import pdb; pdb.set_trace()
        # Should receive a simple linear model back