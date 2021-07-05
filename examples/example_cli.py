import tisane as ts

"""
Example from Bansal et al. CHI 2021
"""
acc = ts.Numeric("accuracy")
expl = ts.Nominal("explanation type")
pid = ts.Nominal("participant")

# expl.treats(pid)
pid.has_unique(expl)
expl.associates_with(acc)

iv = ts.Level(identifier="id", measures=[expl])

design = ts.Design(dv=acc, ivs=iv)

ts.synthesize_statistical_model(design=design)
