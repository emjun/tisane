# Overview of Tisane API

Tisane supports authoring statistical models with and without data. Typically, with data, you can specify fewer things. Without data, you must provide more information.

If you do have data, your data should be in [long format](https://www.theanalysisfactor.com/wide-and-long-data/). 

### Declare observed variables
Variables can have one of 6 different types:
- Nominal: Discrete variables that have no order in their categories
- Ordinal: Discrete variables that have an order in their categories
- Numeric: Continuous variables
- Time: Variables that represent times
- Count: Variables that represent counts, always > 0

With data, cardinality information is optional.
With data, the variable names (e.g., 'Student ID') should be the name of the column that corresponds with the variable.
```
student_id = ts.Nominal('Student ID', cardinality=240) # There are 240 students

grade = ts.Ordinal('Grade', order=['First grade', 'Second grade', 'Third grade', 'Fourth grade', 'Fifth grade']) # Cardinality is optional when you specify the order.
score = ts.Numeric('Score') 

reaction_time = ts.Time('Reaction Time')

count = ts.Count('Time spent on homework')
```

### Specify conceptual relationships
There are two different conceptual relationships variables can have. 
```
exercise = ts.Nominal('exercise', order=['low', 'medium', 'high'])
weight = ts.Numeric('weight')
age = ts.Numeric('age')

exercise.cause(weight)
age.associates_with(weight)
```

### Specify relationships that describe how you collected the data

There are four kinds of relationships that you can express in Tisane: 
_Nests under_: If you have observations that are nested in groups (e.g., students nested in classrooms), use the "nests_under" construct. 
```
student = ts.Nominal('student id', cardinality = 100)
classroom = ts.Nominal('classroom', cardinality=10)

student.nest_under(classroom)
```

_Has_: If a variable has a measure or another variable, you can specify that
```
math_score = ts.Numeric('math score')
age = ts.Numeric('age')
zipcode = ts.Nominal('zipcode', cardinality=10)

student.has(math_score)
student.has(age)
school.has(zipcode)
```

_Repeats_: If you have multiple measurements from the same person or unit of observation.  (repeated measures)
```
week = ts.Nominal('Week in quarter', cardinality=10)
student.repeats(math_score, according_to=week)
```

_Treats_: If there is a treatment or manipulation that affects some observations but not others
```
tutoring = ts.Nominal('Tutoring', cardinality=2)
tutoring.treats(student, num_assignments=1) # Student gets assigned to one condition in tutoring 

funding_aid = ts.Nominal('Funding aid', cardinality=3)
funding_aid.treats(school, num_assignments=3)
```

This implies that there are multiple students in a classroom. In turn, this means that a classroom has multiple students. If there is only one student in a classroom, consider specifying that a student "has" a classroom instead. 

### Specify a study design

A study design is a set of variables. You assign one to be a dependent variable and one or more to be independent variables. 
```
design = ts.Design(
    dv=math,
    ivs=[tutoring, age, funding_aid]
)
```
### Query Tisane for a statistical model and receive a script back!
You can ask Tisane for a statistical model that matches your study design!
```
ts.infer_statistical_model_from_design(design)
```
And Tisane will output a script for you to run!: model.py