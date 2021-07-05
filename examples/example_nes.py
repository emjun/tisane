import tisane as ts

# TODO: Dataset 

math = Numeric('MathAchievement')
hw = Numeric('Homework')
sector = Nominal('Public')
school = Nominal('School')
student = Nominal('Id')

# Conceptual relationships
hw.associates_with(math)
sector.associates_with(math)
# Data measurement relationships
student.has(math)
student.has(hw)
school.has(sector)
student.nests_under(school)

# Question 
ts.find_statistical_model_from(design=Design(dv=math, ivs=[hw, sector]), data='data.csv')

ts.find_statistical_model_with(dv=math, ivs=[hw, sector], data='data.csv')


# Other questions might be...


# TODO: {Count, Unit} as separate data types?
acc = Numeric('Accuracy')
expl = Nominal('Explanation')
participant = Nominal('id')

# Required? 
participant.has(expl)
participant.has_unique(expl) # between subject
participant.has_multiple(expl) # within subjects
expl.associates_with(acc)

ts.find_statistical_model_with(dv=acc, ivs=[expl], data='data.csv')
# Assumes that expl belongs to an id...


leaf_length = Numeric('Leaf length')
fertilizer = Nominal('Fertilizer')
plant = Nominal('plant_id')
bed = Nominal('bed_id')
week = Nominal('week') # repeated measure

plant.has_multiple(leaf_length, repetitions=week)
plant.repeats(leaf_length, repetitions=week)

bed.has_unique(fertilizer) # equivalent to below
fertilizer.treats(bed)




python3 example_nes.py
python3 tisane-cli example_nes.py