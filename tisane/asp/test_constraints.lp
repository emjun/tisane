
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