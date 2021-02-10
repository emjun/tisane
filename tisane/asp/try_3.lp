%:- property(X), not_property(X).

property(X) :- variable(X).
property1(X) :- variable(X).

normal(X) :- transformed(X).
%not_property(X) :- variable(X), not property(X).
model0(X, Y) :- variable(X), variable(Y), normal(X).
%model1(X, Y) :- variable(X), variable(Y), not_property(X).
model2(X, Y) :- variable(X), variable(Y).
model3(X, Y) :- variable(Y), property1(X), normal(X).

#show model0/2. 
%#show model1/2.
#show model2/2.
#show model3/2.

variable(intelligence).
variable(score).
transformed(score).
%normal(score). 
not_property(score). 
%not_property1(score).