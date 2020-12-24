% ====== Generators ======

% What are all the components to an analysis? 

% each IV 
% transformations

% the DV
:- numeric(Y)

% the particular statistical model
R :- residuals % ??? 
regression(I, D) :- normal(R), numeric(Y)

% any model-specific parameters (e.g., family, etc.) 




% What if we represent conceptual graph as facts in ASP?

% Concepts as Nodes
#const n
node(1..3). % 1: Intelligence, 2: Tutoring, 3: Test_Score

% Causation as Directed Edges
directed_edge(1, 3).
directed_edge(2, 3).

% Correlation as Undirected Edges
undirected_edge(1, 2).

concept(intelligence).
concept(tutoring).
concept(test_score). 

causes(intelligence, test_score). 
causes(tutoring, test_score). 
correlates(intelligence, tutoring). 

regression :- normal_residuals(X, Y), numeric(Y), homoscedastic_residuals(X, Y)



% Generate



% Two-stage ASP idea: 
- incrementality -- bake in interactivity 
% Idea: What if we can generate effects sets in ASP? (use some kind of reachability analysis)
