type(ordinal;nominal;numeric).
%{is_numeric(C) } = 1:- concept(C).
{ type(V,T): type(T) } = 1 :- concept(V)


concept(intelligence).
concept(tutoring).
concept(test_score). 

causes(intelligence, test_score). 
causes(tutoring, test_score). 
correlates(intelligence, tutoring). 

%regression :- normal_residuals(X, Y), numeric(Y), homoscedastic_residuals(X, Y)

%normal_residuals(X, Y) :-  True
%numeric(Y) :- type(numeric).


