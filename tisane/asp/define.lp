%%%%% Define %%%%%
% TODO: Want to support transformations that are not the link function, too 

% Link function
transformation(Y, identity) :- link(Y, identity). % for SM -> ED
transformation(Y, log) :- link(Y, log). % TODO: enumerate more facts for all possible link functions

% Variance function 
distribution(Y, gaussian) :- variance(Y, gaussian). % SM -> ED
distribution(Y, inverse_gaussian) :- variance(Y, inverse_gaussian).

%*
% Recommendations for link functions based on data type 
% e.g., poisson distribution and log link for count data
% Variance functions: link functions (linear predictors to outcome)
gaussian: identity, log, inverse 
binomial: logit, probit, cauchit, log, cloglog
gamma: inverse, identity, log 
poisson: log, identity, sqrt 
inverse_gaussian : 1/mu-squared, inverse, identity, log
%SPECIAL CASE: quasi : logit, probit, cloglog, identity, inverse, log, 1/mu-squared, sqrt
*% 

% TODO: Sensitivity analysis when uncertain/multiple could hold. -- as part of output script?

% Data schema from link function 
numeric(V) :- link(V, identity).
numeric(V) :- link(V, ln).
numeric(V) :- link(V, square_root).
categorical(V) :- link(V, log_log). % if get two different data types, that might be fine!
categorical(V) :- link(V, probit). % if get two different data types, that might be fine!
categorical(V) :- link(V, logit).

% Data schema from variance function
numeric(V) :- transformation(V, log). 
binary(V) :- transformation(V, binomial). 
categorical(V) :- transformation(V, multinomial).

% TODO: Data collection procedure
% mixed effects

% Silence properties 
% Interaction terms are not required of all models
interaction(0,0) :- #false.