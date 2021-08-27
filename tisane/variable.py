import unittest
from tisane.data import Dataset, DataVector
from typing import Any, List
import typing  # for typing.Unit

"""
Abstract super class for all variables.
Distinguish between Unit and Measures (Nominal, Ordinal, Numeric).
TODO: Added Time variable, not sure if we should include it?
"""


class AbstractVariable:
    name: str
    data: DataVector
    relationships: List[typing.Union["Has", "Repeats", "Nests"]]

    def __init__(self, name: str, data: None):
        self.name = name
        self.data = data  # or replace with DataVector()?
        self.relationships = list()

    def add_data(self, data):
        self.data = data

    # @param effect the variable causes
    def causes(self, effect: "AbstractVariable"):
        # Update both variables
        cause_relat = Causes(cause=self, effect=effect)
        self.relationships.append(cause_relat)
        effect.relationships.append(cause_relat)

    # @param variable associated with self
    def associates_with(self, variable: "AbstractVariable"):
        # Update both variables
        assoc_relat = Associates(lhs=self, rhs=variable)
        self.relationships.append(assoc_relat)
        variable.relationships.append(assoc_relat)

    # @param moderator contains variables that moderates the effect of self on @param on variable
    def moderates(
        self,
        moderator: typing.Union["AbstractVariable", List["AbstractVariable"]],
        on: "AbstractVariable",
    ):
        # Update both variables
        m_vars = list()
        m_vars.append(self)
        if isinstance(moderator, AbstractVariable):
            m_vars.append(moderator)  # Add moderator to vars list
        else:
            assert isinstance(moderator, List)
            for m in moderator:
                assert isinstance(m, AbstractVariable)
            m_vars += moderator  # Add moderator to vars list

        moderate_relat = Moderates(moderator=m_vars, on=on)
        self.relationships.append(moderate_relat)

        # Add relationship to moderators
        for v in m_vars:
            if self != v:  # Already added to self
                v.relationships.append(moderate_relat)

        # Add relationship to @param on
        on.relationships.append(moderate_relat)


"""
Class for SetUp (experiment's environment) settings
"""


class SetUp(AbstractVariable):
    variable: "Measure"

    def __init__(
        self,
        name: str,
        order: List = None,
        cardinality: int = None,
        data=None,
        **kwargs,
    ):
        super(SetUp, self).__init__(name, data)

        # If there is an order of values provided
        if order is not None:
            if cardinality is not None:
                self.variable = Ordinal(
                    name, order=order, cardinality=cardinality, data=data
                )
            else:
                self.variable = Ordinal(name, order=order, data=data)
        else:
            if cardinality is not None:
                self.variable = Nominal(name, data=data, cardinality=cardinality)
            else:
                self.variable = Numeric(name, data)

    def get_cardinality(self):
        return self.variable.get_cardinality()


"""
Class for Units
"""


class Unit(AbstractVariable):
    def __init__(self, name: str, data=None, cardinality: int = None, **kwargs):
        super(Unit, self).__init__(name, data)
        self.cardinality = cardinality

    def nominal(
        self,
        name: str,
        data=None,
        number_of_instances: typing.Union[int, AbstractVariable, "AtMost"] = 1,
        **kwargs,
    ):
        # Create new measure
        measure = Nominal(name, data=data, **kwargs)
        # Add relationship to self and to measure
        self._has(measure=measure, number_of_instances=number_of_instances)
        # Return handle to measure
        return measure

    def ordinal(
        self,
        name: str,
        order: list,
        cardinality: int = None,
        data=None,
        number_of_instances: typing.Union[int, AbstractVariable, "AtMost"] = 1,
    ):
        # Create new measure
        measure = Ordinal(name=name, order=order, cardinality=cardinality, data=data)
        # Add relationship to self and to measure
        self._has(measure=measure, number_of_instances=number_of_instances)
        # Return handle to measure
        return measure

    def numeric(
        self,
        name: str,
        data=None,
        number_of_instances: typing.Union[int, AbstractVariable, "AtMost"] = 1,
    ):
        # Create new measure
        measure = Numeric(name=name, data=data)
        # Add relationship to self and to measure
        self._has(measure=measure, number_of_instances=number_of_instances)
        # Return handle to measure
        return measure

    def _has(
        self,
        measure: AbstractVariable,
        number_of_instances: typing.Union[int, AbstractVariable, "AtMost"],
    ):
        # Figure out the number of times/repetitions this Unit (self) has of the measure

        repet = None
        according_to = None
        if isinstance(number_of_instances, int):
            repet = Exactly(number_of_instances)
        elif isinstance(number_of_instances, AbstractVariable):
            repet = Exactly(number_of_instances.get_cardinality())
            according_to = number_of_instances

            # TODO: Add implied relationship of associates with for measures that have number_of_instances as AbstractVariable
        elif isinstance(number_of_instances, AtMost):
            repet = number_of_instances

        # Bind measure and unit to each other
        has_relat = Has(
            variable=self, measure=measure, repetitions=repet, according_to=according_to
        )
        self.relationships.append(has_relat)
        measure.relationships.append(has_relat)

        # Add relationships between @number_of_instances (if AbstractVariable) variables and DV?

    # def repeats(self, measure: "Measure", according_to: "Measure"):
    #     repeats_relat = Repeats(unit=self, measure=measure, according_to=according_to)

    #     self.relationships.append(repeats_relat)
    #     measure.relationships.append(repeats_relat) # is this necessary?

    def nests_within(self, group: "Unit"):
        nest_relat = Nests(base=self, group=group)

        self.relationships.append(nest_relat)
        group.relationships.append(nest_relat)

    def get_cardinality(self):
        return self.cardinality


