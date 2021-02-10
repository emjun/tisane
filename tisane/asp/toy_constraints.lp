%%%%% Generate %%%%%
% What it means for variables to be in a statistical model
explains(X0,X1, Y) :-model(X0,X1, Y). 
predicted(Y) :-explains(X0,X1, Y).
predictor(X0) :-explains(X0,X1, Y).
predictor(X1) :-explains(X0,X1, Y).

% For constructing edges in conceptual graph
cause_or_correlate(X, Y) :-cause(X, Y).
cause_or_correlate(X, Y) :-correlate(X, Y).

% Main effects (IV, DV)
cause_or_correlate(X, Y) :-predictor(X), predicted(Y).

% Interaction effects (between IVs)
cause_or_correlate(X0, X1) :-interaction(X0, X1), cause_or_correlate(X0, Y), cause_or_correlate(X1, Y).

% Data types
has_datatype(V) :- categorical(V). % For ensuring that all variables have a data type (assumes we want SAT result)
has_datatype(V) :- numeric(V). % For ensuring that all variables have a data type (assumes we want SAT result)
categorical(V) :-binary(V).
categorical(V) :-ordinal(V).

%%%%% Define %%%%%
% Link function
transformation(Y, identity) :- link(Y, identity). % for SM -> ED
transformation(Y, log) :- link(Y, log). % TODO: enumerate more facts for all possible link functions

% Variance function 
distribution(Y, gaussian) :- variance(Y, gaussian). % SM -> ED
distribution(Y, inverse_gaussian) :-variance(Y, inverse_gaussian).

% Data schema from link function 
numeric(V) :-link(V, identity).
numeric(V) :-link(V, ln).
numeric(V) :-link(V, square_root).
categorical(V) :- link(V, log_log). % if get two different data types, that might be fine!
categorical(V) :- link(V, probit). % if get two different data types, that might be fine!
categorical(V) :-link(V, logit).

% Data schema from variance function
numeric(V) :-transformation(V, log). 
binary(V) :-transformation(V, binomial). 
categorical(V) :-transformation(V, multinomial).

% Silence properties 
% Interaction terms are not required of all models
interaction(0,0) :-#false.


%%%%% Test %%%%%
%% Data types
% cannot be categorical and numeric 
:-numeric(V), categorical(V).

% Ensure every predicted/predictor has a data type!
:-predicted(V), not has_datatype(V).
:-predictor(V), not has_datatype(V).

%%%%% Show %%%%%
#show 0. 
