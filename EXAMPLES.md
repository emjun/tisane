# API Overview through Examples 

<!-- Generalized linear mixed effects models can help analysts answer research questions when they h helpful for nested, repeated, and non-nested.  -->
Data collection procedures may lead to intentional and unintentional clustering in the data that affects how data are measured and, ultimately, what statistical models are inferred and constructed. There are two common collection 
procedures that lead to clustering: hierarchies and repeated measures. Generalized linear mixed effects models (GLMMS) can help with both situations! Generalized linear mixed effecst models can also handle non-nested complexities. 

Below, we will illustrate how Tisane can help with nested, repeated, and non-nested settings where GLMMs are applicable, starting with a very simple example.

For all API examples, add comment for what the line of code means in plain English

--- 

## Simple linear model without any clustering
Source: This example comes from [1]. 

### Authoring a simple model with only main effects
This is an example "in which physical endurance of n = 245 adults is predicted form their age and the number of years of vigorous physical exercise in which they have engaged." Each adult has an _age_, a number of years of physical _exercise_, and a number of minutes of sustained jogging on a treadmill (a proxy for _endurance_) at the time of this study.

```
import tisane as ts
import pandas as pd 

## Load data
df = pd.read_csv("./exercise_simple.csv")

## Declare observed variables
# The researchers observe participants/cases (observational unit). 
pid = ts.Unit("case", cardinality=245) # pid is an observational unit. There are 245 adults.

# Each pid (cause/adult) has an age value, which is numeric.
# Verbose: Each instance of pid has one instance of a numeric variable age.
# Note: By default, number_of_instances equals 1. The parameter value is explicitly set below for clarity. 
age = pid.numeric("age", number_of_instances=1)  # participant age

# Each pid has an exercise value, which is numeric .
# Verbose: Each instance of pid has one instance of a numeric variable exercise. 
exercise = pid.numeric("exercise")  # years of vigorous physical exercise

# Each pid has an endurance value, which is numeric. 
# Verbose: Each instance of pid has one instance of a numeric variable endurance. 
endurance = pid.numeric("endurance") # number of minutes of sustained jogging on a treadmill
    
## Declare conceptual relationships between the observed variables
exercise.causes(endurance) 
age.associates_with(endurance)

## Query relatioships to infer a statistical model and generate a script
# Author query by partially authoring a statistical model as a Design
design = ts.Design(dv=endurance, ivs=[age, exercise]).assign_data(df) 
ts.infer_statistical_model_from_design(design=design)
```

### Adding in an interaction 
Extending the example above, suppose we want to express that _age_ moderates the effect of _exercise_ on _endurance_. In other words, how do we specify an interaction effect between two or more variables? 
We would add the following conceptual relationship: 
```
# Reads: Age moderates the effect of exercise on endurance
age.moderates(moderator=[exercise], on=endurance)
```
> Maybe we should rename "moderator" parameter to simply "variables"? 

> Should we also ensure that age.moderates(moderator=[exercise], on=endurance) is equivalent to exercise.moderates(moderator=[age], on=endurance)? In the current implementation, these two statements are treated as two different conceptual relationships (different node and edges), but they are statistically equivalent. The same interaction effect (i.e., age*exercise) is included in the statistical model. 

--- 

## Nested/hierarchical data
Source: This example comes from [1]. 

Consider another health dataset where adults participate in exercise groups that promote different approaches to weight loss. Researchers are interested in understanding how motivation and group approaches affect weight loss. Researchers observe that individuals nested within the same group tend to cluster together: 

"We assume that the data have been collected
from intact women's groups that have a focus on diet and weight control; the
groups meet regularly to discuss diet and weight control, and have some level of
cohesion. We may thus expect some correlation among the women within a group j
in both their motivation to lose weight and weight loss success. 

There are a total of 386 women in all distributed across the 40 groups. Group
size ranges from 5 to 15 women. There is substantial clustering in the data,
reflected in the fact that the groups differe substantially in mean pounds of
weight lost, from a low mean of 9.75 points lost to a high mean of 24.43 pounds
lost."

