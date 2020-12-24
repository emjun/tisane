%%%%%% GENERATE %%%%%%




%%%%%%% DEFINE %%%%%%

% Statistical models
linear_regression(X, Y) :- normal_residuals(X, Y), homoscedastic_residuals(X, Y), numeric(Y).
logistic_regression(X, Y) :- normal_residuals(X, Y), homoscedastic_residuals(X, Y), binary(Y).

% Properties
normal_residuals(X, Y) :- set_of_variables(X), variable(Y).
% normal_residuals(X, Y, @normal_residuals(X, Y)) :- set_of_x_variables(X), variable(Y). 
homoscedastic_residuals(X, Y) :- set_of_variables(X), numeric(Y).

% Data types
primitive_type(int; float; string).
numeric(V) :- variable(V). %, primitive_type(int; float).
categorical(V) :- variable(V). %, primitive_type(string). 
binary(V) :- variable(V), categorical(V). %, primitive_type(string).

set_of_variables(X) :- numeric(X), X < 5.
% set_of_variables(X) :- is_list_of_one_or_more_vars(X, @is_list(X)). 


numeric_transform(V) :- variable(V), numeric(V). 
categorical_transform(V) :- variable(V), categorical(V).

%%%%%%% TEST %%%%%%
variable(3).
variable(10).


%%%%%% CONTROL OUTPUT %%%%%%
#show 0.
%#show linear_regression/2.
%#show logistic_regression.
% #show numeric_transform/1. 
% #show categorical_transform/1. 
% #show set_of_variables/1.
% #show numeric/1.

%#show.