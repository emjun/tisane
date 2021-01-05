normal_residuals(X0, X1, Y) :- variable(X0), variable(X1), variable(Y), numeric_or_categorical(X0), numeric_or_categorical(X1), numeric_or_categorical(Y).
numeric(V) :- variable(V), not categorical(V).
two_categories(V) :- variable(V), categorical(V).
transformed(V) :- variable(V).
multicollinear(X0, X1, Y) :- variable(X0), variable(X1), variable(Y), not tolerate_correlation(X0, X1).

linear_regression(X0, X1, Y) :- variable(X0), variable(X1), variable(Y), normal_residuals(X0, X1, Y), homoscedastic_residuals(X0, X1, Y), not multicollinear(X0, X1, Y), numeric(Y), numeric_or_categorical(X0), numeric_or_categorical(X1), transformed(X0), transformed(X1), transformed(Y).


logistic_regression(X0, X1, Y) :- variable(X0), variable(X1), variable(Y), normal_residuals(X0, X1, Y), homoscedastic_residuals(X0, X1, Y), not multicollinear(X0, X1, Y), two_categories(Y), numeric_or_categorical(X0), numeric_or_categorical(X1), transformed(X0), transformed(X1), transformed(Y).

%*
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
*%

%* FOR TESTING AND DEVELOPMENT
*%
variable(intelligence).
variable(tutoring).
variable(score).
normal_residuals(intelligence, tutoring, score).
homoscedastic_residuals(intelligence, tutoring, score).
tolerate_correlation(intelligence, tutoring).
numeric(score).
numeric(intelligence).

numeric_or_categorical(intelligence).
numeric_or_categorical(tutoring).
numeric_or_categorical(score).

categorical(tutoring).
%categorical(score).
%two_categories(score).
%numeric_or_categorical(intelligence).
transformed(intelligence).
transformed(score).


%%%%%% CONTROL OUTPUT %%%%%%
#show 0. 

#show linear_regression/3.
#show logistic_regression/3.
