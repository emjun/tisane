from z3 import *

Object = DeclareSort('Object')

# Declare List data type with variable length
List = Datatype('List')
List.declare('cons', ('car', Object), ('cdr', List)) # Define ctor
# List.declare('cons', Object, ('cdr', List)) # Define ctor
List.declare('nil') # Define ctor
List = List.create() # Create Datatype

Explains = Function('Explains', Object, List, BoolSort())
Models = Function('Models', Object, List, BoolSort())
IsPredicted = Function('IsPredicted', Object, BoolSort())
IsPredictor = Function('IsPredictor', Object, BoolSort()) # TODO 
ArePredictors = Function('ArePredictors', List, BoolSort()) # TODO

# Free variable
y = Const('y', Object)
xs = Const('xs', List)
x = Const('x', Object) # TODO: Want x to be in xss
# xs = Const('xs', SeqSort(Object)) 

# assert 3 is somewhere in this sequence
# s.add(Contains(oseq, Unit(IntVal(3))))

model_explanation = [
    ForAll([y, xs], Implies(Models(y, xs), Explains(y, xs))),
    ForAll([y, xs], Implies(Explains(y, xs), IsPredicted(y))),
    ForAll([y, xs], Implies(Explains(y, xs), ArePredictors(xs))), # TODO: Question of how to use IsPredictor for each IV? 
    # ForAll([x, xs], Implies(IsPredictor(x), ArePredictors(xs))), # TODO: Question of how to use IsPredictor for each IV? 
]

Cause = Function('Cause', Object, Object, BoolSort())
Correlate = Function('Correlate', Object, Object, BoolSort())
HasEdge = Function('HasEdge', Object, Object, BoolSort())

conceptual_graph = [
    # ForAll([x, y], Implies(Cause(x, y), HasEdge(x, y))),
    # ForAll([x, y], Implies(Correlate(x, y), HasEdge(x, y))),
    # ForAll([x, y], Implies(HasEdge(x, y), (Or(Cause(x, y), Correlate(x, y))))),
    # Implies(Cause(x,y), HasEdge(x, y)),
    # Implies(Correlate(x,y), HasEdge(x, y)),
    ForAll([x, y], Xor(Correlate(x, y), Cause(x, y))),
    # Xor(Cause(x, y), Correlate(x, y)),
]


axioms = model_explanation + conceptual_graph
s = Solver()
s.add(axioms)
print(s.check())


# objects to test with 
sat = Const('sat', Object)
intelligence = Const('intelligence', Object)
tutoring = Const('tutoring', Object)

# Create list of IVs
ivs = List.cons(tutoring, List.nil)
ivs = List.cons(intelligence, ivs) 
# Create sequence of IVs
# ivs = SeqSort(tutoring, intelligence)
s.add(Models(sat, ivs))

# Create edge
# s.add(HasEdge(tutoring, sat))
s.add(Cause(tutoring, sat))
s.add(Correlate(tutoring, sat))

print(s.assertions())
print(s.check()) 

# print(s.model())


# ts = Solver()
# ts.add(ForAll([x], Xor(Correlate(x, y), Cause(x, y))))
# ts.add(Cause(tutoring, sat))
# ts.add(Correlate(tutoring, sat))
# # ts.add(Xor(Cause(tutoring, sat), Correlate(tutoring, sat)))
# print(ts.check()) # correctly outputs UNSAT
# print(ts.model())

# For all objects that explain the same object, they are ivs? 


### Questions? 
# How to use Sequence Sort? -- how to add 