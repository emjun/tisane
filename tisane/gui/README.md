# Tisane GUI
Purpose: Asking disambiguation questions, offering interactions for helping analysts answer those questions, and saving answers to use when inferring a statistical model from a Tisane specification. 

The motivating principle behind the interaction model behind Tisane, which includes the GUI and disambiguation questions, is to derive statistical models based on conceptual and data measurement relationships analysts express. 

## Key challenge 
The primary challenge we are trying to address through the Tisane GUI is to (1) suggest potential oversights in initial model specification at the query level based on the variable relationships the analyst expressed and (2) elicit runtime data-specific information (i.e., family and link functions). Both these tasks are necessary in order to generate a final statistical model and ensure that it has statistical conclusion and external validity. 

A secondary challenge is to discourage analysts from p-hacking their statistical models. This challenge is already baked into our approach in designing Tisane because analysts author programs that describe variables and variable relationships, not statistical models directly in Tisane. 

In order to address these challenges, we have specific design goals, below. 

## Design goals
1. Provide an overiew of the query and interactively added variables to keep "local context" that expresses/represents analyst goals.  
2. Require analysts to consider omissions/alternatives that further their analysis goals. 
3. Guide users through rationale for why Tisane makes specific suggestsions. Imagine users who may not know what a "main effect" or "random effect" is. 
- This means that we should define terms wherever possible.
- This also means that we should indicate implications of decisions. (?) 

> FEEDBACK REQUESTED: Do you think we should have any additional design goals/requirements? 

## Development notes
Example apps
- Code for all these examples: https://github.com/plotly/dash-sample-apps/tree/main/apps

- Overall layout with specific regions designated to specific tasks: https://dash-gallery.plotly.host/dash-daq-tektronix350/
- Overall layout, breadcrumbs at top (might use something like this for tracking progress): https://dash-gallery.plotly.host/ddk-oil-and-gas-demo/
- Overall layout, nice clean: https://dash-gallery.plotly.host/dash-aix360-heart/
- [For the tabbed section on the left (could use for Main, Interaction, Random Effects, and Family/Link)](https://dash-gallery.plotly.host/dash-alignment-chart/)


### Styling
Dash Bootstrap documentation: https://dash-bootstrap-components.opensource.faculty.ai/docs/