```
## Load data
df = pd.read_csv("./exercise_groups.csv")

## Declare observed variables
# Researchers observe adults/members as the observational unit.
adult = ts.Unit("member", cardinality=386) # 386 adults
# Each adult has a value for motivation, which is ordinal 

# Each adult has a motivation level value, which is ordinal.
# Verbose: Each instance of adult has one instance of an ordinal variable motivation level. 
motivation_level = adult.ordinal("motivation", order=[1, 2, 3, 4, 5, 6])

# Each adult has a pounds lost value, which is numeric 
# Verbose: Each instance of adult has one instance of a numeric variable pounds lost. 
pounds_lost = adult.numeric("pounds_lost")

# Researchers treat groups of adults. In other words, groups are an experimental unit. 
group = ts.Unit("group", cardinality=40)  # 40 groups
# Each group has one of two weight loss treatment approaches, which is nominal. 
# Note: By default, number_of_instances equals 1. The parameter value is explicitly set below for clarity. 
treatment_approach = group.nominal("treatment", cardinality=2, number_of_instances=1) # 2 choices of approach: "Control" and "Treatment"

## Declare conceptual relationships between the observed variables
motivation_level.cause(pounds_lost)
treatment_approach.causes(pounds_lost)

## Declare data measurement relationships between the observed variables
# Adults are nested within groups
# A nested relationship is assumed to be many (adult) to 1 (group). Many adults are in the same group, and each adult is assigned only one group. 
adult.nests_within(group) 

## Query relatioships to infer a statistical model and generate a script
# Author query by partially authoring a statistical model as a Design
# Notice that the ivs come from different observational/experimental units. In other words, they are at different "levels." 
# Tisane will detect this and automatically infer the random effects structure to control for adult group membership (i.e., random intercept for group). 
design = ts.Design(dv=pounds_lost, ivs=[treatment_approach, motivation_level]).assign_data(df)
ts.infer_statistical_model_from_design(design=design)
```

--- 

## Repeated measures 
So far, we have considered examples in which each observational unit is measured once. However, it is common to collect data at multiple time points (e.g., longitudinal study). Consider the next example from a research article on pig growth over time due to feed nutrition [4]. 

Researchers tracked 82 pigs for 12 weeks. Each pig received one of three levels of vitamin E and one of three levels of copper. 
```
## Load data 
df = pd.read_csv("./pigs.csv")

## Declare experimental setting 
# Week is an experimental environment or setup variable because it is neither a unit nor a measure of a unit. 
week = ts.SetUp("Week", cardinality=12)

## Declare observed variables
# Researchers treat pigs as the experimental unit.
pig = ts.Unit("Pig", cardinality=82)
# Each pig has a vitamin E value, which is ordinal.
# Verbose: Each instance of pig has one instance of an ordinal variable vitamin E level. 
# Informally: Each pig receives a specific amount of vitamin E. 
# Note: By default, number_of_instances equals 1. The parameter value is explicitly set below for clarity. Note: 
vitamin_e = pig.ordinal("Evit", order=["Evit000", "Evit100", "Evit200"], number_of_instances=1)

# Each pig has a copper value, which is ordinal.
# Verbose: Each instance of pig has one instance of an ordinal variable copper level. 
# Informally: Each pig receives a specific amount of copper. 
# Note: By default, number_of_instances equals 1. The parameter value is explicitly set below for clarity. 
copper = pig.ordinal("Cu", order=["Cu000", "Cu035", "Cu175"], number_of_instances=1)

# Repeated measure
# Each pig has a weight value, which is numeric, for each value of week. 
# Verbose: Each instance of pig has one instance of a numeric variable weight for each value of week. 
weight = pig.numeric("Weight", number_of_instances=week) 

## Declare conceptual relationships between the observed variables
time.causes(weight)

## Query relatioships to infer a statistical model and generate a script
# Author query by partially authoring a statistical model as a Design
# Tisane will detect the repeated measure and automatically infer the random effects structure to control for repeated, non-independent observations from the same pig (i.e., random intercept for pig)
design = ts.Design(dv=weight, ivs=[time]).assign_data(df)
ts.infer_statistical_model_from_design(design=design)
```

--- 

## Nesting + Repeated measures 
Source: This example comes from [4]. 

What if we have nested/hierarchical data AND repeated measures? We can express BOTH in a Tisane program, and Tisane will handle both!

