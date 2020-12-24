%%%%%% GENERATE %%%%%%

%%%%%%% DEFINE %%%%%%

% Statistical models
linear_regression(X, Y) :- normal_residuals(X, Y), homoscedastic_residuals(X, Y), numeric(Y), numeric_or_categorical_X(X).
logistic_regression(X, Y) :- normal_residuals(X, Y), homoscedastic_residuals(X, Y), binary(Y).
generalized_linear_model(X, Y) :-

% What if instead of prenamed models, we had a build your own model?
% (That is essentially what would occur through interaction.)
Each linear model needs:    Y, 
                            linear combination of Xs, 
                            any transformations to variables, 
                            variable types for all vars, 
                            cardinality of categorical vars, % this helps with logistic vs. multinominal regression
                            (shape of) relationship between variables (family, etc.???),
                            residuals distribution,
                            residuals homoscedasticity (variance),
                            correlation between Xs (multicollinearity),
                            causal or data collection relationship between Xs (e.g., for multilevel modeling)


% TODO: Type check transformations make sense
transform(V, log;normalize) :- variable(V),  numeric(V)

log_transform(V) :- variable(V), numeric(V)
center(V) :- variable(V), numeric(V) 
transform(X) :- variable(X) % types of transformations???
% i don't think we care about this (could have multiple and that's fine) - variable can have only one transformation
% { transform(V,T) }  = 1 :- variable(V) 








% Properties
normal_residuals(X, Y) :- set_of_variables(X), variable(Y).
% normal_residuals(X, Y, @normal_residuals(X, Y)) :- set_of_x_variables(X), variable(Y). 
homoscedastic_residuals(X, Y) :- set_of_variables(X), numeric(Y).

% Data types
primitive_type(int; float; string).
numeric(V) :- variable(V), primitive_type(int; float).
categorical(V) :- variable(V), primitive_type(string). 
binary(V) :- variable(V), categorical(V), primitive_type(string).

set_of_variables(X) :- numeric(X), X < 5.
% set_of_variables(X) :- is_list_of_one_or_more_vars(X, @is_list(X)). 


%%%%%%% TEST %%%%%%
variable(13).


#show linear_regression/2.
#show logistic_regression/2.


%%%%%% CONTROL OUTPUT %%%%%%

I can get as output all the possible "versions" of statistical models (including effects generation)?

In order to have dynamic arity and dynamically write rules, need to generate on the fly...?
list_of_ivs()