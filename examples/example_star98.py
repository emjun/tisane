import tisane as ts
import pandas as pd

"""
Adapted from Jeff Gill 2000, which was also included in Statsmodels examples

Background, copied from Statsmodels example: 
"Math scores for 303 student with 10 explanatory factors

This data is on the California education policy and outcomes (STAR program
results for 1998.  The data measured standardized testing by the California
Department of Education that required evaluation of 2nd - 11th grade students
by the the Stanford 9 test on a variety of subjects.  This dataset is at
the level of the unified school district and consists of 303 cases.  The
binary response variable represents the number of 9th graders scoring
over the national median value on the mathematics exam.

The data used in this example is only a subset of the original source."
"""

# Load data
df = pd.read_csv('./examples/data/star98.csv')

# Observed variables
math_achievement = ts.Count('PR50M')
lowinc = ts.Numeric('LOWINC')
per_pupil_spending = ts.Numeric('PERSPENK')
student_teacher_ratio = ts.Numeric('PTRATIO')

 PERMINTE_AVYRSEXP
        PEMINTE_AVSAL
        AVYRSEXP_AVSAL
        PERSPEN_PTRATIO
        PERSPEN_PCTAF
        PTRATIO_PCTAF
        PERMINTE_AVTRSEXP_AVSAL
        PERSPEN_PTRATIO_PCTAF


# prep_course_enrollment = ts. Numeric('PCTAF')
# average_budget = ts.Numeric('AVSALK')
# charter_school_per = ts.Numeric('PCTCHRT')
# yearround_school_per = ts.Numeric('PCTYRRND')
# asian_per = ts.Numeric('PERASIAN')
# black_per = ts.Numeric('PERBLACK')
# hispanic_per = ts.Numeric('PERHISP')
# minority_teachers = ts.Numeric('PERMINTE')
# average_teacher_exper = ts.Numeric('AVYRSEXP')

# Conceptual relationships
math_achievement.