from z3 import *


def method_to_generate():

    # Declare data type
    Object = DeclareSort("Object")

    names = ["intelligence", "tutoring", "sat_score"]
    ivs_seq = None
    for n in names:
        obj = Const(n, Object)  # create a Z3 object
        # facts.append(obj) # add each object
        # Have we created a sequence of IVs yet?
        # If not, create one
        if not ivs_seq:
            # set first Unit of sequence
            ivs_seq = Unit(obj)
        # We already created a sequence of IVs
        else:
            # concatenate
            ivs_seq = Concat(Unit(obj), ivs_seq)


def create_unit():
    Object = DeclareSort("Object")

    facts = list()

    names = ["intelligence", "tutoring", "sat_score"]
    intelligence_0 = Const("intelligence 0", Object)
    ivs_seq = Unit(intelligence_0)
    # ivs_seq = None

    for i in range(2):
        intelligence = Const("intelligence", Object)
        facts.append(intelligence)

        if ivs_seq is None:
            # ivs_seq.append(Unit(intelligence))
            pass
    #     else:
    #         # ivs_seq = Unit(intelligence)
    #         pass


# This causes an error
def read_from_string():
    facts = ["Object = DeclareSort('Object') Const(intelligence, Object)"]
    s = Solver()
    s.from_string(facts)


# method_to_generate()
# read_from_string()
create_unit()
