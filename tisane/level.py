from tisane.variable import (
    AbstractVariable,
    Nominal,
    Ordinal,
    Numeric,
    Treatment,
    Nest,
    RepeatedMeasure,
)


from typing import List


class Level(object):
    _id: str
    _measures: List[AbstractVariable]

    def __init__(self, identifier: str, measures: List[AbstractVariable]):
        self._id = identifier
        self._measures = measures

    # Nest this Level under another Level
    def nest_under(self, other: "Level"):
        return LevelSet(levels=[self, other])


class LevelSet(object):
    _level_set = List[Level]

    def __init__(self, levels=List[Level]):
        self._level_set = levels

    def get_levels(self):
        return self._level_set

    # Nest this LevelSet under another Level
    # Useful for chaining nest_under statements
    def nest_under(self, level: Level):
        self._level_set.append(level)

        return self
