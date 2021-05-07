# COVID PPE Exampe 0
# Multivariate example where compound concepts are required (concept is not 1:1 to variable/data)

analysis = Tisane(task="prediction")  # should an analysis only have one task?

# Concepts
approval = Concept("approval")
safety = Concept("safety")
replicability = Concept("replicability")

# Likely could hide this away in some way (e.g., a more functional API)
analysis.addConcept(approval)
analysis.addConcept(safety)
analysis.addConcept(replicability)

# Measurements for Concepts
# Not necessary if have no data?
approval.data = Variable(...)


# Verify expected model
analysis.verify(MultinomialRegression)

# provide partial specification to narrow search space
analysis.specifySomethingLike("Approval ~ safety + replicability")
analysis.specifySomethingLike(main=[safety, replicability], dv=approval, random=None)

# callbacks for follow-up hypotheses -- combine multiple programming models...not sure this is a good or bad thing
