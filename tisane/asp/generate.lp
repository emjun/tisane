%%%%% Generate %%%%%
% What it means for variables to be in a statistical model
explains(X0, Y) :- model(X0, Y). 
predicted(Y) :- explains(X0, Y).
predictor(X0) :- explains(X0, Y).
predictor(X1) :- explains(X0, Y).

% For constructing edges in conceptual graph
cause_or_correlate(X, Y) :- cause(X, Y).
cause_or_correlate(X, Y) :- correlate(X, Y).

% Main effects (IV, DV)
cause_or_correlate(X, Y) :- predictor(X), predicted(Y).

% Interaction effects (between IVs)
cause_or_correlate(X0, X1) :- interaction(X0, X1), cause_or_correlate(X0, Y), cause_or_correlate(X1, Y).

% Data types
has_datatype(V) :- categorical(V). % For ensuring that all variables have a data type
has_datatype(V) :- numeric(V). % For ensuring that all variables have a data type 

categorical(V) :- binary(V).
categorical(V) :- ordinal(V).