 %*

Base: We have these variables 
Step: The variables have types and properties
Check: base model query ? 

*%

#const istop  = "SAT".
#const imin   = 1.
%#const imax   = 11.

#program base.

variable(X). 
variable(Y). 
explains(X, Y) :- variable(X), variable(Y)

#program step(k).

{ c(k) }.
q(k) :- c(k).
% assign var types

% assign properties

% find base model

#program check(k).

 :- explains(X, Y); explains(Y, X), query(k).

#show 0.

 %*

Base: We have these variables 
Step: The variables have types and properties
Check: base model query ? 

 *%