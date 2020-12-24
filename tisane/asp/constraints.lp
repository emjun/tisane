%*
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
*%

%%%%%% GENERATE %%%%%%
normal_residuals(X, Y) :- variable(X), variable(Y), numeric_or_categorical(X), numeric_or_categorical(Y).
numeric(V) :- variable(V), not categorical(V).
two_categories(V) :- variable(V), categorical(V).
transformed(V) :- variable(V).
multicollinear(X, Y) :- variable(X), variable(Y), not tolerate_correlation(X).

%%%%%%% DEFINE %%%%%%

linear_regression(X, Y) :-  variable(X),
                            variable(Y), 
                            normal_residuals(X, Y), 
                            homoscedastic_residuals(X, Y), 
                            not multicollinear(X, Y), 
                            numeric(Y), 
                            numeric_or_categorical(X), 
                            transformed(X), 
                            transformed(Y).


logistic_regression(X, Y) :-    variable(X),
                                variable(Y),
                                normal_residuals(X, Y), 
                                homoscedastic_residuals(X, Y), 
                                not multicollinear(X, Y), 
                                two_categories(Y), 
                                numeric_or_categorical(X), 
                                transformed(X), 
                                transformed(Y).
%*
multinomial_regression(X, Y) :- variable(X),
                                variable(Y),
                                normal_residuals(X, Y), 
                                homoscedastic_residuals(X, Y), 
                                three_or_more_categories(Y), 
                                numeric_or_categorical(X), 
                                transformed(X), 
                                transformed(Y).

generalized_linear_model(X, Y) :-   variable(X),
                                    variable(Y),
                                    normal_residuals(X, Y), 
                                    homoscedastic_residuals(X, Y), 
                                    two_categories(Y), 
                                    numeric_or_categorical(X), 
                                    transformed(X), 
                                    transformed(Y).
*%

% Can have either linear or logistic regression only
:- linear_regression(X, Y), logistic_regression(X, Y).

%%%%%%% TEST %%%%%%
% #const x = "Intelligence".
% #const y = "Score".

variable(intelligence). % unsafe !!!
variable(score). 
normal_residuals(intelligence, score). 
homoscedastic_residuals(intelligence, score). 
tolerate_correlation(intelligence).
%numeric(score).
categorical(score).
two_categories(score). 
numeric_or_categorical(intelligence). 
transformed(intelligence). 
transformed(score). 


%%%%%% CONTROL OUTPUT %%%%%%
#show 0. 

#show linear_regression/2.
#show logistic_regression/2.