Taking the pigs example above, one key aspect of the data collection procedure was that 82 pigs were housed in 22 litters. This means that some pigs may be more similar to each other than others (another form of clustering!), perhaps due to litter space, litter location, etc. We should account for these potentially confounding factors due to litter in the statistical model. How? Well, we can let Tisane figure out the details! 

To the above program, we add the following declarations: 
```
# Researchers treat litters as an observational unit. 
litter = ts.Unit("Litter", cardinality=22)

# Adults are nested within groups
# A nested relationship is assumed to be many (pig) to 1 (litter). Many pigs are in the same litter, and each pig is assigned/lives in only one litter. 
pig.nests_within(litter)
```

The complete program then is: 
```
## Load data 
df = pd.read_csv("./pigs.csv")

## Declare experimental setting 
week = ts.SetUp("Week", cardinality=12)

## Declare observed variables
pig = ts.Unit("Pig", cardinality=82)
vitamin_e = pig.ordinal("Evit", order=["Evit000", "Evit100", "Evit200"], number_of_instances=1)
copper = pig.ordinal("Cu", order=["Cu000", "Cu035", "Cu175"], number_of_instances=1)
weight = pig.numeric("Weight", number_of_instances=week) 

litter = ts.Unit("Litter", cardinality=22)

## Declare conceptual relationships between the observed variables
time.causes(weight)

## Declare data measurement relationships between the observed variables
pig.nests_within(litter)

## Query relatioships to infer a statistical model and generate a script
# Author query by partially authoring a statistical model as a Design
# Tisane will detect the repeated measure and automatically infer the random effects structure that (i) controls for repeated, non-independent observations from the same pig (i.e., random intercept for pig) and (ii) controls for pigs nested within litters (i.e., random intercept for litter)
design = ts.Design(dv=weight, ivs=[time]).assign_data(df)
ts.infer_statistical_model_from_design(design=design)
```

### Note
[statsmodels](https://www.statsmodels.org/stable/index.html), a popular Python package for statistical analysis, includes the above pig growth example as in their documentation for [linear mixed-effects models](https://www.statsmodels.org/stable/mixed_linear.html). Interestingly, the statsmodels documentation ignores the fact that pigs are nested in litters and omits the random effect of litter! We were able to detect this omission by specifying variable relationships in Tisane. In this way, Tisane is helpful for authoring and sanity checking analyses.

--- 

## Non-nesting 
NOTE: I feel least certain about this API. 
Note: These non-nesting settings require

Source: This example comes from [2]. 

Non-nested occur because there are multiple ways to divide the observations. Two ways this happens is when there are multiple categorizing values. For example, <social science example>. 
Another example, which may at first seem a bit unexpected is looking at trial vs. participant perspectives, which, as Barr et al. describe, is common in linguistics []. For example….
This is also similar to the motivating example in Barr et al. [] and []. 

Node: Cannot account for lower level than level of DV in a GLM

## Edge cases 
Models with only random effects

## Limitations 

## STILL IN PROGRESS: 
I re-implemented the candidate model generation procedure to no longer rely on any SMT. I am still in the progress of adding graph inference rules for generating random effects for interactions following Barr's updated recommendations []. 

## QUESTIONS: 
1. For constructing queries, should we rename ``ts.Design`` to ``ts.Query`` so that it's clear that the analyst is authoring a query? 


--- 

## References 
Gelman and Hill provide an overview of GLMMs and related methods [2]. Kreft and De Leeuw discuss the usage of GLMMs with nested, or hierarchical data, in education research [3]. Cohen, Cohen, West, and Aiken provide overview of key principles and modeling basics [1].

1. Cohen, P., West, S. G., & Aiken, L. S. (2014). Applied multiple regression/correlation analysis for the behavioral sciences. Psychology press.
2. Gelman, A., & Hill, J. (2006). Data analysis using regression and multilevel/hierarchical models. Cambridge university press.
3. Kreft, I. G., Kreft, I., & de Leeuw, J. (1998). Introducing multilevel modeling. Sage.
4. Lauridsen, C., Højsgaard, S.,Sørensen, M.T. C. (1999) Influence of Dietary Rapeseed Oli, Vitamin E, and Copper on Performance and Antioxidant and Oxidative Status of Pigs. J. Anim. Sci.77:906-916 