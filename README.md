# tisane
Tisane: Authoring Statistical Models via Formal Reasoning from Conceptual and Data Relationships

**TL;DR:** Analysts can use Tisane to author generalized linear models with or without mixed effects. Tisane infers statistical models from variable relationships (from domain knowledge) that analysts specify. By doing so, Tisane helps analysts avoid common threats to external and statistical conclusion validity. Analysts do not need to be statistical experts! 

[Jump to see examples here.](EXAMPLES.md) Below, we provide an overview of the API and language primitives. 

----

Tisane provides (i) a graph specification language for expressing relationships between variables and (ii) an interactive query and compilation process for inferring a valid statistical model from a set of variables in the graph.

## Graph specification language
### Variables
There are three types of variables: (i) Units, (ii) Measures, and (iii) SetUp, or environmental, variables. 
- ``Unit`` types represent entities that are observed (``observed units`` in the experimental design literature) or the recipients of experimental conditions (``experimental units``). 

```
# There are 386 adults participating in a study on weight loss.
adult = ts.Unit("member", cardinality=386)
```

- ``Measure`` types represent attributes of units that are proxies of underlying constructs. Measures can have one of the following data types: numeric, nominal, or ordinal. Numeric measures have values that lie on an interval or ratio scale. Nominal measures are categorical variables without an ordering between categories. Ordinal measures are categorical variables with an ordering between categories. 

```
# Adults have motivation levels.
motivation_level = adult.ordinal("motivation", order=[1, 2, 3, 4, 5, 6])
# Adults have pounds lost. 
pounds_lost = adult.numeric("pounds_lost")
# Adults have one of four racial identities in this study. 
race = adult.nominal("race group", cardinality=4)
```

- ``SetUp`` types represent study or experimental settings that are global and unrelated to any of the units involved. For example, time is often an environmental variable that differentiates repeated measures but is neither a unit nor a measure. 


```
# Researchers collected 12 weeks of data in this study. 
week = ts.SetUp("Week", order=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
```

Design rationale: We derived this type system from how other software tools focused on study design separate their concerns.

### Relationships between variables
Analysts can use Tisane to express (i) conceptual and (ii) data measurement relationships between variables.

There are three different types of conceptual relationships.
- A variable can *cause* another variable. (e.g., ``motivation_level.causes(pounds_lost)``)
- A variable can be *associated with* another variable. (e.g., ``race.associates_with(pounds_lost)``)
- One or more variables can *moderate* the effect of a variable on another variable.  (e.g., ``age.moderates(moderator=[motivation_level], on=pounds_lost)``)
Currently, a variable, V1, can have a moderated relationship with a variable, V2, without also having a causal or associative relationship with V2.

<!-- > FEEDBACK REQUESTED: Should this be the case? Initially, I though that moderation (which is later translated into an interaction effect) is another way/type of how two variables relate. At the same time, if V1 has a moderated effec on V2, it is implied that V1 has some kind of associative relationship with V2.  -->

These relationships are used to construct an internal graph representation of variables and their relationships with one another.

Internally, Tisane constructs a graph representing these relationships. Graph representation is useufl for inferring statistical models (next section). 

For example, the below graph represents the above relationships. Rectangular nodes are units. Elliptical nodes are measures and set-up variables. The colored node is the dependent variable in the query.The dotted edges connect units to their measures. The solid edges represent conceptual relationships, as labeled. 
![A graph representation created using DOT](examples/readme_dot_graph.png?raw=true)

![A graph representation created using TikZ](examples/readme_graph_tikz.png?raw=true)

## Interactive query and compilation 
Analysts query the relationships they have specified (technically, the internal graph represenation) for a statistical model. For each query, analysts must specify (i) a dependent variable to explain using (ii) a set of independent variables. 

```
design = ts.Design(dv=pounds_lost, ivs=[treatment_approach, motivation_level]).assign_data(df)
ts.infer_statistical_model_from_design(design=design)
```

