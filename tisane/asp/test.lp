%%%%% Test %%%%%
% Data types
% cannot be categorical and numeric 
:- numeric(V), categorical(V).
%ordinal(V) :- not binary(V). % cannot be binary and ordinal?? - allow for now until have example want to work through.

% Ensure every predicted/predictor has a data type!
:- predicted(V), not has_datatype(V).
:- predictor(V), not has_datatype(V).