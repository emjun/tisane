%%%%% SM -> ED %%%%%

%%%%% Generate %%%%%
explains(X, Y) :- model(X, Y). 
predicted(Y) :- explains(X, Y).
predictor(X) :- explains(X, Y).

% Main effects
% Y ~ X1 + X2


% Interaction effects
% Y ~ X1 + X2 + X1*X2

%link(Y) :- transformation(Y,(linear;log;loglog)).
transformation(Y, linear) :- link(Y, linear). % for SM -> ED
%link(Y, linear) :- transformation(Y, linear). % for ED -> SM
transformation(Y, log) :- link(Y, log). % TODO: enumerate more facts for all possible link functions

%variance(Y) :- distribution(Y, (gaussian; gamma)). % ED -> SM 
distribution(Y, gaussian) :- variance(Y, gaussian). % SM -> ED
distribution(Y, inverse_gaussian) :- variance(Y, inverse_gaussian).

%%%%% Define %%%%%


% Silence properties 

%%%%% Test %%%%%


%%%%% Show %%%%%
#show 0.

%%%%% Sample program %%%%%
% Y ~ X1
model(age, sat). 
link(sat, linear).
variance(sat, gaussian).

% Y ~ X1 + X2
model(age, tutoring, sat).







%* Testing arity - works!
GENERATE:
explains(X0, X1, Y) :- model(X0, X1, Y). 
predicted(Y) :- explains(X0, X1, Y).
predictor(X0) :- explains(X0, X1, Y).
predictor(X1) :- explains(X0, X1, Y).

SAMPLE PROG: 
model(age, tutoring, sat).
*% 
