%%%%% DEFINE %%%%%
% Variables 
% For every X, Y, If there is a model with X and Y, this implies that X explains Y. 
explains(X, Y) :- model(X, Y). 
model(X, Y) :-  transformation(X, T),
                transformation(Y, T), 
                distribution(Y, D). 
% Each variable has only one transformation
{ transformation(V, T) : variableTransform(T) } = 1 :- variable(V).
{ distribution(V, D) : variableDistrib(D) } = 1 :- variable(V).
variableTransform(linear;natural_log;square_root;log_log;probit;logit).
variableDistrib(gaussian; gamma; inverse_gaussian; poisson; quasi_poisson; negative_binomial; binomial; multinomial).

%%%%% GENERATE %%%%%

% TODO: Restrict such that if X explains Y, Y cannot explain X.


%variable(age).
explains(age, sat).
%model(age, sat).
variable(age). 
variable(sat).

