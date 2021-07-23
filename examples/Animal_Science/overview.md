# Overview of the Animal Science example

## Sources
The [original paper](https://pubmed.ncbi.nlm.nih.gov/10328356/) reference:  
Lauridsen, C., Højsgaard, S.,Sørensen, M.T. C. (1999) Influence of Dietary Rapeseed Oli, Vitamin E, and Copper on Performance and Antioxidant and Oxidative Status of Pigs. J. Anim. Sci.77:906-916 
```
@article{lauridsen1999influence,
  title={Influence of dietary rapeseed oil, vitamin E, and copper on the performance and the antioxidative and oxidative status of pigs},
  author={Lauridsen, Charlotte and H{\o}jsgaard, S{\o}ren and S{\o}rensen, Martin Tang},
  journal={Journal of animal science},
  volume={77},
  number={4},
  pages={906--916},
  year={1999},
  publisher={Oxford University Press}
}
```

The [data](https://vincentarelbundock.github.io/Rdatasets/doc/geepack/dietox.html) is available through [Rdatasets](https://vincentarelbundock.github.io/Rdatasets/) and is used as an [example of mixed-effects linear models in statsmodels](https://www.statsmodels.org/stable/examples/notebooks/generated/mixed_lm_example.html). 

Locally, the pigs dataset is available [here](https://github.com/emjun/tisane/blob/main/examples/data/dietox.csv). This local copy was downloaded from Rdatasets for testing purposes. 

## Summary of study design
- 82 pigs total, across 22 litters.
- Each pig received one of 10 dietary conditions: 3 vitamin E levels x 3 copper levels (Diets 1-9) and a baseline(``Basal diet''). Diets 1-9 were defined by nutritional additions made to the baseline basal diet. 
- Pigs could freely eat and drink.
- The researchers recorded pig weight and feed consumption every week. 
- The pigs in the same litter were slaughtered on the same day when they weighed approxiatmely 100kg. 
- Three days prior to slaughter, researchers measured and recorded characteristics of blood samples. 
- Researchers measured feed properties for concentrations of minerals and vitamins. 

From just reading, I would want to translate/write a program that contained the following:
```
pigs.in(litter) # pigs nested within litters
pig.has(diet, 1)
pigs.have(weight).foreach(week)
pigs.have(feed_consumption).foreach(week)

pig.has(diet, 1) => 
pig.has(vitaminE, 1)
pig.has(copper, 1)
```

## Original data analysis 
### Types of clustering the authors were concerned about and aware of: 
- _``For growth and feed intake data, repeated measurements were made on the same experimental unit (i.e., pig), and data were, therefore, expected to exhibit some sort of correlation. This was accounted for by considering statistical models in which performance was modeled as a function of time; all measurements, not only total weight gain or feed intake at the end of the experimental period, were used in the statistical analysis.''_
--> random effect for repeated measures of the same pig
--> time as a main effect

- _``Furthermore, data from pigs within a litter were expected to be correlated.''_
--> random effect of litter 

### Approach 
_``Effect of treatments at specific timepoints was investigated using a standard ANOVA model with a random litter effect. The effect of different levels of the same treatment was investigated by pairwise comparisons.''_
--> Compare across multiple timepoints using mixed-effects ANOVA
--> [UNCLEAR] ``different levels of the same treatment'' == compare timepoints within the same treatment conditions?

_``Clearly, at the beginning of the experiment, there is no treatment effect (Figure 1). However, a treatment effect began to appear after 3 wk. Therefore, the weight gain from wk 4 to 12 was modeled with a third-degree polynomial, with the intercept depending on the treatment and random linear regression coefficients...random litter effect accounting for dependency among pigs from the same litter, and B_eci is a random effect accounting for correlation between repeated measurements on the same animal.''_
--> Random effect for litter
--> Random effect of animal
--> [LIMITATION] The original paper used a third-degree polynomial model, which we do not support in Tisane. 

_``A profile diagram showed an approximately linear decrease in utilization over time (except in wk 12, when the decrease seemed to be larger). To study whether any treatment effect occurred, this linear decrease was investigated, allowing slope and intercept of the curves to depend on the treatments.''_
--> random slope and intercept of animal are correlated

_``For investigating the influence of rapeseed oil on the performance of pigs, analyses similar to those described above were conducted on the basis of the basal diet and Diet 1.''_
--> Additional pairwise comparisons?

_``The effects of vitamin E and copper on performance traits for the entire experimental period, as well as on blood and liver traits, were analyzed using an ANOVA model with a random litter effect. Because the interaction between dietary vitamin E and copper was not statistically significant for most of the traits, the following model was used... [linear mode with no interaction effect].''_
--> random effect of litter
--> [UNKNOWN] how did the researchers establish that there was no interaction effect?

### Reported results 
**Note, some of these results refer to pairwise comparisons and were obtained outside of the random effects ANOVA**

#### DV: Weight
_``Table 4 shows the influence of dietary treatments on the performance of the pigs. For all performance traits, no statistically significant differences were found between treatments, except between dietary vitamin E levels with regard to ADG, for the entire period (i.e., performance measured at the end of the experiment).''_

_``However, when the individual growth curves were analyzed (not shown), a copper effect on weekly weight gain was found for wk 3. Pigs fed 175 ppm copper grew faster (P = .02) than did pigs fed 35 ppm copper, but no differences were found between pigs fed 175 and 0 ppm of supplemental copper.''_

_``Differences on feed intake among treatments were consistent with those found for weight gain; the only treatment effect was the supplementation with copper, which caused an increase in the feed intake in wk 3 (P < .05 for 175 vs 35 ppm). Feed utilization was not influenced by copper treatments. No effect of vitamin E was observed on weekly performance data.''_

_``For pigs fed rapeseed oil, the rate of growth tended to increase and the feed intake tended to be less until about wk 6 compared with pigs fed the basal diet (P < .10). However, differences were not statistically significant, and the results are, therefore, not shown.''_

#### DV: Blood Responses, note: these values are not provided in the dataset
_``Supplementation with vitamin E increased the concentration of this vitamin in plasma ( P < .001), but the increase did not differ between the two levels of supplementation (P > .10) (Table 5).''_

_``Pigs fed rapeseed oil had a higher concentration of vitamin E in plasma ( P = .004) than pigs fed the basal diet.''_

_``There was no interaction between dietary vitamin E and copper for this trait.''_

_``The concentration of vitamin C, the activity of the antioxidative enzymes in the plasma, and the hematological traits (PCV, concentration of hemoglobin, spontaneous hemolysis in vitro, and plasma concentrations of Na+ and K+) were not influenced by the dietary treatments.''_

_``Increasing levels of copper in the diet tended to increase (P = .08) the activity of GOT, and the activity of GOT in plasma of pigs fed rapeseed oil was slightly lower than that of pigs on the basal diet (P = .06) (Table 5). No influence of dietary vitamin E was observed on the plasma activity of GOT. The activity of CK did not differ between treatment groups. Dietary treatments influenced neither ELP nor the susceptibility of the plasma to lipid oxidation measured as TBARS. However, there was a tendency (P = .11) for a decreased level of plasma TBARS at 0 min of pigs fed dietary copper.''_

_``Total cholesterol (20 ± .46 mg/dL) and triglyceride (29 ± 1.69 mg/dL) content of plasma were not influenced by supplemental dietary vitamin E or copper (Diets 1 to 9). Pigs fed the basal diet had a lower content of total cholesterol (17 mg/dL, P = .023) and triglycerides (16 mg/dL, P = .005) in plasma than pigs fed rapeseed oil (21 and 29 mg/dL for cholesterol and triglycerides, respectively). Correlation between plasma vitamin E and plasma triglycerides (r = .90, P = .0002) and of plasma vitamin E and plasma cholesterol (r = .64, P = .01) were found. Thus, when the vitamin E concentration was expressed in relation to the content of triglycerides in plasma instead of per milliliter of plasma, as in Table 5, the difference between the two dietary treatments was smaller but still significant (P = .03) (6.5 mg of vitamin E per milligram of triglycerides per milliliter of plasma from pigs on the basal diet and 7.9 mg of vitamin E per milligram of triglycerides per milliliter of plasma from those on the rapeseed oil diet).''_

Observation: Looking at Table 5, there seem to be different numbers of pigs involved in the comparisons of conditions. (Would this be something we could compute to be a potential warning for convergence error?) How is the linear model used?

#### DV: Liver Responses, note: these values are not provided in the dataset
_``The weight of the liver was not influenced by the dietary treatments. Table 6 shows the effects of dietary treatments on the concentration of vitamin E, copper, and vitamin A in the liver and the activities of SOD, Se-GSH-Px, and non-Se-GSH-Px in the liver cytosolic fraction.''_

_``The liver concentration of vitamin E increased with addition of vitamin E to the diets (P < .001), whereas no differences were found between the basal diet and Diet 1 with respect to this trait.''_

_``An interaction was found between dietary vitamin E and copper (P = .05); addition of 35 or 175 ppm copper to the feed increased the vitamin E concentration in the liver, but the increase in vitamin E was similar for both 35 and 175 ppm copper. No interaction between dietary vitamin E and copper was observed for the other traits presented in Table 6.''_

_``Supplementation with 175 mg of copper increased (P < .01) the concentration of copper in the liver. Addition of rapeseed oil to the feed increased (P = .04) the concentration of copper in the liver, whereas no influence of dietary vitamin E was observed with regard to the copper concentration in the liver. Dietary treatments did not influence the activity of SOD, Se- GSH-Px, and non-Se-GSH-Px measured in the liver cytosolic fraction (Table 6).''_

_``The concentration of fat in the liver (2.9 ± .98 g/100 g) was not influenced by the dietary treatments. However, addition of rapeseed oil to the feed affected the fatty acid composition of the liver and elevated ( P = .06) the total concentration of fatty acids (Table 7). Overall, the content of saturated fatty acids was unaffected, but the content of monounsaturated fatty acids and that of polyunsaturated fatty acids were higher (P = .01) in the liver of pigs fed rapeseed oil than in liver of pigs fed the basal diet.''_


_``Dietary vitamin E and copper caused no significant effects on the fatty acid composition of the liver. A significant interaction ( P = . 0 1 ) between dietary vitamin E and copper was observed for the hepatic concentration of C22:6, but, because a similar effect was not found for the other fatty acids, means of this fatty acid were pooled within treatments as for other fatty acids.''_

_``The rates of Fe2+-induced lipid oxidation in livers of pigs on the different feeding regimens are presented in Figure 2. The oxidative changes were larger ( P < .01, at 40 to 120 min) in the livers of pigs fed the basal diet compared with pigs fed diets with rapeseed oil (Figure 2a). The addition of either vitamin E (P = .002) or copper (P = .02) to the feed reduced the oxidative stress of the liver even before Fe2+-induced lipid oxidation (Figure 2b). No differences between the two levels of supplementation of either vitamin E or copper were seen on the inhibition of the Fe2+- induced lipid oxidation, and no significant interactions between dietary vitamin E and copper were observed on the rate of lipid oxidation.''_


## Of note: Statsmodels data analysis


## Tisane data analysis 

#### DV: Weight
In study design, there is a distinction between assignments and observations
- Assignments (e.g., conditions) should exist in the constructors
- Observations (e.g., measures)

Trying to distinguish between two types of statements: 
- There are X types of a condition
- The unit receives N (of the X) types

--> Both read: Unit (LHS) "has" N instances (param) of Measure (RHS)


```
df = pd.read_csv("./examples/data/dietox.csv")

#vitaminE = litter.nominal("Evit", cardinality=3)
#copper = litter.nominal("Cu", cardinality=3)

# Without cardinality info, pass data instead
time = ts.Control("Time", data=df['time'])
pig = ts.Unit("Pig", data=df['pig id'])
litter = ts.Unit("Litter", data=df['litter'])

# With cardinality info, don't pass data
pig = ts.Unit("Pig", cardinality=82)
litter = ts.Unit("Litter", cardinality=22)
week = ts.Control("Week", cardinality=12)

pig.nests_within(litter, number_of_instances=NUMBER_OF_PIGS_IN_A_LITTER) # pigs nested within litters
diet = pig.nominal("Diet", data=df["Evit" * "Cu"], number_of_instances=1) # Each pig has 1 diet
weight = pig.numeric("Weight", number_of_instances=week.cardinality()) # Each pig has 1 instance of a Weight measure corresponding to each week
feed = pig.numeric("Feed consumption", number_of_instances=week) # Each pig has a feed consumption measure corresponding to each week
# The assumption is that there is a "for each" variable passed as number_of_instances @param

# Hypothetical: 
diet = pig.nominal("Diet", data=df["Evit" * "Cu"], number_of_instances=2) # Each pic has two instances of a diet

# Conceptual relationship
time.cause(weight)

# Specify and execute query
design = ts.Design(dv=weight, ivs=[time]).assign_data(df)

ts.infer_statistical_model_from_design(design=design)
```

High-level points: 
- number_of_instances = ratio of Unit to Measure. Unit is always set to "1" 
- number_of_instances can be set to an INT, variable (syntactic sugar for variable.cardinality which returns an INT), which get cast to an internal INT type (i.e., ExactlyOne, GreaterThanOne)
- "exactly" comes in the form of INT
- "up_to" comes in the form of either a function tisane provides (e.g., ts.up_to(....)) or "one_of" (e.g., ts.one_of([1, 2, 3])) which outputs an internal INT type (i.e., ExactlyOne, GreaterThanOne)



