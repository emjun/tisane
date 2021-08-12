# API Overview through Examples 

<!-- Generalized linear mixed effects models can help analysts answer research questions when they h helpful for nested, repeated, and non-nested.  -->
Data collection procedures may lead to intentional and unintentional clustering in the data that affects how data are measured and, ultimately, what statistical models are inferred and constructed. There are two common collection 
procedures that lead to clustering: hierarchies and repeated measures. Generalized linear mixed effects models (GLMMS) can help with both situations! Generalized linear mixed effecst models can also handle non-nested complexities. 

Below, we will illustrate how Tisane can help with nested, repeated, and non-nested settings where GLMMs are applicable, starting with a very simple example.

For all API examples, add comment for what the line of code means in plain English

--- 

## Simple linear model without any clustering
Source: This example comes from [3]. 

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

# Each pid (cause/adult) has an age measure, which is numeric.
# Verbose: Each instance of pid has one instance of a numeric variable age.
# Note: By default, number_of_instances equals 1. The parameter value is explicitly set below for clarity. 
age = pid.numeric("age", number_of_instances=1)  # participant age

# Each pid has an exercise measure, which is numeric .
# Verbose: Each instance of pid has one instance of a numeric variable exercise. 
exercise = pid.numeric("exercise")  # years of vigorous physical exercise

# Each pid has an endurance measure, which is numeric. 
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

> FEEDBACK REQUESTED: Should we also ensure that age.moderates(moderator=[exercise], on=endurance) is equivalent to exercise.moderates(moderator=[age], on=endurance)? In the current implementation, these two statements are treated as two different conceptual relationships (different node and edges), but they are statistically equivalent. The same interaction effect (i.e., age*exercise) is included in the statistical model. 

--- 

## Nested/hierarchical data
Source: This example comes from [3]. 

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

# Each adult has a motivation level value, which is ordinal.
# Verbose: Each instance of adult has one instance of an ordinal variable motivation level. 
motivation_level = adult.ordinal("motivation", order=[1, 2, 3, 4, 5, 6])

# Each adult has a pounds lost measure, which is numeric 
# Verbose: Each instance of adult has one instance of a numeric variable pounds lost. 
pounds_lost = adult.numeric("pounds_lost")

# Researchers treat groups of adults. In other words, groups are an experimental unit. 
group = ts.Unit("group", cardinality=40)  # 40 groups
# Each group has one of two weight loss treatment approaches, which is nominal. 
# Note: By default, number_of_instances equals 1. The parameter measure is explicitly set below for clarity. 
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
So far, we have considered examples in which each observational unit is measured once. However, it is common to collect data at multiple time points (e.g., longitudinal study). Consider the next example from a research article on pig growth over time due to feed nutrition [6]. 

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
# Each pig has a vitamin E measure, which is ordinal.
# Verbose: Each instance of pig has one instance of an ordinal variable vitamin E level. 
# Informally: Each pig receives a specific amount of vitamin E. 
# Note: By default, number_of_instances equals 1. The parameter measure is explicitly set below for clarity. Note: 
vitamin_e = pig.ordinal("Evit", order=["Evit000", "Evit100", "Evit200"], number_of_instances=1)

# Each pig has a copper measure, which is ordinal.
# Verbose: Each instance of pig has one instance of an ordinal variable copper level. 
# Informally: Each pig receives a specific amount of copper. 
# Note: By default, number_of_instances equals 1. The parameter value is explicitly set below for clarity. 
copper = pig.ordinal("Cu", order=["Cu000", "Cu035", "Cu175"], number_of_instances=1)

# Repeated measure
# Each pig has a weight measure, which is numeric, for each value of week. 
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

## Nested + Repeated measures 
Source: This example comes from [6]. 

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
GLMMs are useful for analyzing non-nested data where multiple ways to group the observations are justifiable. For example, study participants may be grouped by age, location, and occupation. As another example, experimental results may be examined by participant, condition, or stimulus. Gelman and Hill provide examples of both. Barr et al.'s recommendations for maximal mixed effects structures use the latter as a motivating example [1, 2]. Below, we will draw on Barr et al.'s example from [1]. 

Barr et al. describe a ``hypothetical lexical decision experiment, [where] subjects see strings of letters and have to decide whether or not each string forms an English word, while their response times are measured. Each subject is exposed to two types of words, forming condition A and condition B of the experiment. The words in one condition differ from those in the other condition on some intrinsic categorical dimension (e.g., syntactic class), comprising a word-type manipulation that is within-subjects and between-items. The question is whether reaction times are systematically different between condition A and condition B.'