"""
Super class for Measures
"""


class Measure(AbstractVariable):
    def __init__(self, name: str, data: None, **kwargs):
        super(Measure, self).__init__(name, data)

    # Composition relationship between two measures
    def has(
        self,
        measure: AbstractVariable,
        number_of_instances: typing.Union[int, AbstractVariable, "AtMost"] = 1,
    ):
        repet = None
        according_to = None
        if isinstance(number_of_instances, int):
            repet = Exactly(number_of_instances)
        elif isinstance(number_of_instances, AbstractVariable):
            repet = Exactly(number_of_instances.get_cardinality())
            according_to = number_of_instances
        elif isinstance(number_of_instances, AtMost):
            repet = number_of_instances

        # Bind measure and unit to each other
        has_relat = Has(
            variable=self, measure=measure, repetitions=repet, according_to=according_to
        )
        self.relationships.append(has_relat)
        measure.relationships.append(has_relat)

    # @returns the unit this measure is an attribute of
    def get_unit(self) -> Unit:
        for r in self.relationships:
            if isinstance(r, Has):
                if r.measure is self and isinstance(r.variable, Unit):
                    return r.variable

        return None

    # @returns the unit relationship, None otherwise
    def get_unit_relationsihp(self) -> "Has":
        for r in self.relationships:
            if isinstance(r, Has):
                if r.measure is self and isinstance(r.variable, Unit):
                    return r

        return None


"""
Class for Nominal measures
"""


class Nominal(Measure):
    cardinality: int
    categories = list

    def __init__(self, name: str, data=None, **kwargs):
        super(Nominal, self).__init__(name=name, data=data)
        self.data = data
        self.categories = None

        # for time being until incorporate DataVector class and methods
        if "categories" in kwargs.keys():
            self.categories = kwargs["categories"]
            num_categories = len(kwargs["categories"])
            assert int(kwargs["cardinality"]) == len(kwargs["categories"])
            if num_categories == 1:
                # self.assert_property(prop="cardinality", val="unary")
                pass
            elif num_categories == 2:
                # self.assert_property(prop="cardinality", val="binary")
                pass
            else:
                assert num_categories > 2
                # self.assert_property(prop="cardinality", val="multi")
            self.cardinality = num_categories

        else:
            if "cardinality" in kwargs.keys():
                self.cardinality = kwargs["cardinality"]
            else:
                if "categories" in kwargs.keys():
                    num_categories = len(kwargs["categories"])
                    self.cardinality = num_categories

        # has data
        if self.data is not None:
            num_categories = len(self.data.get_categories())
            if num_categories == 1:
                pass
                # self.assert_property(prop="cardinality", val="unary")
            elif num_categories == 2:
                pass
                # self.assert_property(prop="cardinality", val="binary")
            else:
                assert num_categories > 2
                # self.assert_property(prop="cardinality", val="multi")

        # # Associate self with unit by add variable relationship to self and to unit
        # unit._has(measure=self, exactly=exactly, up_to=up_to)

    def __str__(self):
        return f"NominalVariable: data:{self.data}"

    # @returns cardinality
    def get_cardinality(self):
        return self.cardinality


"""
Class for Ordinal measures
"""


