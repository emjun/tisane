# More on conceptual relationships: Causes vs. Associates with? Which to choose?
[For the latest discussion and planned steps on this topic, please see and feel free to chime in on this Request For Comments (RFC!)](https://github.com/emjun/tisane/issues/33#issue-1073669958)
Tisane currently provides two types of conceptual relationships: `causes` and `associates_with`. This doc covers when and how to use these verbs. 

If a user provides associates_with, we walk them through possible association patterns to identify the underlying causal relationships. In other words, `associates_with` indicates a need for disambiguation to compile to a series of `causes` statements.

To do this well, we need to resolve two competing interests: causal accuracy and usability. Prioritizing causal accuracy, the system should help an analyst distinguish and choose among an exhaustive list of possible causal situations. However, doing so may be unusable because the task of differentiating among numerous possible causal situations may be unrealistic for analysts unfamiliar with causality. These concerns do not seem insurmountable. 

With an infinite number of hidden variables, there are an infinite number of possible causal relationships. We could restrict the number of hidden variables an analyst considers. This decision compromises causal accuracy for usability. If we had a justifiable cap on hidden variables, it may be worthwhile to take this approach. 

Another perspective: If the goal is to translate each `associates_with` into a set of `causes`, why provide `associates_with` at all?

The primary reason I wanted to provide both was because of the following: 
- Analysts are sometimes unsure about the causal edges in their conceptual models. This uncertainty can be due to their own *lack of knowledge* or because the relationships are *hypothesized* but not known and now the analysts want to see if data supports the hypothesized relationships. 
- There may be a *lack of definitive evidence in a domain* about some causal edges and paths (that may involve multiple variables).

In all these cases, it seems important to acknowledge what is known, what is hypothesized/the focus of inquiry, and what is asserted for the scope of the analysis. (accurate documentation, transparency)

In the current version of Tisane, analysts can express any relationships they might know or are probing into using `causes`. If analysts do not want to assert any causal relationships due to a perceived lack of evidence in their field, they should use `associates_with`. Whenever possible, analysts should use `causes` instead of `associates_with`.

Tisane's model inference process makes argubaly less useful covariate selection recommendations based on `associates_with` relationships. Tisane looks for variables that have `associates_with` relationships with both one of the IVs and the DV. Tisane suggests these variables as covariates with caution, including a warning in the Tisane GUI and a tooltip explaining to analysts that `associates_with` edges may have additional causal confounders that are not specified or detectable with the current specification. 

For the `causes` relationships, Tisane uses the disjunctive criteria, developed for settings where researchers may be uncertain about their causal models, to recommend possible confounders as covariates. 

We assume that the set of IVs an end-user provides in their query are the ones they are most interested in and want to treat as exposures.
> What happens if the initial choice of variables could lead to confusion in interpretation of results?
We currently treat each IV as a separate exposure and combine all confounders into one model. In some cases, this may lead to interpretation confusion. For example, if the model includes two variables on the same causal path, one of the variables may appear to have no effect on the outcome even if it does (due to d-separation). We currently expect analysts to be aware of and interpret their results accurately in light of their variable selection choices. In their input queries, analysts should include only the variables they absolutely care the most about in their queries. 