```
## Load data 
df = pd.read_csv("./linguistics.csv") 

## Declare observed variables
# Subjects are an experimental unit. 
subject = ts.Unit("Subject")

# Words are also an experimental/observational unit. 
word = ts.Unit("Word")

# Each subject has a two values for condition, which is nominal.
# Verbose: Each instance of subject has two instances of a nominal variable condition. 
# Informally: Each subjects sees two (both) conditions. 
condition = subject.nominal("Word type", cardinality=2, number_of_instances=2)

# Repeated measures
# Each subject has a measure reaction time, which is numeric, for each instance of a word
# Verbose: Each instance of subject has one instance of a numeric variable weight for each value of word. 
# Informally: Each subject has a reaction time for each word.
reaction_time = subject.numeric("Time", number_of_instances=word) 

# Each condition has/is comprised of two words. 
condition.has(word, number_of_instances=2)
# ALTERNATIVELY, we could do something like the below (not implemented). It is a bit more complicated to calculate the number of instances, but still doable I think.
# Each word has one value for condition (already defined above as a measure of subject)
word.has(condition, number_of_instances=1) # Condition has two units

## Query relatioships to infer a statistical model and generate a script
design = ts.Design(dv=reaction_time, ivs=[condition]).assign_data(df)
ts.infer_statistical_model_from_design(design=design)
```

> FEEDBACK REQUESTED: The primary limitation/wrinkle in the graph specification language is that it works really well when a measure (i.e., condition) only belongs to one unit (e.g., subject). However, it is difficult when the measure could be used to parition the data in multiple different ways, i.e., according to subject vs. according to word vs. according to condition.  On one hand, it's okay that the language is a bit clunky for non-nesting relationships because they tend to be less common. On the other hand, this edge case may suggest that our language primitives, specifically declaring measures through unit interfaces (e.g., subject.numeric) isn't quite right. 
> The central trouble with a non-nesting relationship is that it's somewhere between an attribution and nesting relationship. It's sort of a composition relationship, but it seems distinct from a strictly nesting relationship where the nested unit (e.g., student) could theoretically be nested in any other nesting unit (e.g., classroom). It also feels inconsistent to describe it as a "has" relationship because attribution relationships can be read off as "<Entity/Unit> has <Attribute/Measure>."

--- 

## Limitations 
In the non-nested case, choosing between main effects or random effects for multiple grouping variables (e.g., age, location, occupation) pertains to assumptions about variance and clustering analysts are willing to make as well as the specific research question an analyst wants to answer (perhaps?). Adding the grouping variables as main effects assumes independence of variance. Adding the grouping variables as random effects assumes non-independence of variance. Picking between these (and other) alternatives seems like a well defined and scoped question to explore during model revision. 
> FEEDBACK REQUESTED: Given the above, is it reasonable to not tackle this particular example in Tisane right now? And argue for out of scope in the paper? 

--- 

## Edge cases 
Currently, a query must specify at least one independent variable. This means that it is not possible to author a GLMM without at least one main effect or interaction effect. My main motivation for this is that analysts typically have a specific main or interaction effect of interest when authoring linear models. At the same time, it would be relatively easy to add this functionality to increase expressivity. 
> FEEDBACK REQUESTED: Which edge cases do you think we should make sure to address/make possible? How do you think about central vs. edge case in GLMMs?

--- 

## STILL IN PROGRESS: 
I re-implemented the candidate model generation procedure to no longer rely on any SMT. I am still in the progress of adding graph inference rules for generating random effects for interactions following Barr's updated recommendations [2]. 

> FEEDBACK REQUESTED: For constructing queries, should we rename ``ts.Design`` to ``ts.Query`` so that it's clear that the analyst is authoring a query? 


--- 

## References 
Gelman and Hill provide an overview of GLMMs and related methods [4]. Kreft and De Leeuw discuss the usage of GLMMs with nested, or hierarchical data, in education research [5]. Cohen, Cohen, West, and Aiken provide overview of key principles and modeling basics [3].

1. Barr, D. J. (2013). Random effects structure for testing interactions in linear mixed-effects models. Frontiers in psychology, 4, 328.
2. Barr, D. J., Levy, R., Scheepers, C., & Tily, H. J. (2013). Random effects structure for confirmatory hypothesis testing: Keep it maximal. Journal of memory and language, 68(3), 255-278.
3. Cohen, P., West, S. G., & Aiken, L. S. (2014). Applied multiple regression/correlation analysis for the behavioral sciences. Psychology press.
4. Gelman, A., & Hill, J. (2006). Data analysis using regression and multilevel/hierarchical models. Cambridge university press.
5. Kreft, I. G., Kreft, I., & de Leeuw, J. (1998). Introducing multilevel modeling. Sage.
6. Lauridsen, C., Højsgaard, S.,Sørensen, M.T. C. (1999) Influence of Dietary Rapeseed Oli, Vitamin E, and Copper on Performance and Antioxidant and Oxidative Status of Pigs. J. Anim. Sci.77:906-916 