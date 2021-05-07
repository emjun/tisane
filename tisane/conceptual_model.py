from tisane.graph import Graph
from tisane.variable import Cause, Associate

from typing import List


class ConceptualModel(object):
    graph: Graph

    def __init__(
        self,
        causal_relationships: List[Cause] = None,
        associative_relationships: List[Associate] = None,
    ):
        self.graph = Graph()

        if causal_relationships:
            self._add_causal_relationships(causal_relationships)

        if associative_relationships:
            self._add_associative_relationships(associative_relationships)

    def _add_causal_relationships(self, relationships: List[Cause]):
        for r in relationships:
            cause = r.cause
            effect = r.effect

            self.graph.cause(cause=cause, effect=effect)

    def _add_associative_relationships(self, relationships: List[Associate]):
        for r in relationships:
            lhs = r.lhs
            rhs = r.rhs

            self.graph.associate(lhs=lhs, rhs=rhs)