*Query validation:* To be a valid query, Tisane verifies that the dependent variable does not cause an independent variable. It would be conceptually incorrect to explain a cause from an effect. 

### Interaction model 
A key aspect of Tisane that distinguishes it from other systems, such as [Tea](tea-lang.org/), is the importance of user interaction in guiding the statistical model that is inferred as output and ultimately fit. 

Tisane generates a space of candidate statistical models and asks analysts disambiguation questions for (i) including additional main or interaction effects and, if applicable, correlating (or uncorrelating) random slopes and random intercepts as well as (ii) selecting among viable family/link function pairs.

To help analysts, Tisane provides text explanations and visualizations. For example, to show possible family functions, Tisane simulates data to fit a family function and visualizes it on top of a histogram of the analyst's data and explains to the how to use the visualization to compare family functions. 

### Statistical model inference
After validating a query, Tisane traverses the internal graph representation in order to generate candidate generalized linear models with or without mixed effects. A generalized linear model consists of a model effects structure and a family/link function pair. 


## Query
Analysts query the relationships they have specified (technically, the internal graph represenation) for a statistical model. For each query, analysts must specify (i) a dependent variable to explain using (ii) a set of independent variables.

Query validation: To be a valid query, Tisane verifies that the dependent variable does not cause an independent variable. It would be conceptually incorrect to explain a cause from an effect.

## Statistical model inference
After validating a query, Tisane traverses the internal graph representation in order to generate candidate generalized linear models with or without mixed effects. A generalized linear model consists of a model effects structure and a family/link function pair.

### Model effects structure
<!-- generate possible statistical model effects structures and family/link functions.  -->
Tisane generates candidate main effects, interaction effects, and, if applicable, random effects based on analysts' expressed relationships.

- Tisane aims to direct analysts' attention to variables, especially possible confounders, that the analyst may have overlooked. When generating main effects candidates, Tisane looks for other variables in the graph that may exert causal influence on the dependent variable and are related to the input independent variables.
- Tisane aims to represent conceptual relationships between variables accurately. Based on the main effects analysts choose to include in their output statistical model, Tisane suggests interaction effects to include. Tisane relies on the moderate relationships analysts specified in their input program to infer interaction effects.
- Tisane aims to increase the generalizability of statistical analyses and results by automatically detecting the need for and including random effects. Tisane follows the guidelines outlined in [] and [] to generat the maximal random effects structure.

[INFERENCE.md](tisane/INFERENCE.md) explains all inference rules in greater detail.

### Family/link function
Family and link functions depend on the data types of dependent variables and their distributions.

Based on the data type of the dependent variable, Tisane suggests matched pairs of possible family and link functions to consider. Tisane ensures that analysts consider only valid pairs of family and link functions.

<!-- Two aspects: 
- generating the space
- narrowing the space -->

----

## Limitations
- **Tisane is designed for researchers or analysts who are domain experts and can accurately express their domain knowledge and data measurement/collection details using the Tisane graph specification language.** We performed an initial evaluation of the expressive coverage of Tisane's language and found that it is useful for expressing a breadth of study designs common in HCI. 

<!-- Limitation: If user does not include any variables at one level, no random effects will be generated, cross-level interactions included. Is this justifiable? -->

----

## Benefits
### Tisane helps analysts avoid common threats to statistical conclusion and external validity. 
Specifically, Tisane helps analysts 
- avoid violations of GLM assumptions by inferring random effects and plausible family and link functions
- fishing and false discovery due to conceptually incomplete statistical models
- interaction of the causal relationships with units, interaction of the causal realtionships with settings due to not controlling for the appropriate clusters/non-independence of observations as random effects

These are four of the 37 threats to validity Shadish, Cook, and Campbell outline across internal, external, statistical conclusion, and construct validity [1]. 

---

## Examples
[Check out examples here!](EXAMPLES.md)

## References 
[1] Cook, T. D., Campbell, D. T., & Shadish, W. (2002). Experimental and quasi-experimental designs for generalized causal inference. Boston, MA: Houghton Mifflin.
