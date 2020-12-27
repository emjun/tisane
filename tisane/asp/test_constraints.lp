normal_residuals(X, Y) :- variable(X), variable(Y), numeric_or_categorical(X), numeric_or_categorical(Y).
numeric(V) :- variable(V), not categorical(V).
two_categories(V) :- variable(V), categorical(V).
transformed(V) :- variable(V).
multicollinear(X, Y) :- variable(X), variable(Y), not tolerate_correlation(X).

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

%* FOR TESTING AND DEVELOPMENT
variable(intelligence). 
variable(tutoring).
variable(score).
normal_residuals(intelligence, tutoring, score).
homoscedastic_residuals(intelligence, tutoring, score).
tolerate_correlation(intelligence, tutoring).
%numeric(score).
numeric(intelligence).

numeric_or_categorical(intelligence). 
numeric_or_categorical(tutoring). 
numeric_or_categorical(score). 

categorical(tutoring).
categorical(score).
two_categories(score).
%numeric_or_categorical(intelligence).
transformed(intelligence).
transformed(score).
*%

%%%%%% CONTROL OUTPUT %%%%%%
#show 0. 

#show linear_regression/2.
#show logistic_regression/2.