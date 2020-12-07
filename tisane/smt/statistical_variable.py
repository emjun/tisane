from tisane.concept import Concept

import z3

class StatVar(object):
    name: str

    def __init__(self, con: Concept):
        self.name = con.name
        self.__z3__ = z3.Bool(self.name)