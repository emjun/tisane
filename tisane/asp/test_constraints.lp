normal_residuals(X, Y) :- variable(X), variable(Y).
%, numeric_or_categorical(X), numeric_or_categorical(Y).
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
                            %numeric_or_categorical(X), 
                            transformed(X), 
                            transformed(Y).


logistic_regression(X, Y) :-    variable(X),
                                variable(Y),
                                normal_residuals(X, Y), 
                                homoscedastic_residuals(X, Y), 
                                not multicollinear(X, Y), 
                                two_categories(Y), 
                                %numeric_or_categorical(X), 
                                transformed(X), 
                                transformed(Y).

%%%%%% CONTROL OUTPUT %%%%%%
#show 0. 

#show linear_regression/2.
#show logistic_regression/2.