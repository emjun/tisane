"""
SAMPLE PROGRAM
"""

import tisane as ts


##### WITHOUT DATA
# TODO: add which variables the concepts correspond to
intell = ts.Concept('Intelligence')
age = ts.Concept('Age')
aptitude = ts.Concept('Aptitude')


# Input: Observed variables + data schema
dataset = ts.Data(iid='Participant_ID') # necesary for checking if between-subjects, within-subjects
pid = ts.Variable(name='Participant_ID', dtype=nominal, data=dataset) # assume all variables are found in the dataset 
iq = ts.Variable(name='IQ', dtype=numeric, data=dataset) # name is column name
age = ts.Variable(name='Age', dtype=numeric, data=dataset)
sat = ts.Variable(name='SAT Score', dtype=numeric, data=dataset)
# Below line necessary???
# analysis.data(dataset=dataset, vars=[pid, iq, age, sat]) # could make more functional 

# Input: Data collection procedure
# Assign IVs and DV; data is optional
dcp = ts.Design(ivs=[iq, age], dv=[sat], unit=pid) # as part of effects set generation or selection (thinking about covariates)
# Specify between-/within-subjects
dcp.set_unit(pid)
dcp.nest(iq, pid, 1) # 1:1
dcp.nest(age, pid, 1)

analysis = ts.Tisane(vars=[pid, iq, age, sat], design=dcp)
# Intermediate output: Conceptual graph
# Relate variables
# Revise (Intermediate input)
analysis.relate(intelligence, 'cause', test_score)
analysis.relate(tutoring, 'cause', test_score)
analysis.relate(intelligence, 'correlate', tutoring)

# Input: Query about research question 
analysis.query('explain', ivs=[iq, age], dv=[sat])

""" TO EXPLORE: More expressive query language (borrowing from SQL?) -- what if design as query language?
SELECT iq, age as IV and sat as DV 
FROM analysis.variables
EXPLAIN 

""""
##### WITH DATA
ds = ts.Data(source='data.csv', iid='Participant_ID')
pid.add_data(data=ds[0]) # array-like list of values
iq.add_data(data=ds[1])
age.add_data(data=ds[2])
sat.add_data(data=ds[3])

# if wanted to combine observed data:
verbal = ts.Variable(name='Verbal Aptitude', dtype=numeric) 
math = ts.Variable(name='Math Aptitude', dtype=numeric)
verbal.add_data(data=ds[4])
math.add_data(data=ds[5])
sat.add_data(verbal.get_data() + math.get_data()) 

analysis = ts.Tisane(vars=[pid, iq, age, sat], design=dcp)

analysis.query('explain', ivs=[iq, age], dv=[sat])

### TUTORING
pid = ts.Proxy(name='Participant_ID', dtype=nominal)
iq = ts.Proxy(name='IQ', dtype=numeric)
age = ts.Proxy(name='Age', dtype=numeric)
sat = ts.Proxy(name='SAT Score', dtype=numeric)
tutoring = ts.Proxy(name='Tutoring', dtype=nominal, categories=['Tutoring', 'No tutoring'])

dataset = ts.Data(iid='Participant_ID') # necesary for checking if between-subjects, within-subjects

dcp = ts.Design(ivs=[iq, age, tutoring], dv=[sat], unit=pid) # as part of effects set generation or selection (thinking about covariates)
# Specify between-/within-subjects
dcp.set_unit(pid)
dcp.nest(iq, pid, 1)
dcp.nest(age, pid, 1)
dcp.nest(pid, tutoring, 1)

analysis = ts.Tisane(vars=[pid, iq, age, sat, tutoring], design=dcp)

analysis.query('explain', ivs=[iq, age, tutoring], dv=[sat])

### TUTORING IN CLASS! (nested)
pid = ts.Proxy(name='Participant_ID', dtype=nominal)
iq = ts.Proxy(name='IQ', dtype=numeric)
age = ts.Proxy(name='Age', dtype=numeric)
sat = ts.Proxy(name='SAT Score', dtype=numeric)
tutoring = ts.Proxy(name='Tutoring', dtype=nominal, categories=['Tutoring', 'No tutoring'])
classroom = ts.Proxy(name='class', dtype=nominal)

dataset = ts.Data(iid='Participant_ID') # necesary for checking if between-subjects, within-subjects

dcp = ts.Design(ivs=[iq, age, tutoring], dv=[sat]) # as part of effects set generation or selection (thinking about covariates)
dcp.set_unit(pid)
dcp.nest(iq, pid, 1) # Between-subjects
dcp.nest(age, pid, 1) # Between-subjects
dcp.nest(pid, classroom, 1) # nest pid in classroom, Between-subects

analysis = ts.Tisane(vars=[pid, iq, age, sat, tutoring, classroom], design=dcp)

analysis.query('explain', ivs=[iq, age, tutoring], dv=[sat])


### CONCEPTS: Specify concepts that are more abstract that the observed data (e.g., same construct can be measured using multiple obs. vars or combinations of obs. vars)
intelligence = ts.Concept(name='Intelligence', proxy=[iq])
intelligence = ts.Concept(name='Intelligence', proxy=[verbal, math])
intelligence = ts.Concept(name='Intelligence', proxy=[verbal + math]) # verbal + math would return a new Variable
