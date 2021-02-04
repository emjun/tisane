%%%%% SM -> ED %%%%%
% TODO: Break these rules apart into separate files?

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
% TODO: Want to support transformations that are not the link function, too 

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

% TODO: Data collection procedure
% mixed effects

% Silence properties 
% Interaction terms are not required of all models
interaction(0,0) :-#false.


%%%%% Test %%%%%
%% Data types
% cannot be categorical and numeric 
:-numeric(V), categorical(V).
%ordinal(V) :- not binary(V). % cannot be binary and ordinal?? - allow for now until have example want to work through.

% Ensure every predicted/predictor has a data type!
:-predicted(V), not has_datatype(V).
:-predictor(V), not has_datatype(V).

%%%%% Show %%%%%
#show 0. 

model(intelligence,age,sat).
link(sat, identity).
variance(sat, gaussian).
%binary(sat).
%binary(intelligence).
%numeric(age). 



%*
%%%%% Sample program %%%%%

% Y ~ X1 + X2
%numeric(tutoring). % causes UNSAT if binary(tutoring) also included - yay!
%cause_or_correlate(sex, sat). % can add arbitrary relationships to effects set (from user input)
% TODO: How to make sure we get all data type info for each variable?
*%

% TODO: What and how to represent differences in main vs. interacion vs. mixed effects?
% Focus on main effects only for now. 
% 1. get to compile set of facts --> mostly done 
% 2. query loop with facts --> START HERE
% 3. output based on SAT facts 
% Related to 3: What if questions about data collection just need to be asked to user (more than one measurement, one, etc.?)

%* Y ~ X1 + X2 + X1*X2
%cause_or_correlate(sex, sat). % can add arbitrary relationships to effects set (from user input)
*%