# Overview of the Linguistics example

## Sources
The [original paper]() reference:  

```

```

The [data](https://www.rdocumentation.org/packages/influence.ME/versions/0.9-3/topics/school23) is available through [influence.ME](https://www.rdocumentation.org/packages/influence.ME/versions/0.9-9). The dataset is a subsample of the larger [NELS-88 dataset](https://nces.ed.gov/surveys/nels88/).

The data is simulated for a hypothetical [``lexical decision'' experiment](). 

Locally, the dataset is available [here](). This local copy was downloaded from RDocumentation for testing purposes. 

## Summary of study design
The example study design comes from a ``hypothetical lexical decision experiment, [where] subjects see strings of letters and have to decide whether or not each string forms an English word, while their response times are measured. Each subject is exposed to two types of words, forming condition A and condition B of the experiment. The words in one condition differ from those in the other condition on some intrinsic categorical dimension (e.g., syntactic class), comprising a word-type manipulation that is within-subjects and between-items. The question is whether reaction times are systematically different between condition A and condition B.'

- Dependent variable: response time 
- Subjects see both types of words
- Two types of words (condition A, B) --> within-subjects (because subjects see both types of words), between-items (because each word can only have one type)

Toy dataset: 
- simulated data
- four subjects, four items --> ``two observations per treatment condition per participant''

## Tisane data analysis 
```
Word and Subject as units

word = ts.Unit("Word/item")
subject = ts.Unit("Subject")

reaction_time = subject.numeric("Time", number_of_instances=word) # Each subject has 1 Time value for each word
type = word.nominal("Word_type", number_of_instances=1) # Each word has 1 Word type
type = subject.nominal("Word_type", number_of_instances=2) # Each subject sees 2 Word types

word.nests_within(subject, number_of_instances=2) 
```


```
Condition and Subject as units (this feels more awkward and different from the other examples)

condition = ts.Unit("Word_type")
subject = ts.Unit("Subject")

reaction_time = subject.numeric("Time", number_of_instances=word) # Each subject has 1 Time value for each word
word = condition.nominal("Word", number_of_instances=2) # Each condition has 2 instances

condition.nests_within(subject, number_of_instances=2) # Each subject has 2 conditions -- this feels different than how you might specify condition in other situations
```


```
Condition and Subject as units

condition = subject.nominal("Word_type", number_of_instances=2) # Each subject has 2 instances of Word type
subject = ts.Unit("Subject")


word = condition.nominal("Word", number_of_instances=2) # Each condition has 2 words
reaction_time = subject.numeric("Time", number_of_instances=word) # Each subject has 1 Time value for each word

```

```
Word and Subject as units
word = ts.Unit("Word")
subject = ts.Unit("Subject")

condition = word.nominal("Word_type", number_of_instances=1) # Each word has 1 Word type
# Reads: Subject has a reaction time value for each instance of word
reaction_time = subject.numeric("Time", number_of_instances=word) # Each subject has 1 Time value for each word --> repeated measures
# Reads: Word has a reaction time value...
reaction_time = word.numeric("Time", number_of_instances=) # Each subject has 1 Time value for each word --> repeated measures

subject.has(condition, number_of_instances=2)

word.nests_within(subject, number_of_instance=subject) # Each word is nested within each subject OR Each subject sees each word

# This might be the "right" Tisane specification, but we might need to rethink/think through algorithm for interring random effects. 
```

## Original data analysis 

## Of note: Statsmodels data analysis



