%%%%% GENERATE %%%%%
% Variables 

% (Scale) Transformations (AKA link functions).
transformed(V) :- linear(V); natural_log(V); square_root(V); log_log(V); probit(V); logit(V).
linear(V) :- variable(V), numeric(V).
natural_log(V) :- variable(V), numeric(V), not linear(V). 
square_root(V) :- variable(V), numeric(V), not linear(V), not natural_log(V). 
log_log(V) :- variable(V), binary(V); ordinal(V).
probit(V) :- variable(V), binary(V); ordinal(V), not log_log(V). 
logit(V) :- variable(V), categorical(V), not log_log(V), not probit(V). 
categorical :- ordinal(V); nominal(V), not log_log(V), not probit(V).

categorical(V) :- variable(V), not numeric(V). 
nominal(V) :- variable(V), categorical(V).
binary(V) :- variable(V), categorical(V), not nominal(V).
ordinal(V) :- variable(V), categorical(V), not nominal(V). 

%numeric(V) :- variable(V).
%nonnegative(V) :- variable(V), numeric(V). 
count(V) :- variable(V), numeric(V). 
numeric(V) :- variable(V), 1 {nonnegative(V); count(V)} 1.



% (Distribution) Variance function: Distribution of Y conditioned upon X 
distribution(V) :- gaussian(V); gamma(V); inverse_gaussian(V); poisson(V); quasi_poisson(V); negative_binomial(V); binomial(V); multinomial(V).
gaussian(V) :- numeric(V), not count(V).  % linear(V) because this means link function is identity. 
gamma(V) :- nonnegative(V), not gaussian(V). 
inverse_gaussian(V) :- numeric(V), nonnegative(V), not gaussian(V), not gamma(V). 
poisson(V) :- numeric(V). 
quasi_poisson(V) :- count(V), not poisson(V). % Look into
negative_binomial(V) :- count(V), not poisson(V), not quasi_poisson(V). % Look into
binomial(V) :- binary(V).
multinomial(V) :- categorical(V). 
:- binomial(V); multinomial(V).


%log(V) :- variable(V), not linear(V). % may want to make linear defined as anything but

%* Link functions 
link_function(X, Y) :-  identity(X, Y);  % may want to make normal_link defined as anything but
                        logit(X, Y).
*%

%*
% Variance functions
variance_function(X, Y) :- identity(X, Y);
                            other_var(X, Y).
*% 

%* Estimators
estimator(X, Y) :- ols(X, Y); mle(X, Y). 
mle(X, Y) :-    variable(X),
                variable(Y), 
                not ols(X, Y).
*%
                
%%%%% DEFINE %%%%%
% Like before, would have to expand Xs to match arity of effect set considering

base_glm_model(X, Y) :- explains(X, Y),
                        transformed(X), 
                        transformed(Y),
                        distribution(Y). 

% explains(X, Y) :- transformed(X), transformed(Y), distribution(Y).
% Helpful to have recommendations about types of data (e.g., count data should use Poisson) - count data != numeric data although may appear numeric

%%%%% TEST (Eliminate unwanted answer sets) %%%%%
% Cannot swap IVs and DV
base_glm_model(X, Y) :- explains(X, Y).
%variable(X) :- predictor(X).
%variable(Y) :- predicted(Y).
predictor(X) :- explains(X, Y). 
predicted(Y) :- explains(X, Y).
%explains(X, Y) :-   predictor(X), 
%                    predicted(Y).
%:- base_glm_model(X, Y).


%%%%% SHOW %%%%%
% Show: could be specialized based on type of query end-user wants (research question -> model, power analysis, hypothesis test, etc.)
#show 0.
%#show link_function/2.
%#show base_glm_model/2.



explains(age, sat).
numeric(age). 
numeric(sat).
%gaussian(sat).
%nonnegative(age).
%nonnegative(sat).
