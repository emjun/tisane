decision_file = "./examples/data/decision-result-filter.csv"
survey_file = "./examples/data/survey-result-filter.csv"

import tisane as ts

import pandas as pd

"""
Does the Whole...
"""

# Load data
df = pd.read_csv(decision_file)

df["choice_is_correct"] = df["y"] == df["choice"]
import pdb

pdb.set_trace()
df["pred_is_correct"] = df["y"] == df["pred"]
import pdb

pdb.set_trace()
# df['pred2_is_correct'] = df['y'] == df['pred2']


# Observed variables
cond_id = ts.Nominal("condition")
task = ts.Nominal("task")
assignment_id = ts.Nominal("assignmentId")
choice_is_correct = ts.Nominal("choice_is_correct", cardinality=2)
pred_is_correct = ts.Nominal("pred_is_correct")
# pred2_is_correct = ts.Nominal('pred2_is_correct')
question_id = ts.Nominal("questionId")
time = ts.Time("time")

# # Conceptual relationship
# time.cause(weight)
choice_is_correct.associates_with(pred_is_correct)
choice_is_correct.associates_with(assignment_id)

# # Data measurement
# pig_id.repeats(weight, according_to=time)
assignment_id.has_unique(cond_id)
assignment_id.has_unique(task)

design = ts.Design(
    dv=choice_is_correct,
    ivs=[cond_id, question_id, time, task, assignment_id, pred_is_correct]
    # ivs = [cond_id, question_id, pred2_is_correct, time, task, assignment_id, pred_is_correct]
).assign_data(df)

ts.infer_statistical_model_from_design(design=design)
