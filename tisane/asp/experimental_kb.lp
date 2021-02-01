%%%%% GENERATE %%%%%
% Applies to any variable
transformed(V) :- linear(V); log(V). 
log(V) :- variable(V), not linear(V). % may want to make linear defined as anything but
estimator(X, Y) :- ols(X, Y); mle(X, Y). 
mle(X, Y) :-    variable(X),
                variable(Y), 
                not ols(X, Y).

% Link functions 
link_function(X, Y) :-  normal_link(X, Y);  % may want to make normal_link defined as anything but
                        other_link(X, Y).
%other_link(X, Y) :- variable(X), variable(Y), not normal_link(X, Y). 

% Variance 
variance_function(X, Y) :- identity(X, Y);
                            other_var(X, Y). 

%other_var(X, Y) :- variable(X), variable(Y), not identity(X, Y). % may want to change variable predicates

%* Experimental design 
between_subjects(V) :-  categorical(V), 
                        ...only occurs once... - would have to check this elsewhere?
*%

% Default to OLS when... -- MAY NOT NEED THIS!
ols(X, Y) :- linear(X), linear(Y). 

%%%%% DEFINE %%%%%
% Like before, would have to expand Xs to match arity of effect set considering
base_glm_model(X, Y) :- variable(X), 
                        variable(Y),
                        explains(X, Y),
                        transformed(X), 
                        transformed(Y),
                        link_function(X, Y), 
                        variance_function(X, Y), 
                        estimator(X, Y). 

% Helpful to have recommendations about types of data (e.g., count data should use Poisson) - count data != numeric data although may appear numeric

%%%%% TEST %%%%%
% Trying to suppress assignment of same variables to X and Y. 
:- explains(X, Y); explains(Y, X).


%%%%% SHOW %%%%%
% Show: could be specialized based on type of query end-user wants (research question -> model, power analysis, hypothesis test, etc.)
#show 0.
#show link_function/2.
#show base_glm_model/2.



variable(age). 
variable(sat).
linear(age). 
linear(sat).
identity(age, sat). 
normal_link(age, sat). 
explains(age, sat).