class Ordinal(Measure):
    cardinality: int
    ordered_cat: list

    def __init__(self, name: str, order: list, cardinality: int = None, data=None):
        super(Ordinal, self).__init__(name=name, data=data)
        self.ordered_cat = order
        self.data = data
        self.properties = dict()
        # self.assert_property(prop="dtype", val="ordinal")

        # Order must be provided
        self.ordered_cat = order
        num_categories = len(self.ordered_cat)
        self.cardinality = num_categories
        if num_categories == 1:
            pass
            # self.assert_property(prop="cardinality", val="unary")
        elif num_categories == 2:
            pass
            # self.assert_property(prop="cardinality", val="binary")
        else:
            assert num_categories > 2
            # self.assert_property(prop="cardinality", val="multi")

        # Verify that order and cardinality match
        if cardinality is not None:
            assert self.cardinality == len(order)
        self.cardinality = len(order)

        # # Associate self with unit by add variable relationship to self and to unit
        # unit._has(measure=self, exactly=exactly, up_to=up_to)

    def __str__(self):
        return f"OrdinalVariable: ordered_cat: {self.ordered_cat}, data:{self.data}"

    def get_cardinality(self):
        return self.cardinality

    # Estimate the cardinality of a variable by
    def calculate_cardinality_from_data(self, data: Dataset):
        data = data.dataset[self.name]  # Get data corresponding to this variable
        unique_values = data.unique()

        return len(unique_values)


"""
Class for Numeric measures
"""


class Numeric(Measure):
    def __init__(self, name: str, data=None):
        super(Numeric, self).__init__(name=name, data=data)
        self.data = data
        self.properties = dict()
        # self.assert_property(prop="dtype", val="numeric")

        # # Associate self with unit by add variable relationship to self and to unit
        # unit._has(measure=self, exactly=exactly, up_to=up_to)

    def __str__(self):
        return f"NumericVariable: data:{self.data}"

    def get_cardinality(self):
        if self.data is not None:
            # Return number of unique values
            raise NotImplementedError
        else:
            return 1


##### Conceptual relationships
"""
Class for Cause relationships
"""


class Causes(object):
    cause: AbstractVariable
    effect: AbstractVariable

    def __init__(self, cause: AbstractVariable, effect: AbstractVariable):
        self.cause = cause
        self.effect = effect


"""
Class for Associate relationships
"""


class Associates(object):
    lhs: AbstractVariable
    rhs: AbstractVariable

    def __init__(self, lhs: AbstractVariable, rhs: AbstractVariable):
        self.lhs = lhs
        self.rhs = rhs


"""
Class for Moderate relationships (for Interactions)
"""


class Moderates(object):
    moderator: List[AbstractVariable]
    on: AbstractVariable

    def __init__(self, moderator: List[AbstractVariable], on: AbstractVariable):
        self.moderator = moderator
        self.on = on


##### Data measurement relationships
"""
Class for Has relationships
"""


class Has:
    variable: AbstractVariable
    measure: AbstractVariable
    repetitions: "NumberValue"
    according_to: AbstractVariable

    def __init__(
        self,
        variable: AbstractVariable,
        measure: AbstractVariable,
        repetitions: "NumberValue",
        according_to: AbstractVariable = None,
        **kwargs,
    ):
        self.variable = variable
        self.measure = measure
        self.repetitions = repetitions
        self.according_to = according_to


"""
Class for expressing repeated measures
"""


class Repeats:
    unit: Unit
    measure: Measure
    according_to: Measure

    def __init__(self, unit: Unit, measure: Measure, according_to: Measure):
        self.unit = unit
        self.measure = measure
        self.according_to = according_to


"""
Class for expressing nesting relationship between units
"""


class Nests:
    base: Unit
    group: Unit

    def __init__(self, base: Unit, group: Unit):
        self.base = base
        self.group = group


"""
Wrapper class for expressing values for the number of repetitions of a condition, etc.
"""


class NumberValue:
    value: int

    def __init__(self, value: int):
        self.value = value

    def is_greater_than_one(self):
        return self.value > 1

    def is_equal_to_one(self):
        return self.value == 1

    def get_value(self):
        return self.value


"""
Class for expressing exact values
"""


class Exactly(NumberValue):
    def __init__(self, value: int):
        super(Exactly, self).__init__(value)


"""
Class for expressing an upper bound of values
"""


class AtMost(NumberValue):
    def __init__(self, value: typing.Union[int, AbstractVariable]):
        if isinstance(value, int):
            super(AtMost, self).__init__(value)
        elif isinstance(value, AbstractVariable):
            super(AtMost, self).__init__(value.get_cardinality())
