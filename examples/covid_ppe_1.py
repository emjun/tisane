# COVID PPE Example 1
# Adapt from COVID PPE Example 0 so that there is a 1:1 correspondence from Concept:Variable/Data

analysis = Tisane(task="prediction") # should an analysis only have one task?

# Concepts
approval = Concept("approval")
doc = Concept("documentation")
form_comp = Concept("form completion")
replication = Concept("replication")

# Likely could hide this away in some way (e.g., a more functional API)
analysis.addConcept(approval)
analysis.addConcept(doc)
analysis.addConcept(form_comp)
analysis.addConcept(replication)

# Measurements for Concepts
# Not necessary if have no data?
"""
data = Data(".csv")
approval.obs = Variable(data=data["approval"], dtype=nominal, categories=["community", "clinical", "incomplete", "rejected"])
doc.obs = Variable()
"""
# Have data schema 
approval.specifyData(dtype=nominal, categories=["community", "clinical", "incomplete", "rejected"])
# Have data 
approval.addData(data=data["approval"], dtype=nominal, categories=["community", "clinical", "incomplete", "rejected"])
# OR 
approval.specifyData(dtype=nominal, categories=["community", "clinical", "incomplete", "rejected"])
approval.addData(data=data["approval"], kwargs) # kwargs provide syntactic sugar

# STUDY DESIGN 
- What does TSL look like??

# NO assumptions, knowledge about data


# Hypothesis



# WOULD BE NICE: 
# Verify expected model
analysis.verify(MultinomialRegression) 

# provide partial specification to narrow search space
analysis.specifySomethingLike("Approval ~ safety + replicability")
analysis.specifySomethingLike(main=[safety, replicability], dv=approval, random=None)

# callbacks for follow-up hypotheses -- combine multiple programming models...not sure this is a good or bad thing