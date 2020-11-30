# Tutoring Example 0
"""
Study Design: Half participants get Tutoring, Half do not get Tutoring. See impact of Tutoring on Test Scores.
Research Question: How does tutoring affect test performance?
Hypothesis: Tutoring positively improves test performance for all students regardless of IQ.
Task goal: hypothesis testing
"""

import tisane as ts

# LANG REQUIREMENT: At least two different tasks: explanation (theory/domain info impt), prediction (theory/domain not impt)
analysis = ts.Tisane(task="hypothesis testing") # analysis has one task

# CONCEPTS
# Concepts
test_score = ts.Concept("Test Score")
intelligence = ts.Concept("Intelligence")
tutoring = ts.Concept("Tutoring")

# Likely could hide this away in some way (e.g., a more functional API)
analysis.addConcept(test_score)
analysis.addConcept(intelligence)
analysis.addConcept(tutoring)


# MEASUREMENTS
# No data but know some ideas for measurement
test_score.specifyData(dtype="numeric") # Score 0 - 100 
intelligence.specifyData(dtype="numeric") # IQ score 
tutoring.specifyData(dtype="nominal", categories=["afterschool", "none"])

# STUDY DESIGN -- inspiration from TSL
analysis.between(tutoring)

# TODO: Do we need a notion of a "unit"?? like a participant? Trial? 
"""
Between(Pointer, Device X ID)
Ops for IVs in TSL: 
nest
cross 
concatenate 
replicate
"""

# LANG REQ: Type of relationship
# LANG REQ: Clear assignment of X and Y (TODO: verify with the study design)
analysis.relate(ivs=[intelligence, tutoring], dv=[test_score], type="linear")
analysis.relate(ivs=[intelligence, tutoring], dv=[test_score], type="quadratic")
analysis.relate(ivs=[intelligence, tutoring], dv=[test_score], type="exponential")
# ... could be other different types of relationships


# CONCEPTUAL RELATIONSHIPS
# KNOW IVS and DV are related in THEORY vs. exploratory
intelligence.causes(test_score, "assert") # know this from theory
tutoring.causes(test_score, "ask") # asking about this relationship
# assert intelligence.causes(score)
# assume intelligence.causes(score)
"""
Relationships:
assert (theory) | assume (exploratory) | ask (hypothesis testing)
"""

# DATA ASSUMPTIONS
# Data assumptions are about the POPULATION, not SAMPLE (???) -- start here: Read 480 - 481 in CCWA
"""
Data:
assert (population) | assume (exploratory, based on sample) | ask (??)
"""

# Hypothesis 


# WOULD BE NICE: 
# Verify expected model
analysis.verify(MultinomialRegression) 

# provide partial specification to narrow search space
analysis.specifySomethingLike("Approval ~ safety + replicability")
analysis.specifySomethingLike(main=[safety, replicability], dv=approval, random=None)

# callbacks for follow-up hypotheses -- combine multiple programming models...not sure this is a good or bad thing