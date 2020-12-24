% ====== Definitions ======

% Data types: ordinal, nominal, quantitative, temporal.
type(ordinal;nominal;quantitative;temporal).
% Basic types of the data.
primitive_type(string;number;boolean;datetime).

% Possible tasks
tasks(explain). % could add prediction here in future

% ====== Helpers ======
categorical(V) :- type(V, (nominal;ordinal)).
continuous(V) :- not categorical(V)
numeric(V) :- continuous(V) % could also add temporal?
quantitative(V) :- numeric(V)
